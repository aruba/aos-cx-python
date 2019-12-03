#!/usr/bin/env python3
"""
This workflow performs the following steps:
1. Create VLAN
      Ex:
        vlan 999
            description For LAB 999

2. Create SVI
      Ex:
        interface vlan999
            description ### SVI for LAB999 ###
            ip address 10.10.10.99/24

3. Add DHCP helpers for SVI
      Ex:
        interface vlan999
            description ### SVI for LAB999 ###
            ip address 10.10.10.99/24
            ip helper-address 1.1.1.1
            ip helper-address 2.2.2.2

3. Create L2 interface
    a. Create the interface
    b. Enable the interface
    c. Set VLAN mode to 'access'
    d. Set VLAN as untagged VLAN
      Ex:
        interface 1/1/20
            no shutdown
            no routing
            vlan access 999



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
from src import session
from src import vlan
from src import interface
from src import dhcp

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

        vlan.create_vlan_and_svi(data['vlanid'], data['vlanname'], data['vlanportname'], data['vlaninterfacename'],
                                 data['vlandescription'], data['vlanip'], vlan_port_desc=data['vlanportdescription'],
                                 **session_dict)

        # Add DHCP helper IPv4 addresses for SVI
        dhcp.add_dhcp_relays(data['vlanportname'], "default", data['ipv4helperaddresses'], **session_dict)

        # Add a new entry to the Port table if it doesn't yet exist
        interface.add_l2_interface(data['physicalport'], **session_dict)

        # Update the Interface table entry with "user-config": {"admin": "up"}
        interface.enable_disable_interface(data['physicalport'], **session_dict)

        # Set the L2 port VLAN mode as 'access'
        vlan.port_set_vlan_mode(data['physicalport'], "access", **session_dict)

        # Set the access VLAN on the port
        vlan.port_set_untagged_vlan(data['physicalport'], data['vlanid'], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
