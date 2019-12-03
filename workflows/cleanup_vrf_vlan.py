#!/usr/bin/env python3
"""
This workflow performs the following steps:
1. Remove all IPv4 DHCP helpers for SVI
      Ex:
        interface vlan999
            no ip helper-address 1.1.1.1
            no ip helper-address 2.2.2.2

2. Remove VLANs and SVIs
      Ex:
        no interface vlan 888
        no interface vlan 999
        no vlan 888
        no vlan 999

3. Remove VRF
      Ex:
        no vrf VRFa

4. Reset the L2 interface
      Ex:
        interface 1/1/20
            no shutdown
            no routing
            vlan access 1

Preconditions:
Must have run either the vrf_vlan_access or vrf_vlan_trunk workflow, or have the equivalent settings.

Note: Doing "no interface vlan999" removes all DHCP helpers, vlan999 from Interface table,
vlan999 from Ports table, vlan999 from bridge -> ports, and vlan999 from vrfs->LAB->ports
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
from src import session, vrf, dhcp, interface, vlan

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
    data = yaml_ops.read_yaml("vrf_vlan_data.yaml")

    if not data['switchip']:
        data['switchip'] = input("Switch IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['switchip']
        os.environ['NO_PROXY'] = data['switchip']

    base_url = "https://{0}/rest/{1}/".format(data['switchip'], data['version'])
    try:
        session_dict = dict(s=session.login(base_url, data['username'], data['password']), url=base_url)

        # Delete all DHCP relays for interface
        dhcp.delete_dhcp_relays(data['vlan1portname'], data['vrfname'], **session_dict)

        # Delete VLAN and SVI
        vlan.delete_vlan_and_svi(data['vlan1id'], data['vlan1portname'], **session_dict)
        vlan.delete_vlan_and_svi(data['vlan2id'], data['vlan2portname'], **session_dict)

        # Delete VRF
        vrf.delete_vrf(data['vrfname'], **session_dict)

        # Initialize System interface
        interface.initialize_interface(data['systeminterfacename'], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
