#!/usr/bin/env python3
"""
This workflow performs the following steps:
1. Delete L2 LAGs and VLANs
    a. Delete VLANs
    b. Delete L2 LAG
    Ex:
      no vlan 66
      no vlan 67
      no interface lag 66
      interface 1/1/51
          no lag 66
      interface 1/1/52
          no lag 66

2. Delete L3 LAGs
    Ex:
      no interface lag 11
      interface 1/1/3
          no lag 11
      interface 1/1/4
          no lag 11

Preconditions:
Must have run the configure_l2_l3_lags workflow or have the equivalent settings.
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
from src import session, system, vlan, lag

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

        # Delete L2 LAGs:
        for l2_lag_data in data['l2_lags']:
            # Delete VLANs
            for vlan_id in l2_lag_data['trunk_vlans']:
                vlan.delete_vlan(vlan_id, **session_dict)

            # Remove the L2 ports from the LAG and delete the LAG
            lag.delete_lag_interface(l2_lag_data.get('name'), l2_lag_data.get('interfaces'), **session_dict)

        # Delete L3 LAGs:
        for l3_lag_data in data['l3_lags']:
            # Remove the L2 ports from the LAG and delete the LAG
            lag.delete_lag_interface(l3_lag_data.get('name'), l3_lag_data.get('interfaces'), **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
