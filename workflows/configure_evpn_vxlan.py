#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/evpn_vxlan_data.yaml file.
This workflow performs the following steps:
A. Configure Fabric Infrastructure (OSPF and BGP Setup on Spines and Leafs)
    1. Configure OSPF On Spines
        a. Create an OSPFv2 ID
        b. Create an OSPFv2 Area
   Ex:
    router ospf 1
        redistribute connected
        redistribute static
        area 0.0.0.0

    2. Configure Loopback Interface on Spines
        a. Give Loopback IP Address
        b. Set Loopback Interface to OSPF Area
   Ex:
    interface loopback 0
        ip address 10.2.0.101/32
        ip ospf 1 area 0.0.0.0

    3. Configure Downlinks on Spines to Leaf Switches
        a. Give each Interface an IP Address
        b. Set each Interface to OSPF Area
        c. Set Interface to OSPF Network point-to-point
        d. Enable the Interface
   Ex:
    interface 1/1/2
        no shutdown
        ip address 10.1.1.1/31
        ip ospf 1 area 0.0.0.0
        ip ospf network point-to-point
    interface 1/1/3
        no shutdown
        ip address 10.1.1.5/31
        ip ospf 1 area 0.0.0.0
        ip ospf network point-to-point

    4. Add IBGP EVPN peering on Spines towards all Leaf switches
        a. Create Router BGP
            i. Set BGP Router ID
            ii. Set BGP neighbor IP remote-as BGP port for each neighbor
            iii. Set BGP neighbor IP update-source as Loopback ID for each neighbor
        b. Set address-family to EVPN
            i. Set each EVPN neighbor to route-reflector-client
            ii. Set each EVPN neighbor to send-community
            iii. Set each EVPN neighbor to activate
   Ex:
    router bgp 65001
        bgp router-id 10.2.0.101
        neighbor 10.2.0.1 remote-as 65001
        neighbor 10.2.0.1 update-source loopback 0
        neighbor 10.2.0.2 remote-as 65001
        neighbor 10.2.0.2 update-source loopback 0
        address-family l2vpn evpn
            neighbor 10.2.0.1 activate
            neighbor 10.2.0.1 route-reflector-client
            neighbor 10.2.0.1 send-community
            neighbor 10.2.0.2 activate
            neighbor 10.2.0.2 route-reflector-client
            neighbor 10.2.0.2 send-community
        exit-address-family

    5. Configure OSPF on each Leaf
        a. Create an OSPF ID
        b. Create and OSPFv2 Area
   Ex:
    router ospf 1
        redistribute connected
        redistribute static
        area 0.0.0.0

    6. Configure Loopback Interface on each Leaf
        a. Give Loopback IP Address
        b. Set Loopback Interface to OSPF Area
   Ex:
    interface loopback 0
        ip address 10.2.0.1/32
        ip ospf 1 area 0.0.0.0

    7. Configure Uplinks on Leaf Switches to Spines
        a. Give each Interface an IP Address
        b. Set each Interface to OSPF Area
        c. Set Interface to OSPF Network point-to-point
        d. Enable the Interface
   Ex:
    interface 1/1/2
        no shutdown
        ip address 10.1.1.0/31
        ip ospf 1 area 0.0.0.0
        ip ospf network point-to-point

    8. Add IBGP EVPN peering on each leaf switches to Spines
        a. Create Router BGP
            i. Set BGP Router ID
            ii. Set BGP neighbor IP remote-as BGP port for each neighbor
            iii. Set BGP neighbor IP update-source as Loopback ID for each neighbor
        b. Set address-family to EVPN
            i. Set each EVPN neighbor to send-community
            ii. Set each EVPN neighbor to activate
   Ex:
    router bgp 65001
        bgp router-id 10.2.0.1
        neighbor 10.2.0.101 remote-as 65001
        neighbor 10.2.0.101 update-source loopback 0
        address-family l2vpn evpn
            neighbor 10.2.0.101 activate
            neighbor 10.2.0.101 send-community
        exit-address-family


