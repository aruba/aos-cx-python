#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/vsx_data.yaml file.
This workflow performs the following steps:
1. Setup primary VSX switch
    a. Create VLANs
   Ex:
    vlan 1,77,88
    vlan 100
        description Downstream VLAN 100
    interface vlan77
        description ISL VLAN
    interface vlan88
        description ISL VLAN

    b. Create a VSX Instance
        i. Set Keep Alive IP Address
        ii. Set Keep Alive MACs
   Ex:
    vsx
        system-mac 00:11:22:33:44:55
        inter-switch-link lag 33
        role primary
        keepalive peer 192.168.6.2 source 192.168.6.1

    c. Assign VSX Active Gateways to VLANs
   Ex:
    interface vlan100
        vsx-sync active-gateways policies
        ip address 10.100.100.1/24
        active-gateway ip mac 00:00:00:00:00:01
        active-gateway ip 10.100.100.200

    d. Create Interfaces
        i. Create LAG to function as ISL
        ii. Create interface to function as Keep-alive connection
        iii. Create MCLAGs to downstream devices
   Ex:
    interface lag 20 multi-chassis
        no shutdown
        description Downstream MCLAG
        no routing
        vlan trunk native 1
        vlan trunk allowed 100
        lacp mode active
        lacp fallback
    interface lag 33
        no shutdown
        description ISL LAG
        no routing
        vlan trunk native 1
        vlan trunk allowed 77,88,100
        lacp mode active
    interface 1/1/23
        no shutdown
        lag 20
    interface 1/1/24
        no shutdown
        lag 20
    interface 1/1/46
        no shutdown
        lag 33
    interface 1/1/47
        no shutdown
        lag 33
    interface 1/1/48
        no shutdown
        ip address 192.168.6.1/24

2. Setup Secondary VSX switch
    a. Create VLANs
   Ex:
    vlan 1,77,88
    vlan 100
        description Downstream VLAN 100
    interface vlan77
        description ISL VLAN
    interface vlan88
        description ISL VLAN

    b. Create a VSX Instance
        i. Set Keep Alive IP Address
        ii. Set Keep Alive MACs
   Ex:
    vsx
        system-mac 00:11:22:33:44:55
        inter-switch-link lag 33
        role secondary
        keepalive peer 192.168.6.1 source 192.168.6.2

    c. Assign VSX Active Gateways to VLANs
   Ex:
    interface vlan100
        vsx-sync active-gateways policies
        ip address 10.100.100.2/24
        active-gateway ip mac 00:00:00:00:00:01
        active-gateway ip 10.100.100.200

    d. Create Interfaces
        i. Create LAG to function as ISL
        ii. Create interface to function as Keep-alive connection
        iii. Create MCLAGs to downstream devices
   Ex:
    interface lag 20 multi-chassis
        no shutdown
        description Downstream MCLAG
        no routing
        vlan trunk native 1
        vlan trunk allowed 100
        lacp mode active
        lacp fallback
    interface lag 33
        no shutdown
        description ISL LAG
        no routing
        vlan trunk native 1
        vlan trunk allowed 77,88,100
        lacp mode active
    interface 1/1/23
        no shutdown
        lag 20
    interface 1/1/24
        no shutdown
        lag 20
    interface 1/1/46
        no shutdown
        lag 33
    interface 1/1/47
        no shutdown
        lag 33
    interface 1/1/48
        no shutdown
        ip address 192.168.6.2/24

