#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/vsx_data.yaml file.
This workflow performs the following steps:
1. Remove VSX Settings from Primary switch
    a. Delete VLAN VSX configuration
    b. Delete VSX Settings
    c. Delete VLANs
    d. Delete LAGs and Interfaces
   Ex:
    no interface vlan100
    no vsx
    no vlan 77
    no vlan 88
    no int lag 20
    no int lag 33
    interface 1/1/46
        shutdown
    interface 1/1/47
        shutdown
    interface 1/1/48
        shutdown
        no ip address 192.168.6.1/24

2. Remove VSX Settings from Secondary switch
    a. Delete VLAN VSX configuration
    b. Delete VSX Settings
    c. Delete VLANs
    d. Delete LAGs and Interfaces
   Ex:
    no interface vlan100
    no vsx
    no vlan 77
    no vlan 88
    no int lag 20
    no int lag 33
    interface 1/1/46
        shutdown
    interface 1/1/47
        shutdown
    interface 1/1/48
        shutdown
        no ip address 192.168.6.1/24


Preconditions:
Must run configure_vsx workflow prior, or have equivalent settings on the device
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
        data['version'] = "v1"

    # Clear VSX settings on Primary
    base_url_1 = "https://{0}/rest/{1}/".format(data['primarymgmtip'], data['version'])
    try:
        session_dict_1 = dict(s=session.login(base_url_1, data['primaryusername'], data['primarypassword']),
                              url=base_url_1)

        # Delete VSX settings from VLANs
        vsx.delete_vsx_interface_vlan(data['vlanid'], **session_dict_1)

        # Delete VSX Instance
        vsx.delete_vsx(**session_dict_1)

        # Delete VLANs
        vlan.delete_vlan_and_svi(data['vlanid'], data['vlanportname'], **session_dict_1)
        for islvlans in data['islvlans']:
            vlan.delete_vlan_and_svi(islvlans, 'vlan%s' % islvlans, **session_dict_1)

        # Delete Lag
        lag.delete_lag_interface(data['islport'], data['peer1isllaginterfaces'], **session_dict_1)
        lag.delete_lag_interface(data['mclagport'], data['peer1mclaginterfaces'], **session_dict_1)

        # Disable and initialize Interfaces
        for link in data['peer1isllaginterfaces']:
            interface.enable_disable_interface(link, state="down", **session_dict_1)
            interface.initialize_interface(link, **session_dict_1)
        for mclink in data['peer1mclaginterfaces']:
            interface.enable_disable_interface(mclink, state="down", **session_dict_1)
            interface.initialize_interface(mclink, **session_dict_1)
        interface.initialize_interface(data['primarykeepaliveinterface'], **session_dict_1)

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

        # Delete VSX settings from VLANs
        vsx.delete_vsx_interface_vlan(data['vlanid'], **session_dict_2)

        # Delete VSX Instance
        vsx.delete_vsx(**session_dict_2)

        # Delete VLANs
        vlan.delete_vlan_and_svi(data['vlanid'], data['vlanportname'], **session_dict_2)
        for islvlans in data['islvlans']:
            vlan.delete_vlan_and_svi(islvlans, 'vlan%s' % islvlans, **session_dict_2)

        # Delete Lag
        lag.delete_lag_interface(data['islport'], data['peer2isllaginterfaces'], **session_dict_2)
        lag.delete_lag_interface(data['mclagport'], data['peer2mclaginterfaces'], **session_dict_2)

        # Disable and initialize Interfaces
        for link in data['peer2isllaginterfaces']:
            interface.enable_disable_interface(link, state="down", **session_dict_2)
            interface.initialize_interface(link, **session_dict_2)
        for mclink in data['peer2mclaginterfaces']:
            interface.enable_disable_interface(mclink, state="down", **session_dict_2)
            interface.initialize_interface(mclink, **session_dict_2)
        interface.initialize_interface(data['secondarykeepaliveinterface'], **session_dict_2)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))

    session.logout(**session_dict_2)

if __name__ == '__main__':
    main()