B. Configure Tenant Infrastructure (VRFs and VXLAN)
    1. Configure Leaf Switches to Servers
        a. Create VLANs on Leaf switches
        b. Configure LAGs
        c. Attach server Interfaces to LAGs and allow VLANs
   Ex:
    vlan 1,11-12
    interface lag 10
        no shutdown
        no routing
        vlan trunk native 1
        vlan trunk allowed 11-12
        lacp mode active
    interface 1/1/52
        no shutdown
        lag 10

    2. Configure VXLAN on each Leaf
        a. Create VXLAN interface
        b. Set source IP
        c. Create VNIs for each VLAN
   Ex:
    interface vxlan 1
        source ip 10.2.0.1
        no shutdown
        vni 11
            vlan 11
        vni 12
            vlan 12

    3. Configure EVPN on each Leaf
        a. Set each VLAN to rd auto
        b. Set each VLAN to route-target export and import auto
   Ex:
    evpn
        vlan 11
            rd auto
            route-target export auto
            route-target import auto
        vlan 12
            rd auto
            route-target export auto
            route-target import auto

    4. Setup Border Leaf Switch
        a. Configure VRF to Core and external facing Interface to import routes from different VRFs
            i. Set rd 1:3
            ii. Set address-family ipv4 unicast route-targets to import and export
        b. Configure interface to Core network
            i. Set IP address and attach Core VRF
        c. Configure Router BGP
            i. Set VRF Core with neighbor IP remote-as port
            ii. Set address-family ipv4 unicast with neighbor IP and activate
        d. Configure Tenant VRFs
            i. Set each Tenant VRF to rd 1:1
            ii. Set address-family ipv4 unicast and route-target imports and exports for each Tenant VRF
        e. Set VLAN interfaces as default gateways
            i. Attach specified Tenant VRF and IP address on subnet
        f. Configure Router BGP for Tenant VRFs
            i. For each Tenant VRF, set address-family ipv4 unicast and redistribute connected
   Ex:
    vrf Core
        rd 1:3
        address-family ipv4 unicast
            route-target export 65001:3
            route-target import 65001:1
            route-target import 65001:2
            route-target import 65001:3
        exit-address-family
    vrf VRFa
        rd 1:1
        address-family ipv4 unicast
            route-target export 65001:1
            route-target import 65001:1
            route-target import 65001:3
        exit-address-family
    vrf VRFb
        rd 1:2
        address-family ipv4 unicast
            route-target export 65001:2
            route-target import 65001:2
            route-target import 65001:3
        exit-address-family
    interface lag 10
        no shutdown
        no routing
        vlan trunk native 1
        vlan trunk allowed 11-12
        lacp mode active
    interface 1/1/51
        vrf attach Core
        ip address 10.1.1.12/31
    interface vlan11
        vrf attach VRFa
        ip address 10.3.1.2/24
        active-gateway ip mac 00:00:00:00:01:01
        active-gateway ip 10.3.1.1
    interface vlan12
        vrf attach VRFb
        ip address 10.3.2.2/24
        active-gateway ip mac 00:00:00:00:01:01
        active-gateway ip 10.3.2.1
    interface vxlan 1
        source ip 10.2.0.2
        no shutdown
        vni 11
            vlan 11
        vni 12
            vlan 12
    router bgp 65001
        vrf Core
            neighbor 10.1.1.13 remote-as 65002
            address-family ipv4 unicast
                neighbor 10.1.1.13 activate
            exit-address-family
        vrf VRFa
            address-family ipv4 unicast
                redistribute connected
            exit-address-family
        vrf VRFb
            address-family ipv4 unicast
                redistribute connected
            exit-address-family

