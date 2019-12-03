#!/usr/bin/env python3
"""
This workflow pulls data from the sampledata/access_security_data.yaml file.
This workflow performs the following steps:

1. Configure the RADIUS server host
    Ex:
      radius-server host 10.10.10.10 key plaintext test1

2. Enable 802.1x globally
    Ex:
      aaa authentication port-access dot1x authenticator
        enable

3. Enable 802.1x on an L2 interface
    a. Create L2 interface
    b. Configure 802.1x on the interface
    Ex:
      interface 1/1/2
        no shutdown
        no routing
        vlan access 1
        aaa authentication port-access dot1x authenticator
            cached-reauth
            cached-reauth-period 3600
            eapol-timeout 30
            max-eapol-requests 2
            max-retries 3
            quiet-period 70
            reauth
            reauth-period 600
            discovery-period 40
            enable

4. Enable MAC authentication globally
    Ex:
      aaa authentication port-access mac-auth
        enable

5. Enable MAC authentication on an L2 interface
    a. Create L2 interface
    b. Configure MAC authentication on the interface
    Ex:
      interface 1/1/3
        no shutdown
        no routing
        vlan access 1
        aaa authentication port-access mac-auth
            cached-reauth
            cached-reauth-period 3600
            quiet-period 0
            reauth
            reauth-period 600
            enable

6. Enable port security globally
    Ex:
      port-access port-security enable

7. Set a reserved VLAN for tunneled clients
    a.  Create a VLAN
    b. Set it as the reserved VLAN for tunneled clients
    Ex:
      vlan 1000
        name vlan1000
      ubt-client-vlan 1000

8. Create a User-Based-Tunneling (UBT) zone
    Ex:
      ubt zone default vrf default
        primary-controller ip 10.10.10.148
        sac-heartbeat-interval 1
        uac-keepalive-interval 60
        enable

9. Create a port access role
    Ex:
      port-access role role-1
        gateway-zone zone default gateway-role sunitha
        vlan access 111

10. Create a client port for tunneled clients
    a. Create L2 interface
    b. Enable MAC authentication on the interface
    c. Set limit on allowable authorized clients on the interface
    Ex:
      interface 1/1/24
        no shutdown
        no routing
        vlan access 1
        aaa authentication port-access client-limit 256
        aaa authentication port-access mac-auth
            enable

11. Set the source IP address for UBT
    Ex:
      ip source-interface ubt 10.10.10.87

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

            # Configure RADIUS server host
            access_security.create_radius_host_config(data['radius_server_host']['vrf'],
                                                      data['radius_server_host']['hostname'],
                                                      passkey=data['radius_server_host']['passkey'], **session_dict)

            # Enable 802.1x globally
            access_security.enable_disable_dot1x_globally(enable=True, **session_dict)

            # Create L2 interface
            interface.add_l2_interface(data['802.1x']['port'], **session_dict)

            # Configure 802.1x on the L2 interface
            access_security.configure_dot1x_interface(data['802.1x']['port'], auth_enable=data['802.1x']['auth_enable'],
                                                      cached_reauth_enable=data['802.1x']['cached_reauth_enable'],
                                                      cached_reauth_period=data['802.1x']['cached_reauth_period'],
                                                      discovery_period=data['802.1x']['discovery_period'],
                                                      eapol_timeout=data['802.1x']['eapol_timeout'],
                                                      max_requests=data['802.1x']['max_requests'],
                                                      max_retries=data['802.1x']['max_retries'],
                                                      quiet_period=data['802.1x']['quiet_period'],
                                                      reauth_enable=data['802.1x']['reauth_enable'],
                                                      reauth_period=data['802.1x']['reauth_period'], **session_dict)

            # Enable MAC authentication globally
            access_security.enable_disable_mac_auth_globally(enable=True, **session_dict)

            # Create L2 interface
            interface.add_l2_interface(data['mac_auth']['port'], **session_dict)

            # Configure MAC authentication on the L2 interface
            access_security.configure_mac_auth_interface(data['mac_auth']['port'], auth_enable=data['mac_auth']['auth_enable'],
                                                         cached_reauth_enable=data['mac_auth']['cached_reauth_enable'],
                                                         cached_reauth_period=data['mac_auth']['cached_reauth_period'],
                                                         quiet_period=data['mac_auth']['quiet_period'],
                                                         reauth_enable=data['mac_auth']['reauth_enable'],
                                                         reauth_period=data['mac_auth']['reauth_period'], **session_dict)

            # Enable port security globally
            access_security.enable_disable_port_security_globally(enable=True, **session_dict)

            # Create reserved VLAN for tunneled clients
            vlan.create_vlan(data['vlan']['id'], data['vlan']['name'], **session_dict)

            # Set reserved VLAN for tunneled clients
            access_security.set_ubt_client_vlan(data['vlan']['id'], **session_dict)

            # Create user-based-tunneling (UBT) zone
            access_security.create_ubt_zone(data['zone']['name'], data['zone']['vrf_name'],
                                            enable=data['zone']['enable'],
                                            pri_ctrlr_ip_addr=data['zone']['pri_ctrlr_ip_addr'],
                                            sac_heartbeat_interval=data['zone']['sac_heartbeat_interval'],
                                            uac_keepalive_interval=data['zone']['uac_keepalive_interval'],
                                            **session_dict)

            # Create port access role
            access_security.create_port_access_role(data['role']['name'], gateway_zone=data['role']['gateway_zone'],
                                                    ubt_gateway_role=data['role']['ubt_gateway_role'],
                                                    vlan_mode=data['role']['vlan_mode'],
                                                    vlan_tag=data['role']['vlan_tag'], **session_dict)

            # Create L2 interface
            interface.add_l2_interface(data['client_port']['port'], **session_dict)

            # Enable MAC authentication on client port
            access_security.configure_mac_auth_interface(data['client_port']['port'],
                                                         auth_enable=data['client_port']['auth_enable'],
                                                         reauth_enable=data['client_port']['reauth_enable'],
                                                         cached_reauth_enable=data['client_port']['cached_reauth_enable'],
                                                         **session_dict)

            # Set maximum limit of allowable authorized clients on the client port
            access_security.set_port_access_clients_limit(data['client_port']['port'],
                                                          data['client_port']['clients_limit'], **session_dict)

            # Set source IP address for UBT
            access_security.set_source_ip_ubt(data['ubt_source_ip']['vrf_name'], data['ubt_source_ip']['ip_addr'],
                                              **session_dict)

        else:
            print("This workflow only applies to access platforms!")

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
