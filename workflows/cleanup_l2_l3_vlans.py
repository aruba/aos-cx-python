#!/usr/bin/env python3
"""
This workflow performs the following steps:
1. Delete DHCP helpers from SVI
      Ex:
        interface vlan999
            no ip helper-address 1.1.1.1
            no ip helper-address 2.2.2.2

2. Delete SVI
      Ex:
        no interface vlan 999

3. Delete VLAN
      Ex:
        no vlan 999

4. Initialize L2 interface
      Ex:
        interface 1/1/20
            no shutdown
            no routing
            vlan access 1

Preconditions:
Must have run the configure_l2_l3_vlans workflow or have the equivalent settings.
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
from src import session
from src import dhcp
from src import interface
from src import vlan

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    data = yaml_ops.read_yaml("vlan_data.yaml")

    if not data['switchip']:
        data['switchip'] = input("Switch IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['switchip']
        os.environ['NO_PROXY'] = data['switchip']

    base_url = "https://{0}/rest/{1}/".format(data['switchip'],data['version'])
    try:
        session_dict = dict(s=session.login(base_url, data['username'], data['password']), url=base_url)

        # Delete all DHCP relays for interface
        dhcp.delete_dhcp_relays(data['vlanportname'], "default", **session_dict)

        # Delete VLAN and SVI
        vlan.delete_vlan_and_svi(data['vlanid'], data['vlanportname'], **session_dict)

        # Initialize L2 interface
        interface.initialize_interface(data['physicalport'], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
