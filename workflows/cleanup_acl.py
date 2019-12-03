#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/acl_data.yaml file.
This workflow performs the following steps:
1. Detach ACL from VLAN
   Ex:
    vlan 200
        no apply access-list ip acl_ipv4 in

2. Delete IPv4 ACL
    a. Delete entries in ACL
    b. Delete the ACL
   Ex:
    no access-list ip acl_ipv4

3. Delete IPv6 ACL
    a. Delete entries in ACL
    b. Delete the ACL
   Ex:
    no access-list ipv6 acl_ipv6

4. Delete MAC ACL
    a. Delete entries in ACL
    b. Delete the ACL
   Ex:
    no access-list mac acl_mac

5. Reset interfaces
   Ex:
    interface 1/1/10
        shutdown
        routing
    interface 1/1/11
        shutdown
        routing
        no apply access-list ip acl_ipv4 in
    interface 1/1/12
        shutdown
        routing
        no apply access-list ipv6 acl_ipv6 in
    interface 1/1/21
        shutdown
        no lag 13
    interface 1/1/22
        shutdown
        no lag 13
    no interface lag 13


Preconditions:
Must have run configure_acl workflow or have an equivalent configuration on the device
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
from src import session, acl, vlan, interface, lag, system

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
        session_dict['platform_name'] = system.get_system_info(**session_dict).get('platform_name')

        # Clear Egress ACLs from L3 interface
        acl.clear_interface_acl(data['L3egressinterface'], acl_type="aclv4_out", **session_dict)

        # Clear Ingress ACLs from L2 interface
        acl.clear_interface_acl(data['ipv4L2ingressinterface'], acl_type="aclv4_in", **session_dict)
        acl.clear_interface_acl(data['ipv6L2ingressinterface'], acl_type="aclv6_in", **session_dict)

        # Clear Ingress ACLs from LAG interface
        acl.clear_interface_acl(data['LAGname'], acl_type="aclv4_in", **session_dict)

        # Detach ACL from VLAN
        vlan.detach_vlan_acl(data['aclVLANid'], "ipv4", **session_dict)

        # Remove and initialize L2 and L3 interfaces
        interface.initialize_interface(data['L3egressinterface'], **session_dict)
        interface.initialize_interface(data['ipv4L2ingressinterface'], **session_dict)
        interface.initialize_interface(data['ipv6L2ingressinterface'], **session_dict)
        interface.initialize_interface(data['interfaceVLAN'], **session_dict)

        # Remove LAG and initialize associated L2 interfaces
        lag.delete_lag_interface(data['LAGname'], data['LAGinterfaces'], **session_dict)
        for LAGinterface in data['LAGinterfaces']:
            interface.initialize_interface(LAGinterface, **session_dict)

        # Delete VLAN
        vlan.delete_vlan(data['aclVLANid'], **session_dict)

        # For each ACL that was configured
        for pair_dict in [{"name": data['ipv4aclname'], "type": "ipv4"},
                          {"name": data['ipv6aclname'], "type": "ipv6"},
                          {"name": data['macaclname'], "type": "mac"}]:

            # Delete ACL entries
            for i in range(10, 60, 10):
                acl.delete_acl_entry(pair_dict["name"], pair_dict["type"], i, **session_dict)

            # Delete the ACL
            acl.delete_acl(pair_dict["name"], pair_dict["type"], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict)

if __name__ == '__main__':
    main()
