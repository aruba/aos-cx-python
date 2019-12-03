#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/acl_data.yaml file.
This workflow performs the following steps:
1. Create an IPv4 ACL
   Ex:
    access-list ip acl_ipv4

2. Add entries to IPv4 ACL
    a. Add entries to the ACL
    b. Version-up the ACL
   Ex:
    access-list ip acl_ipv4
        10 deny tcp 10.1.2.1/255.255.255.0 any count
        20 deny udp any 10.33.12.3 eq 80 count
        30 permit any 10.2.4.2 10.33.25.34/255.255.255.0 count
        40 deny any any any count
        50 permit any any any count

3. Create an IPv6 ACL
   Ex:
    access-list ipv6 acl_ipv6

4. Add entries to IPv6 ACL
    a. Add entries to the ACL
    b. Version-up the ACL
   Ex:
    access-list ipv6 acl_ipv6
        10 deny tcp any 22f4:23::1/64 count
        20 permit tcp 3000:323:1221::88/64 any count
        30 permit ospf any 3999:929:fa98:00f0::4/120 count
        40 deny any any any count
        50 permit any any any count

5. Create a MAC ACL
   Ex:
    access-list mac acl_mac

6. Add entries to MAC ACL
    a. Add entries to the ACL
    b. Version-up the ACL
   Ex:
    access-list mac acl_mac
        10 permit ff33.244c.aabb any arp count
        20 permit 1f33.cc4c.aaff ff33.244c.aa11 ipv6 count
        30 permit 1f33.cc4c.aaff ff33.244c.aa11 lldp count
        40 permit 1f33.cc4c.aaff ff33.244c.aa11 appletalk count
        50 deny any any any count

7. Create VLAN, L2, L3, and LAG Interfaces
   Ex:
    vlan 200
        name vlan200
    interface lag 13
        no shutdown
        no routing
        vlan trunk native 1
        vlan trunk allowed all
        lacp mode passive
    interface 1/1/10
        no shutdown
        no routing
        vlan access 1
    interface 1/1/11
        no shutdown
        no routing
        vlan trunk native 1 tag
        vlan trunk allowed all
    interface 1/1/12
        no shutdown
        no routing
        vlan trunk native 1 tag
        vlan trunk allowed all
    interface 1/1/21
        no shutdown
        lag 13
    interface 1/1/22
        no shutdown
        lag 13
    interface 1/1/40
        no shutdown

8. Attach IPv4 ACL to VLAN
   Ex:
    vlan 200
        apply access-list ip acl_ipv4 in

9. Attach VLAN to interface
   Ex:
    interface 1/1/10
        vlan trunk allowed 200

10. Apply IPv4 ACL to L2 interface on ingress
   Ex:
    interface 1/1/11
        apply access-list ip acl_ipv4 in

11. Apply IPv6 ACL to L2 interface on ingress
   Ex:
    interface 1/1/11
        apply access-list ip acl_ipv4 in

12. Apply IPv4 ACL to L3 interface on egress
   Ex:
    interface 1/1/40
        apply access-list ip acl_ipv4 out

13. Apply IPv4 ACL to L2 LAG on ingress
   Ex:
    interface lag 13
        apply access-list ip acl_ipv4 in

