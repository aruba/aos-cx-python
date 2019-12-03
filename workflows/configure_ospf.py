#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/ospf_data.yaml file.
This workflow performs the following steps:
1. Create an OSPFv2 ID
    a. Configure the OSPF ID to redistribute connected
    b. Configure the OSPF ID to redistribute static
   Ex:
    router ospf 1
        redistribute connected
        redistribute static

2. Create an OSPFv2 Area for the previous OSPF ID
   Ex:
    router ospf 1
        area 0.0.0.0

3. Create L3 Interface and attach to OSPFv2 Area
   Ex:
    interface 1/1/1
        no shutdown
        ip address 10.10.10.11/30
        ip ospf 1 area 0.0.0.0
        ip ospf authentication message-digest
        ip ospf message-digest-key 3 md5 ciphertext <md5 key>

4. Create an OSPFv3 ID
   Ex:
    router ospfv3 2

5. Create an OSPFv3 Area for the previous OSPF ID
   Ex:
    router ospfv3 2
        area 0.0.0.1

6. Create L3 Interface and attach to OSPFv3 Area
   Ex:
    interface 1/1/3
        no shutdown
        ipv6 address 10::11/124
        ipv6 ospfv3 2 area 0.0.0.1

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
from src import session, vlan, interface, ospf

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    data = yaml_ops.read_yaml("ospf_data.yaml")

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

        # Create OSPFv2 ID
        ospf.create_ospf_id(data['ospfv2vrf'], data['ospfv2id'], **session_dict)

        # Create an OSPFv2 Area for OSPF ID
        ospf.create_ospf_area(data['ospfv2vrf'], data['ospfv2id'], data['ospfv2area'], **session_dict)

        # Create IPv4 L3 interface
        interface.add_l3_ipv4_interface(data['l3interfacev2'], data['l3interfacev2ipaddress'], **session_dict)
        interface.enable_disable_interface(data['l3interfacev2'], data['l3interfacestatusv2'], **session_dict)

        # Attach L3 interface to OSPF ID
        ospf.create_ospf_interface(data['ospfv2vrf'], data['ospfv2id'], data['ospfv2area'],
                                   data['l3interfacev2'], **session_dict)
        ospf.update_ospf_interface_authentication(data['ospfv2vrf'], data['ospfv2id'], data['l3interfacev2'],
                                                  data['ospfv2auth'], data['ospfv2digestkey'],
                                                  data['ospfv2password'], **session_dict)

        # Create OSPFv3 ID
        ospf.create_ospfv3_id(data['ospfv3vrf'], data['ospfv3id'], **session_dict)

        # Create an OSPFv3 Area for OSPF ID
        ospf.create_ospfv3_area(data['ospfv3vrf'], data['ospfv3id'], data['ospfv3area'], **session_dict)

        # Create IPv6 L3 interface
        interface.add_l3_ipv6_interface(data['l3interfacev3'], data['l3interfacev3ipaddress'], **session_dict)
        interface.enable_disable_interface(data['l3interfacev3'], data['l3interfacestatusv3'],
                                           **session_dict)

        # Attach L3 interface to OSPFv3 ID
        ospf.create_ospfv3_interface(data['ospfv3vrf'], data['ospfv3id'], data['ospfv3area'],
                                     data['l3interfacev3'], **session_dict)
        ospf.update_ospf_interface_authentication(data['ospfv3vrf'], data['ospfv3id'], data['l3interfacev2'],
                                                  data['ospfv3auth'], data['ospfv3digestkey'],
                                                  data['ospfv3password'], **session_dict)


    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict)


if __name__ == '__main__':
    main()
