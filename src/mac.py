from src import common_ops


def get_all_mac_addrs(vlan_id, **kwargs):
    """
    Perform a GET call to get MAC address(es) for VLAN

    :param vlan_id: Numeric ID of VLAN
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: List of MAC address URIs
    """
    target_url = kwargs["url"] + "system/vlans/%d/macs" % vlan_id

    response = kwargs["s"].get(target_url, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting MAC address(es) of VLAN ID '%d' failed with status code %d"
              % (vlan_id, response.status_code))
    else:
        print("SUCCESS: Getting MAC address(es) of VLAN ID '%d' succeeded" % vlan_id)

    mac_data = response.json()
    return mac_data


def get_mac_info(vlan_id, mac_type, mac_addr, **kwargs):
    """
    Perform a GET call to get MAC info

    :param vlan_id: Numeric ID of VLAN
    :param mac_type: The source of the MAC address. Must be "dynamic," "VSX," "static," "VRRP,"
        "port-access-security," "evpn," or "hsc"
    :param mac_addr: MAC address
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Dictionary containing MAC data
    """
    target_url = kwargs["url"] + "system/vlans/%d/macs/%s/%s" % (vlan_id, mac_type, mac_addr)

    response = kwargs["s"].get(target_url, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting data for MAC '%s' of VLAN ID '%d' failed with status code %d"
              % (mac_addr, vlan_id, response.status_code))
    else:
        print("SUCCESS: Getting data for MAC '%s' of VLAN ID '%d' succeeded" % (mac_addr, vlan_id))

    mac_data = response.json()
    return mac_data