Preconditions:
None
"""

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import os
import sys

dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(dirpath)
sys.path.append(os.path.join(dirpath, "src"))
sys.path.append(os.path.join(dirpath, "cx_utils"))

from cx_utils import yaml_ops
from src import session, acl, vlan, interface, lag


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    data = yaml_ops.read_yaml("acl_data.yaml")

    if not data['switchip']:
        data['switchip'] = input("Switch IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['switchip']
        os.environ['NO_PROXY'] = data['switchip']

    if not data['version']:
        data['version'] = "v10.04"

    base_url = "https://{0}/rest/{1}/".format(data['switchip'], data['version'])
    try:
        session_dict = dict(s=session.login(base_url, data['username'], data['password']), url=base_url)

        # Create empty IPv4 ACL
        acl.create_acl(data['ipv4aclname'], "ipv4", **session_dict)

        # Add entry 10 to IPv4 ACL
        acl.create_acl_entry(data['ipv4aclname'], "ipv4", 10, action="deny", count=data['hitcount'], ip_protocol=6,
                             src_ip="10.1.2.1/255.255.255.0", **session_dict)

        # Add entry 20 to IPv4 ACL
        acl.create_acl_entry(data['ipv4aclname'], "ipv4", 20, action="deny", count=data['hitcount'], ip_protocol=17,
                             dst_ip="10.33.12.3/255.255.255.255", dst_l4_port_min=80, dst_l4_port_max=80,
                             **session_dict)

        # Add entry 30 to IPv4 ACL
        acl.create_acl_entry(data['ipv4aclname'], "ipv4", 30, action="permit", count=data['hitcount'],
                             src_ip="10.2.4.2/255.255.255.255", dst_ip="10.33.25.34/255.255.255.0", **session_dict)

        # Add entry 40 to IPv4 ACL
        acl.create_acl_entry(data['ipv4aclname'], "ipv4", 40, action="deny", count=data['hitcount'], **session_dict)

        # Add entry 50 to IPv4 ACL
        acl.create_acl_entry(data['ipv4aclname'], "ipv4", 50, action="permit", count=data['hitcount'], **session_dict)

        # Version-up the IPv4 ACL to complete the change
        acl.update_acl(data['ipv4aclname'], "ipv4", **session_dict)

        # Create empty IPv6 ACL
        acl.create_acl(data['ipv6aclname'], "ipv6", **session_dict)

        # Add entry 10 to IPv6 ACL
        acl.create_acl_entry(data['ipv6aclname'], "ipv6", 10, action="deny", count=data['hitcount'], ip_protocol=6,
                             dst_ip="22f4:23::1/ffff:ffff:ffff:ffff::", **session_dict)

        # Add entry 20 to IPv6 ACL
        acl.create_acl_entry(data['ipv6aclname'], "ipv6", 20, action="permit", count=data['hitcount'], ip_protocol=6,
                             src_ip="3000:323:1221::88/ffff:ffff:ffff:ffff::", **session_dict)

        # Add entry 30 to IPv6 ACL
        acl.create_acl_entry(data['ipv6aclname'], "ipv6", 30, action="permit", count=data['hitcount'], ip_protocol=89,
                             dst_ip="3999:929:fa98:00f0::4/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ff00", **session_dict)

        # Add entry 40 to IPv6 ACL
        acl.create_acl_entry(data['ipv6aclname'], "ipv6", 40, action="deny", count=data['hitcount'], **session_dict)

        # Add entry 50 to IPv6 ACL
        acl.create_acl_entry(data['ipv6aclname'], "ipv6", 50, action="permit", count=data['hitcount'], **session_dict)

        # Version-up the IPv6 ACL to complete the change
        acl.update_acl(data['ipv6aclname'], "ipv6", **session_dict)

        # Create empty MAC ACL
        acl.create_acl(data['macaclname'], "mac", **session_dict)

        # Add entry 10 to MAC ACL
        acl.create_acl_entry(data['macaclname'], "mac", 10, action="permit", count=data['hitcount'], ethertype=2054,
                             src_mac="ff33.244c.aabb/ffff.ffff.ffff", **session_dict)

        # Add entry 20 to MAC ACL
        acl.create_acl_entry(data['macaclname'], "mac", 20, action="permit", count=data['hitcount'], ethertype=34525,
                             src_mac="1f33.cc4c.aaff/ffff.ffff.ffff", dst_mac="ff33.244c.aa11/ffff.ffff.ffff",
                             **session_dict)

        # Add entry 30 to MAC ACL
        acl.create_acl_entry(data['macaclname'], "mac", 30, action="permit", count=data['hitcount'], ethertype=35020,
                             src_mac="1f33.cc4c.aaff/ffff.ffff.ffff", dst_mac="ff33.244c.aa11/ffff.ffff.ffff",
                             **session_dict)

        # Add entry 40 to MAC ACL
        acl.create_acl_entry(data['macaclname'], "mac", 40, action="permit", count=data['hitcount'], ethertype=32923,
                             src_mac="1f33.cc4c.aaff/ffff.ffff.ffff", dst_mac="ff33.244c.aa11/ffff.ffff.ffff",
                             **session_dict)

        # Add entry 50 to MAC ACL
        acl.create_acl_entry(data['macaclname'], "mac", 50, action="deny", count=data['hitcount'], **session_dict)

        # Version-up the ACL to complete the change
        acl.update_acl(data['macaclname'], "mac", **session_dict)

        # Create VLAN and L2 System interfaces
        interface.add_l2_interface(data['interfaceVLAN'], **session_dict)
        interface.enable_disable_interface(data['interfaceVLAN'], "up", **session_dict)

        interface.add_l2_interface(data['ipv4L2ingressinterface'], **session_dict)
        interface.enable_disable_interface(data['ipv4L2ingressinterface'], "up", **session_dict)
        vlan.port_set_vlan_mode(data['ipv4L2ingressinterface'], "native-tagged", **session_dict)
        vlan.port_add_vlan_trunks(data['ipv4L2ingressinterface'], **session_dict)

        interface.add_l2_interface(data['ipv6L2ingressinterface'], **session_dict)
        interface.enable_disable_interface(data['ipv6L2ingressinterface'], "up", **session_dict)
        vlan.port_set_vlan_mode(data['ipv6L2ingressinterface'], "native-tagged", **session_dict)
        vlan.port_add_vlan_trunks(data['ipv6L2ingressinterface'], **session_dict)

        # Create LAG Interfaces
        for LAGinterface in data['LAGinterfaces']:
            interface.add_l2_interface(LAGinterface, **session_dict)
            interface.enable_disable_interface(LAGinterface, "up", **session_dict)

        # Create L3 interface
        interface.add_l3_ipv4_interface(data['L3egressinterface'], **session_dict)
        interface.enable_disable_interface(data['L3egressinterface'], "up", **session_dict)

        # Create LAG interfaces
        lag.create_l2_lag_interface(data['LAGname'], data['LAGinterfaces'], **session_dict)

        # Create VLAN
        vlan.create_vlan(data['aclVLANid'], "vlan%d" % data['aclVLANid'], **session_dict)

        # Attach the ACL to VLAN
        vlan.attach_vlan_acl(data['aclVLANid'], data['ipv4aclname'], "ipv4", **session_dict)

        # Attach VLAN to interface
        vlan.port_set_vlan_mode(data['interfaceVLAN'], "native-tagged", **session_dict)
        vlan.port_add_vlan_trunks(data['interfaceVLAN'], [data['aclVLANid']], **session_dict)

        # Apply IPv4 ACL to L2 interface on ingress
        acl.update_port_acl_in(data['ipv4L2ingressinterface'], data['ipv4aclname'], 'ipv4', **session_dict)

        # Apply IPv6 ACL to L2 interface on ingress
        acl.update_port_acl_in(data['ipv6L2ingressinterface'], data['ipv6aclname'], 'ipv6', **session_dict)

        # Apply IPv4 ACL to L3 interface on egress
        acl.update_port_acl_out(data['L3egressinterface'], data['ipv4aclname'], **session_dict)

        # Apply IPv4 ACL to L2 LAG on ingress
        acl.update_port_acl_in(data['LAGname'], data['ipv4aclname'], 'ipv4', **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict)

if __name__ == '__main__':
    main()
