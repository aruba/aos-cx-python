#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/loop_protect_data.yaml file.
This workflow performs the following steps:
1. Create the interfaces and VLANs
    a. Create L2 system interface
    b. Create L2 LAG interface
    c. Create multiple VLANs
   Ex:
    vlan 998
        name vlan998
    vlan 999
        name vlan999
    interface lag 99
        no shutdown
        no routing
        vlan trunk native 1
        vlan trunk allowed 998-999
    interface 1/1/3
        no shutdown
        no routing
        vlan trunk native 1
        vlan trunk allowed 998-999
    interface 1/1/4
        no shutdown
        lag 99
    interface 1/1/5
        no shutdown
        lag 99

2. Enable Loop-protect on the interfaces and VLANs
    a. Enable on L2 system interface
        i. Enable Loop-protect for a list of VLANs
    b. Enable on L2 LAG interface
   Ex:
    interface lag 99
        loop-protect
        loop-protect vlan 998-999
    interface 1/1/3
        loop-protect
        loop-protect vlan 998-999

3. Assign actions for Loop-protect
    a. Assign action for do-not-disable on interface
    b. Assign action for tx-disable on LAG
   Ex:
    interface lag 99
        loop-protect action tx-rx-disable
    interface 1/1/3
        loop-protect action do-not-disable


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

        # Create VLANs and L2 LAG; assign VLANs as trunk VLANs on LAG
        for l2_lag_data in data['lags']:
            # Create VLANs
            for vlan_id in l2_lag_data['trunk_vlans']:
                vlan.create_vlan(vlan_id, "vlan%s" % vlan_id, **session_dict)

            # Create L2 LAG and assign VLANs as trunk VLANs on the LAG
            lag.create_l2_lag_interface(data['lags'][0]['name'], data['lags'][0]['interfaces'],
                                        vlan_ids_list=data['lags'][0]['trunk_vlans'],
                                        lacp_mode=data['lags'][0]['lacp_mode'], mc_lag=data['lags'][0]['mc_lag'],
                                        **session_dict)

        # Add a new entry to the Port table if it doesn't yet exist
        interface.add_l2_interface(data['interfacename'], **session_dict)
        vlan.port_add_vlan_trunks(data['interfacename'], data['lags'][0]['trunk_vlans'], **session_dict)

        # Update the Interface table entry with "user-config": {"admin": "up"}
        interface.enable_disable_interface(data['interfacename'], **session_dict)

        # Enable Loop-protect on Interface
        loop_protect.update_port_loop_protect(data['interfacename'], action=None, vlan_list=[], **session_dict)

        # Enable Loop-protect for specific VLANs on Interface
        loop_protect.update_port_loop_protect(data['interfacename'], action=None,
                                              vlan_list=data['lags'][0]['trunk_vlans'], **session_dict)

        # Enable Loop-protect on LAG
        loop_protect.update_port_loop_protect(data['lags'][0]['name'], action=None, vlan_list=[], **session_dict)

        # Enable Loop-protect for specific VLANs on LAG
        loop_protect.update_port_loop_protect(data['lags'][0]['name'],
                                              action=None, vlan_list=data['lags'][0]['trunk_vlans'], **session_dict)

        # Update Loop-protect Actions on Interface
        loop_protect.update_port_loop_protect(data['interfacename'], action=data['interfaceaction'],
                                              vlan_list=None, **session_dict)

        # Update Loop-protect Actions on LAG
        loop_protect.update_port_loop_protect(l2_lag_data.get('name'), action=data['lagaction'],
                                              vlan_list=[], **session_dict)


    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
