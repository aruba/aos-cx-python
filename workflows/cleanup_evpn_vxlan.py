#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/evpn_vxlan_data.yaml file.
This workflow performs the following steps:
A. Cleanup Tenant Infrastructure (VRFs and VXLAN)
    1. Remove Border Leaf Switch configurations
        a. Delete Tenant VRFs
        b. Delete Router BGP settings
        c. Remove external facing Interface settings
        d. Delete VRF to Core
   Ex:
    router bgp 65001
        no vrf Core
        no vrf VRFa
        no vrf VRFb
    no router bgp 65001
    interface 1/1/51
        no ip address 10.1.1.12/31

    2. Delete EVPN settings on each Leaf
   Ex:
    no evpn

    3. Delete VXLAN interface on each Leaf
   Ex:
    no interface vxlan 1

    4. Remove configurations of Leaf Switches to Servers
        a. Delete LAGs
        b. Delete VLANs on Leaf switches
   Ex:
    no interface vlan11
    no interface vlan12
    no interface lag 10

B. Cleanup Fabric Infrastructure (OSPF and BGP Setup on Spines and Leafs)
    1. Delete IBGP EVPN peering on each Leaf switches to Spines
        a. Delete BGP Neighbors
        b. Delete BGP ASN
   Ex:
    router bgp 65001
        no bgp router-id 10.2.0.2
        no neighbor 10.2.0.101 remote-as 65001
    no router bgp 65001

    2. Delete Uplink Configurations on Leaf Switches to Spines
   Ex:
    interface 1/1/2
        shutdown
        no ip address 10.1.1.0/31
        no ip ospf 1 area 0.0.0.0
        routing

    3. Delete Loopback Interface on each Leaf
   Ex:
    no interface loopback 0

    4. Delete OSPF on each Leaf
        a. Delete an OSPFv2 Area
        b. Delete an OSPFv2 ID
   Ex:
    no router ospf 1

    5. Delete IBGP EVPN peering on Spines towards all Leaf switches
        a. Delete BGP Neighbors
        b. Delete BGP ASN
   Ex:
    router bgp 65001
        no bgp router-id 10.2.0.101
        no neighbor 10.2.0.1 remote-as 65001
        no neighbor 10.2.0.2 remote-as 65001
    no router bgp 65001

    6. Delete Downlink Configurations on Spines to Leaf Switches
   Ex:
    interface 1/1/2
        shutdown
        no ip address 10.1.1.1/31
        no ip ospf 1 area 0.0.0.0
        routing
    interface 1/1/3
        shutdown
        no ip address 10.1.1.5/31
        no ip ospf 1 area 0.0.0.0
        routing

    7. Delete Loopback Interface on Spines
   Ex:
    no interface loopback 0

    8. Delete OSPF On Spines
        a. Delete an OSPFv2 Area
        b. Delete an OSPFv2 ID
   Ex:
    no router ospf 1

