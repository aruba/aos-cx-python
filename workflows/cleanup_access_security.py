#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/access_security_data.yaml file.
This workflow performs the following steps:

1. Unconfigure the RADIUS server host
    Ex:
      no radius-server host 10.10.10.10

2. Disable 802.1x globally
    Ex:
      no aaa authentication port-access dot1x authenticator

3. Remove 802.1x from the L2 interface
    a. Remove 802.1x from the L2 interface
    b. Initialize the L2 interface
    Ex:
      interface 1/1/2
        no shutdown
        no routing
        vlan access 1
        no aaa authentication port-access dot1x authenticator


4. Disable MAC authentication globally
    Ex:
      no aaa authentication port-access mac-auth

5. Remove MAC authentication from the L2 interface
    a. Remove MAC authentication from the L2 interface
    b. Initialize the L2 interface
    Ex:
      interface 1/1/3
        no shutdown
        no routing
        vlan access 1
        no aaa authentication port-access mac-auth

6. Disable port security globally
    Ex:
      port-access port-security disable

7. Remove reserved VLAN for tunneled clients
    a. Clear the reserved VLAN value for tunneled clients
    b. Remove the VLAN
    Ex:
      no vlan 1000
      no ubt-client-vlan 1000

8. Delete the User-Based-Tunneling (UBT) zone
    Ex:
      no ubt zone default vrf default

9. Remove the port access role
    Ex:
      no port-access role role-1

10. Remove the client port for tunneled clients
    a. Remove MAC authentication from the L2 interface
    b. Remove limit on allowable authorized clients on the interface
    c. Initialize the interface
    Ex:
      interface 1/1/2
        no shutdown
        no routing
        vlan access 1
        no aaa authentication port-access client-limit
        no aaa authentication port-access mac-auth

11. Remove the source IP address for UBT
    Ex:
      no ip source-interface ubt 10.10.10.87

Preconditions:
Must have run the configure_access_security workflow or have the equivalent settings.

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
from src import access_security
from src import system
from src import interface
from src import vlan

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    data = yaml_ops.read_yaml("access_security_data.yaml")

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

        # Only execute workflow if the platform is in the 6xxx series
        if platform_name.startswith("6"):

            # Unconfigure RADIUS server host
            access_security.delete_radius_host_config(data['radius_server_host']['vrf'],
                                                      data['radius_server_host']['hostname'],
                                                      passkey=data['radius_server_host']['passkey'], **session_dict)

            # Disable 802.1x globally
            access_security.enable_disable_dot1x_globally(enable=False, **session_dict)

            # Remove 802.1x from the L2 interface
            access_security.remove_auth_method_interface(data['802.1x']['port'], "802.1x", **session_dict)

            # Initialize L2 interface
            interface.initialize_interface(data['802.1x']['port'], **session_dict)

            # Disable MAC authentication globally
            access_security.enable_disable_mac_auth_globally(enable=False, **session_dict)

            # Remove MAC authentication from the L2 interface
            access_security.remove_auth_method_interface(data['mac_auth']['port'], "mac-auth", **session_dict)

            # Initialize L2 interface
            interface.initialize_interface(data['mac_auth']['port'], **session_dict)

            # Disable port security globally
            access_security.enable_disable_port_security_globally(enable=False, **session_dict)

            # Clear reserved VLAN value for tunneled clients
            access_security.clear_ubt_client_vlan(**session_dict)

            # Delete reserved VLAN for tunneled clients
            vlan.delete_vlan(data['vlan']['id'], **session_dict)

            # Delete user-based-tunneling (UBT) zone
            access_security.remove_ubt_zone(data['zone']['vrf_name'], **session_dict)

            # Remove port access role
            access_security.remove_port_access_role(data['role']['name'], **session_dict)

            # Remove MAC authentication from the client port
            access_security.remove_auth_method_interface(data['client_port']['port'], "mac-auth", **session_dict)

            # Clear limit of maximum allowable authorized clients on the client port
            access_security.clear_port_access_clients_limit(data['client_port']['port'], **session_dict)

            # Initialize L2 interface
            interface.initialize_interface(data['client_port']['port'], **session_dict)

            # Remove source IP address for UBT
            access_security.remove_source_ip_ubt(data['ubt_source_ip']['vrf_name'], **session_dict)

        else:
            print("This workflow only applies to access platforms!")

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
