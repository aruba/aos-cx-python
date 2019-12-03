#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/loop_protect_data.yaml file.
This workflow performs the following steps:
1. Clear the Loop-protect settings on the L2 interface
   Ex:
    interface 1/1/3
        no loop-protect

2. Clear the Loop-protect settings on the LAG
   Ex:
    interface lag 99
        no loop-protect

3. Delete the L2 Interface
   Ex:
    interface 1/1/3
        shutdown
        routing
    interface 1/1/4
        shutdown
        no lag 99
    interface 1/1/5
        shutdown
        no lag 99

4. Delete the LAG
   Ex:
    no interface lag 99

5. Delete the VLANs
   Ex:
    no vlan 998
    no vlan 999

Preconditions:
Must have run configure_loop_protect workflow or have an equivalent configuration on the device
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
from src import session, vlan, system, lag, interface, loop_protect

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    data = yaml_ops.read_yaml("loop_protect_data.yaml")

    if not data['switchip']:
        data['switchip'] = input("Switch IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['switchip']
        os.environ['NO_PROXY'] = data['switchip']

    base_url = "https://{0}/rest/{1}/".format(data['switchip'], data['version'])
    try:
        session_dict = dict(s=session.login(base_url, data['username'], data['password']), url=base_url)

        system_info_dict = system.get_system_info(params={"selector": "configuration"}, **session_dict)

        # Clear Loop-protect settings on Interface
        loop_protect.clear_port_loop_protect(data['interfacename'], **session_dict)

        # Initialize L2 Interface
        interface.initialize_interface(data['interfacename'], **session_dict)

        # Delete L2 LAGs:
        for l2_lag_data in data['lags']:
            # Delete VLANs
            for vlan_id in l2_lag_data['trunk_vlans']:
                vlan.delete_vlan(vlan_id, **session_dict)

            # Clear Loop-protect settings on LAG
            loop_protect.clear_port_loop_protect(l2_lag_data.get('name'), **session_dict)

            # Delete LAG
            lag.delete_lag_interface(l2_lag_data['name'], l2_lag_data.get('interfaces'), **session_dict)


    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