Preconditions:
Switch model must be VSX capable
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
from src import session, vlan, interface, vsx, system, lag

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    # This is the yaml file that will be used for the vsx_configuration
    data = yaml_ops.read_yaml("vsx_data.yaml")

    if not data['primarymgmtip']:
        data['primarymgmtip'] = input("Switch Primary IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['primarymgmtip']
        os.environ['NO_PROXY'] = data['primarymgmtip']

    if not data['version']:
        data['version'] = "v10.04"

    # Setup VSX on Primary
    base_url_1 = "https://{0}/rest/{1}/".format(data['primarymgmtip'], data['version'])
    try:
        session_dict_1 = dict(s=session.login(base_url_1, data['primaryusername'], data['primarypassword']),
                              url=base_url_1)

        # Create VLANs
        for vlans in data['islvlans']:
            vlan.create_vlan_and_svi(vlans, "VLAN%s" % vlans, "vlan%s" % vlans, "vlan%s" % vlans,
                                     vlan_port_desc="ISL VLAN", **session_dict_1)

        vlan.create_vlan_and_svi(data['vlanid'], data['vlanname'], data['vlanportname'], data['vlanportname'],
                                 data['vlanportdescription'], data['primaryvlanip'], **session_dict_1)

        # Create LAG for ISL
        for link in data['peer1isllaginterfaces']:
            interface.enable_disable_interface(link, state="up", **session_dict_1)
        lag.create_l2_lag_interface(data['islport'], data['peer1isllaginterfaces'], lacp_mode=data['isllacp'],
                                    mc_lag=False, fallback_enabled=False,
                                    vlan_ids_list=(data['islvlans'] + [data['vlanid']]), desc="ISL LAG",
                                    **session_dict_1)

        # Create Downstream MCLAG
        for mclink in data['peer1mclaginterfaces']:
            interface.enable_disable_interface(mclink, state="up", **session_dict_1)
        lag.create_l2_lag_interface(data['mclagport'], data['peer1mclaginterfaces'], lacp_mode=data['mclaglacp'],
                                    mc_lag=True, fallback_enabled=True, vlan_ids_list=data['mclagvlans'],
                                    desc="Downstream MCLAG", **session_dict_1)

        # Create VSX Instance
        vsx.create_vsx("primary", data['islport'], data['secondarykeepaliveip'], data['primarykeepaliveip'],
                       data['keepalivevrf'], data['vsxmac'], **session_dict_1)
        interface.add_l3_ipv4_interface(data['primarykeepaliveinterface'], data['primarykeepaliveip'],
                                        desc="Keepalive Link", **session_dict_1)
        interface.enable_disable_interface(data['primarykeepaliveinterface'], state="up", **session_dict_1)

        # Assign VSX Active-Gateways and synchronization options to VLANs
        vsx.update_vsx_interface_vlan(data['vlanid'], False, {'active-gateways', 'policies'}, data['activegatewaymac'],
                                      data['activegatewayip'], **session_dict_1)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict_1)

    # Setup VSX on Secondary
    if not data['secondarymgmtip']:
        data['secondarymgmtip'] = input("Switch Secondary IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['secondarymgmtip']
        os.environ['NO_PROXY'] = data['secondarymgmtip']

    base_url_2 = "https://{0}/rest/{1}/".format(data['secondarymgmtip'], data['version'])
    try:
        session_dict_2 = dict(s=session.login(base_url_2, data['secondaryusername'], data['secondarypassword']),
                              url=base_url_2)

        # Create VLANs
        for vlans in data['islvlans']:
            vlan.create_vlan_and_svi(vlans, "VLAN%s" % vlans, "vlan%s" % vlans, "vlan%s" % vlans,
                                     vlan_port_desc="ISL VLAN", **session_dict_2)

        vlan.create_vlan_and_svi(data['vlanid'], data['vlanname'], data['vlanportname'], data['vlanportname'],
                                 data['vlanportdescription'], data['secondaryvlanip'], **session_dict_2)

        # Create LAG for ISL
        for link in data['peer2isllaginterfaces']:
            interface.enable_disable_interface(link, state="up", **session_dict_2)
        lag.create_l2_lag_interface(data['islport'], data['peer2isllaginterfaces'], lacp_mode=data['isllacp'],
                                    mc_lag=False, fallback_enabled=False,
                                    vlan_ids_list=(data['islvlans'] + [data['vlanid']]), desc="ISL LAG",
                                    **session_dict_2)

        # Create Downstream MCLAG
        for mclink in data['peer2mclaginterfaces']:
            interface.enable_disable_interface(mclink, state="up", **session_dict_2)
        lag.create_l2_lag_interface(data['mclagport'], data['peer2mclaginterfaces'], lacp_mode=data['mclaglacp'],
                                    mc_lag=True, fallback_enabled=True, vlan_ids_list=data['mclagvlans'],
                                    desc="Downstream MCLAG", **session_dict_2)

        # Create VSX Instance
        vsx.create_vsx("secondary", data['islport'], data['primarykeepaliveip'], data['secondarykeepaliveip'],
                       data['keepalivevrf'], data['vsxmac'], **session_dict_2)
        interface.add_l3_ipv4_interface(data['secondarykeepaliveinterface'], data['secondarykeepaliveip'],
                                        desc="Keepalive Link", **session_dict_2)
        interface.enable_disable_interface(data['secondarykeepaliveinterface'], state="up", **session_dict_2)

        # Assign VSX Active-Gateways to VLANs
        vsx.update_vsx_interface_vlan(data['vlanid'], False, {'active-gateways', 'policies'}, data['activegatewaymac'],
                                      data['activegatewayip'], **session_dict_2)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict_2)

if __name__ == '__main__':
    main()
