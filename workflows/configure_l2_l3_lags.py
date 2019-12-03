#!/usr/bin/env python3
"""
This workflow performs the following steps:
1. Create VLANs and L2 LAG
    a. Create VLANs
    b. Create L2 LAG and associate VLANs as trunk VLANs
    Ex:
      vlan 66
          name vlan66
      vlan 67
          name vlan67
      interface lag 66
          no shutdown
          no routing
          vlan trunk native 1
          vlan trunk allowed 66-67
      interface 1/1/51
          no shutdown
          lag 66
      interface 1/1/52
          no shutdown
          lag 66

2. Create L3 LAG
    Ex:
      interface lag 11
          no shutdown
          description L3-LAG
          ip address 172.177.77.7/24
          lacp mode active
      interface 1/1/3
          no shutdown
          lag 11
      interface 1/1/4
          no shutdown
          lag 11

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
from src import system
from src import lag
from src import interface

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    data = yaml_ops.read_yaml("lag_data.yaml")

    if not data['switchip']:
        data['switchip'] = input("Switch IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['switchip']
        os.environ['NO_PROXY'] = data['switchip']

    base_url = "https://{0}/rest/{1}/".format(data['switchip'], data['version'])
    try:
        session_dict = dict(s=session.login(base_url, data['username'], data['password']), url=base_url)

        system_info_dict = system.get_system_info(**session_dict)

        platform_name = system_info_dict['platform_name']

        # Create VLANs and L2 LAG; assign VLANs as trunk VLANs on LAG
        for l2_lag_data in data['l2_lags']:
            # Create VLANs
            for vlan_id in l2_lag_data['trunk_vlans']:
                vlan.create_vlan(vlan_id, "vlan%s" % vlan_id, **session_dict)

            # Create L2 LAG, add L2 ports to the LAG, and assign VLANs as trunk VLANs on the LAG
            lag.create_l2_lag_interface(l2_lag_data.get('name'), l2_lag_data.get('interfaces'),
                                        vlan_ids_list=l2_lag_data.get('trunk_vlans'),
                                        lacp_mode=l2_lag_data.get('lacp_mode'), mc_lag=l2_lag_data.get('mc_lag'),
                                        **session_dict)

        # Create L3 LAGs
        for l3_lag_data in data['l3_lags']:
            # Create L3 LAG and add L2 ports to the LAG
            lag.create_l3_lag_interface(l3_lag_data.get('name'), l3_lag_data.get('interfaces'), l3_lag_data.get('ipv4'),
                                        lacp_mode=l3_lag_data.get('lacp_mode'), desc=l3_lag_data.get('description'),
                                        **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
