#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/ospf_data.yaml file.
This workflow performs the following steps:
1. Delete/Initialize L3 interfaces
   Ex:
    interface 1/1/3
        shutdown
        no ipv6 address 10::11/124
        no ipv6 ospfv3 2 area 0.0.0.1
    interface 1/1/1
        shutdown
        no ip address 10.10.10.11/30
        no ip ospf 1 area 0.0.0.0
        no ip ospf authentication message-digest
        no ip ospf message-digest-key 3 md5 ciphertext <md5 key>

2. Delete OSPFv3 Area for OSPFv3 ID
   Ex:
    router ospfv3 2
        no area 0.0.0.1

3. Delete OSPF Area for OSPFv2 ID
   Ex:
    router ospf 1
        no area 0.0.0.0

4. Delete OSPFv3 ID
   Ex:
    no router ospfv3 2

5. Delete OSPFv2 ID
   Ex:
    no router ospf 1

Preconditions:
Switch must be configured with the configure_ospf workflow
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
from src import session, ospf, interface

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
    data = yaml_ops.read_yaml("ospf_data.yaml")

    if not data['switchip']:
        data['switchip'] = input("Switch IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['switchip']
        os.environ['NO_PROXY'] = data['switchip']

    if not data['version']:
        data['version'] = "v1"

    base_url = "https://{0}/rest/{1}/".format(data['switchip'],data['version'])
    try:
        session_dict = dict(s=session.login(base_url, data['username'], data['password']), url=base_url)

        # Initialize L3 interfaces
        interface.initialize_interface(data['l3interfacev3'], **session_dict)
        interface.initialize_interface(data['l3interfacev2'], **session_dict)

        # Remove an OSPFv3 Area for OSPF ID
        ospf.delete_ospfv3_area(data['ospfv3vrf'], data['ospfv3id'], data['ospfv3area'], **session_dict)

        # Remove an OSPFv2 Area for OSPF ID
        ospf.delete_ospf_area(data['ospfv2vrf'], data['ospfv2id'], data['ospfv2area'], **session_dict)

        # Remove OSPFv3 ID
        ospf.delete_ospfv3_id(data['ospfv3vrf'], data['ospfv3id'], **session_dict)

        # Remove OSPFv2 ID
        ospf.delete_ospf_id(data['ospfv2vrf'], data['ospfv2id'], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict)


if __name__ == '__main__':
    main()