Preconditions:
At least 3 switches, with at least 1 functioning as a Spine, the rest as the Leaf(s), one Leaf designated as Border Leaf
"""

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import os
import sys
import json

dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(dirpath)
sys.path.append(os.path.join(dirpath, "src"))
sys.path.append(os.path.join(dirpath, "cx_utils"))

from cx_utils import yaml_ops
from src import session, vlan, interface, ospf, bgp, lag, vxlan, evpn, vrf, vsx

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
    data = yaml_ops.read_yaml("evpn_vxlan_data.yaml")

    if not data['version']:
        data['version'] = "v1"

    # Setting up Spines for Fabric Infrastructure
    print("Setting up Spines for Fabric Infrastructure...")
    for spine_data in data['spines']:
        if data['bypassproxy']:
            os.environ['no_proxy'] = spine_data['mgmtip']
            os.environ['NO_PROXY'] = spine_data['mgmtip']
        base_url = "https://{0}/rest/{1}/".format(spine_data['mgmtip'], data['version'])
        try:
            print("Setting up Spine at %s" % spine_data['mgmtip'])
            session_dict = dict(s=session.login(base_url, spine_data['username'], spine_data['password']), url=base_url)

            # Create OSPFv2 ID
            ospf.create_ospf_id(spine_data['ospfvrf'], spine_data['ospfid'], **session_dict)

            # Create an OSPFv2 Area for OSPF ID
            ospf.create_ospf_area(spine_data['ospfvrf'], spine_data['ospfid'], spine_data['ospfarea'], **session_dict)

            # Create Loopback interface
            interface.create_loopback_interface(spine_data['loopbackinterface'], spine_data['ospfvrf'],
                                                spine_data['loopbackip'], **session_dict)
            ospf.create_ospf_interface(spine_data['ospfvrf'], spine_data['ospfid'], spine_data['ospfarea'],
                                       spine_data['loopbackinterface'], **session_dict)

            # Create downstream interfaces
            for downstream in spine_data['downstreaminterface']:
                interface.add_l3_ipv4_interface(downstream['interface'], downstream['ipaddress'], **session_dict)
                interface.enable_disable_interface(downstream['interface'], "up", **session_dict)

                # Attach downstream interface to OSPF ID
                ospf.create_ospf_interface(spine_data['ospfvrf'], spine_data['ospfid'], spine_data['ospfarea'],
                                           downstream['interface'], **session_dict)
                ospf.update_ospf_interface_type(spine_data['ospfvrf'], spine_data['ospfid'], downstream['interface'],
                                                spine_data['ospftype'], **session_dict)

            # Create BGP ASN and Router ID
            bgp.create_bgp_asn(spine_data['ospfvrf'], spine_data['bgpasn'], spine_data['bgprouterid'],
                               **session_dict)
            # Set BGP Neighbors
            for neighbors in spine_data['neighborips']:
                bgp.create_bgp_neighbors(spine_data['ospfvrf'], spine_data['bgpasn'], neighbors,
                                         spine_data['addressfamilytype'], reflector=True, send_community=True,
                                         local_interface=spine_data['loopbackinterface'], **session_dict)

        except Exception as error:
            print('Ran into exception: {}. Logging out..'.format(error))

        session.logout(**session_dict)

    # Setting up Leafs for Fabric Infrastructure
    print("Setting up Leafs for Fabric Infrastructure...")
    for leaf_data in data['leafs']:
        if data['bypassproxy']:
            os.environ['no_proxy'] = leaf_data['mgmtip']
            os.environ['NO_PROXY'] = leaf_data['mgmtip']
        base_url = "https://{0}/rest/{1}/".format(leaf_data['mgmtip'], data['version'])
        try:
            print("Setting up Leaf at %s" % leaf_data['mgmtip'])
            session_dict = dict(s=session.login(base_url, leaf_data['username'], leaf_data['password']), url=base_url)

            # Create OSPFv2 ID
            ospf.create_ospf_id(leaf_data['ospfvrf'], leaf_data['ospfid'], **session_dict)

            # Create an OSPFv2 Area for OSPF ID
            ospf.create_ospf_area(leaf_data['ospfvrf'], leaf_data['ospfid'], leaf_data['ospfarea'], **session_dict)

            # Create Loopback interface
            interface.create_loopback_interface(leaf_data['loopbackinterface'], leaf_data['ospfvrf'],
                                                leaf_data['loopbackip'], **session_dict)
            ospf.create_ospf_interface(leaf_data['ospfvrf'], leaf_data['ospfid'], leaf_data['ospfarea'],
                                       leaf_data['loopbackinterface'], **session_dict)

            # Create upstream interfaces
            for upstream in leaf_data['upstreaminterface']:
                interface.add_l3_ipv4_interface(upstream['interface'], upstream['ipaddress'], **session_dict)
                interface.enable_disable_interface(upstream['interface'], "up", **session_dict)

                # Attach upstream interface to OSPF ID
                ospf.create_ospf_interface(leaf_data['ospfvrf'], leaf_data['ospfid'], leaf_data['ospfarea'],
                                           upstream['interface'], **session_dict)
                ospf.update_ospf_interface_type(leaf_data['ospfvrf'], leaf_data['ospfid'], upstream['interface'],
                                                leaf_data['ospftype'], **session_dict)

            # Create BGP ASN and Router ID
            bgp.create_bgp_asn(leaf_data['ospfvrf'], leaf_data['bgpasn'], leaf_data['bgprouterid'],
                               **session_dict)
            # Set BGP Neighbors
            for neighbors in leaf_data['neighborips']:
                bgp.create_bgp_neighbors(leaf_data['ospfvrf'], leaf_data['bgpasn'], neighbors,
                                         leaf_data['addressfamilytype'], reflector=False, send_community=True,
                                         local_interface=leaf_data['loopbackinterface'], **session_dict)

            # Create VLANs
            for vlan_id in leaf_data['vnivlans']:
                vlan.create_vlan(vlan_id, "VLAN%d" % vlan_id, **session_dict)

            # Create LAGs to Downstream Servers
            for lag_data in leaf_data['lagtoserver']:
                lag.create_l2_lag_interface(lag_data['name'], lag_data['interfaces'], lag_data['lacp_mode'],
                                            lag_data['mc_lag'], False, lag_data['trunk_vlans'], **session_dict)

            # Create VXLAN
            vxlan.create_vxlan_interface(leaf_data['vxlanname'], leaf_data['vxlanip'], **session_dict)

            # Map VNI to VLAN
            for vni_list in leaf_data['vnivlans']:
                vxlan.add_vni_mapping(vni_list, leaf_data['vxlanname'], vni_list, **session_dict)

            # Create EVPN instance
            evpn.create_evpn_instance(**session_dict)

            # Configure EVPN Routes
            for vlan_id in leaf_data['vnivlans']:
                evpn.add_evpn_vlan(vlan_id, **session_dict)

        except Exception as error:
            print('Ran into exception: {}. Logging out..'.format(error))

        session.logout(**session_dict)

    # Setup Border Leaf
    print("Setting up Border Leaf...")
    border_data = data['borderleaf'][0]
    if data['bypassproxy']:
        os.environ['no_proxy'] = border_data['mgmtip']
        os.environ['NO_PROXY'] = border_data['mgmtip']
    base_url = "https://{0}/rest/{1}/".format(border_data['mgmtip'], data['version'])
    try:
        session_dict = dict(s=session.login(base_url, border_data['username'], border_data['password']),
                            url=base_url)
        # Create VRF to Core
        vrf.add_vrf(border_data['vrftocore'], border_data['rd'], **session_dict)
        vrf.add_vrf_address_family(border_data['vrftocore'], border_data['addressfamilytype'],
                                   border_data['addressfamilyexports'], border_data['addressfamilyimports'],
                                   **session_dict)
        # Setup link to Core
        interface.add_l3_ipv4_interface(border_data['interfacetocore'], ip_address=border_data['interfacetocoreip'],
                                   vrf=border_data['vrftocore'], **session_dict)
        # Setup BGP to Core
        bgp.create_bgp_asn(border_data['vrftocore'], border_data['neighbortocoreasn'], **session_dict)
        bgp.create_bgp_neighbors(border_data['vrftocore'], border_data['neighbortocoreasn'], border_data['neighbortocoreip'],
                                 border_data['addressfamilytype'], reflector=False, send_community=False,
                                 **session_dict)
        # Configure Leaf VRF Routes and Address-family
        for tenants in border_data['tenantvrfs']:
            vrf.add_vrf(tenants['name'], tenants['rd'], **session_dict)
            vrf.add_vrf_address_family(tenants['name'], border_data['addressfamilytype'],
                                       tenants['addressfamilyexports'], tenants['addressfamilyimports'],
                                       **session_dict)
            bgp.create_bgp_asn(tenants['name'], border_data['bgpasn'], **session_dict)
            bgp.create_bgp_vrf(tenants['name'], border_data['bgpasn'], tenants['redistribute'], **session_dict)

        # Attach Leaf VRFs and give IP Addresses to VLANs
        for border_vlan in border_data['interfacevlans']:
            vlan.create_vlan_and_svi(border_vlan['vlanid'], "VLAN%d" % border_vlan['vlanid'],
                                     "vlan%d" % border_vlan['vlanid'], "vlan%d" % border_vlan['vlanid'],
                                     vlan_desc=None, ipv4=border_vlan['vlanip'], vrf_name=border_vlan['vlanvrf'],
                                     **session_dict)
            vsx.update_vsx_interface_vlan(border_vlan['vlanid'], False, [], border_vlan['activegatewaymac'],
                                          border_vlan['activegatewayip'], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict)

if __name__ == '__main__':
    main()