Preconditions:
Switches must be configured with the configure_evpn_vxlan workflow
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
from src import session, vlan, interface, ospf, bgp, lag, vxlan, evpn, vrf

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
    data = yaml_ops.read_yaml("evpn_vxlan_data.yaml")

    if not data['version']:
        data['version'] = "v10.04"

    # Cleanup Border Leaf
    print("Cleaning up Border Leaf configuration...")
    border_data = data['borderleaf'][0]
    if data['bypassproxy']:
        os.environ['no_proxy'] = border_data['mgmtip']
        os.environ['NO_PROXY'] = border_data['mgmtip']
    base_url = "https://{0}/rest/{1}/".format(border_data['mgmtip'], data['version'])
    try:
        session_dict = dict(s=session.login(base_url, border_data['username'], border_data['password']),
                            url=base_url)
        # Delete external facing Interface settings
        for border_vlan in border_data['interfacevlans']:
            vlan.delete_vlan_and_svi(border_vlan['vlanid'], "vlan%d" % border_vlan['vlanid'], **session_dict)

        # Delete Tenant VRFs
        for tenants in border_data['tenantvrfs']:
            bgp.delete_bgp_asn(tenants['name'], border_data['bgpasn'], **session_dict)
            vrf.delete_vrf(tenants['name'], **session_dict)

        # Remove Interface Settings to Core
        interface.initialize_interface(border_data['interfacetocore'], **session_dict)

        # Delete Router BGP Settings
        bgp.delete_bgp_asn(border_data['vrftocore'], border_data['neighbortocoreasn'], **session_dict)

        # Delete VRF to Core
        vrf.delete_vrf(border_data['vrftocore'], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict)

    # Cleaning up Leafs for Fabric Infrastructure
    print("Cleaning up Leafs for Fabric Infrastructure...")
    for leaf_data in data['leafs']:
        if data['bypassproxy']:
            os.environ['no_proxy'] = leaf_data['mgmtip']
            os.environ['NO_PROXY'] = leaf_data['mgmtip']
        base_url = "https://{0}/rest/{1}/".format(leaf_data['mgmtip'], data['version'])
        try:
            print("Cleaning up Leaf at %s" % leaf_data['mgmtip'])
            session_dict = dict(s=session.login(base_url, leaf_data['username'], leaf_data['password']), url=base_url)
            # Remove BGP info
            # Delete EVPN instance
            evpn.delete_evpn_instance(**session_dict)

            # Delete VNI to VLAN
            for vni_list in leaf_data['vnivlans']:
                vxlan.delete_vni_mapping(vni_list, **session_dict)

            # Delete VXLAN
            interface.delete_interface(leaf_data['vxlanname'], **session_dict)

            # Delete LAGs to Downstream Servers
            for lag_data in leaf_data['lagtoserver']:
                lag.delete_lag_interface(lag_data['name'], lag_data['interfaces'], **session_dict)

            # Delete VLANs
            for vlan_id in leaf_data['vnivlans']:
                vlan.delete_vlan(vlan_id, **session_dict)

            # Delete BGP ASN and Router ID
            bgp.delete_bgp_asn(leaf_data['ospfvrf'], leaf_data['bgpasn'], **session_dict)

            # Remove OSPF and Interfaces
            # Initialize upstream L2 interfaces
            for upstream in leaf_data['upstreaminterface']:
                interface.initialize_interface(upstream['interface'], **session_dict)

            # Delete Loopback interface
            interface.delete_interface(leaf_data['loopbackinterface'], **session_dict)

            # Delete an OSPFv2 Area for OSPF ID
            ospf.delete_ospf_area(leaf_data['ospfvrf'], leaf_data['ospfid'], leaf_data['ospfarea'], **session_dict)

            # Delete OSPFv2 ID
            ospf.delete_ospf_id(leaf_data['ospfvrf'], leaf_data['ospfid'], **session_dict)

        except Exception as error:
                print('Ran into exception: {}. Logging out..'.format(error))

        session.logout(**session_dict)

    # Cleaning up Spines for Fabric Infrastructure
    print("Cleaning up Spines of Fabric Infrastructure...")
    for spine_data in data['spines']:
        if data['bypassproxy']:
            os.environ['no_proxy'] = spine_data['mgmtip']
            os.environ['NO_PROXY'] = spine_data['mgmtip']
        base_url = "https://{0}/rest/{1}/".format(spine_data['mgmtip'], data['version'])
        try:
            print("Setting up Spine at %s" % spine_data['mgmtip'])
            session_dict = dict(s=session.login(base_url, spine_data['username'], spine_data['password']), url=base_url)

            # Remove BGP configuration
            # Delete BGP ASN and Router ID
            bgp.delete_bgp_asn(spine_data['ospfvrf'], spine_data['bgpasn'], **session_dict)

            # Initialize downstream L2 interfaces
            for downstream in spine_data['downstreaminterface']:
                interface.initialize_interface(downstream['interface'], **session_dict)

            # Create Loopback interface
            interface.delete_interface(spine_data['loopbackinterface'], **session_dict)

            # Create an OSPFv2 Area for OSPF ID
            ospf.delete_ospf_area(spine_data['ospfvrf'], spine_data['ospfid'], spine_data['ospfarea'], **session_dict)

            # Create OSPFv2 ID
            ospf.delete_ospf_id(spine_data['ospfvrf'], spine_data['ospfid'], **session_dict)

        except Exception as error:
            print('Ran into exception: {}. Logging out..'.format(error))

        session.logout(**session_dict)

if __name__ == '__main__':
    main()
