import json
import random

from src import common_ops, port


def get_interface(int_name, depth=0, selector=None, **kwargs):
    """
    Perform a GET call to retrieve data for an Interface table entry

    :param int_name: Alphanumeric name of the interface
    :param depth: Integer deciding how many levels into the API JSON that references will be returned.
    :param selector: Alphanumeric option to select specific information to return.  The options are 'configuration',
        'status', or 'statistics'.  If running v10.04 or later, an additional option 'writable' is included.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Dictionary containing data for Interface entry
    """
    if kwargs["url"].endswith("/v1/"):
        return _get_interface_v1(int_name, depth, selector, **kwargs)
    else:   # Updated else for when version is v10.04
        return _get_interface(int_name, depth, selector, **kwargs)


def _get_interface_v1(int_name, depth=0, selector=None, **kwargs):
    """
    Perform a GET call to retrieve data for an Interface table entry

    :param int_name: Alphanumeric name of the interface
    :param depth: Integer deciding how many levels into the API JSON that references will be returned.
    :param selector: Alphanumeric option to select specific information to return.  The options are 'configuration',
        'status', or 'statistics'.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Dictionary containing data for Interface entry
    """
    int_name_percents = common_ops._replace_special_characters(int_name)

    if selector not in ['configuration', 'status', 'statistics', None]:
        raise Exception("ERROR: Selector should be 'configuration', 'status', or 'statistics'")

    target_url = kwargs["url"] + "system/interfaces/%s?" % int_name_percents
    payload = {
        "depth": depth,
        "selector": selector
    }
    response = kwargs["s"].get(target_url, verify=False, params=payload, timeout=3)

    result = []
    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting Interface table entry '%s' failed with status code %d"
              % (int_name, response.status_code))
    else:
        print("SUCCESS: Getting Interface table entry '%s' succeeded" % int_name)
        result = response.json()
    return result


def _get_interface(int_name, depth=0, selector=None, **kwargs):
    """
    Perform a GET call to retrieve data for an Interface table entry

    :param int_name: Alphanumeric name of the interface
    :param depth: Integer deciding how many levels into the API JSON that references will be returned.
    :param selector: Alphanumeric option to select specific information to return.  The options are 'configuration',
        'status', 'statistics' or 'writable'.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Dictionary containing data for Interface entry
    """
    int_name_percents = common_ops._replace_special_characters(int_name)

    if selector not in ['configuration', 'status', 'statistics', 'writable', None]:
        raise Exception("ERROR: Selector should be 'configuration', 'status', 'statistics', or 'writable'")

    target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
    payload = {
        "depth": depth,
        "selector": selector
    }
    response = kwargs["s"].get(target_url, verify=False, params=payload, timeout=3)
    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting Interface table entry '%s' failed with status code %d"
              % (int_name, response.status_code))
        result = {}
    else:
        print("SUCCESS: Getting Interface table entry '%s' succeeded" % int_name)
        result = response.json()

    return result


def get_all_interfaces(**kwargs):
    """
    Perform a GET call to get a list (or dictionary) of all entries in the Interface table

    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: List/dict of all Interfaces in the table
    """
    target_url = kwargs["url"] + "system/interfaces"

    response = kwargs["s"].get(target_url, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting list/dict of all Interface table entries failed with status code %d"
              % response.status_code)
        interface_list = []
    else:
        print("SUCCESS: Getting list/dict of all Interface table entries succeeded")
        interface_list = response.json()

    return interface_list


def get_ipv6_addresses(int_name, depth=0, **kwargs):
    """
    Perform a GET call to retrieve the list of IPv6 addresses for an Interface table entry

    :param int_name: Alphanumeric name of the interface
    :param depth: Integer deciding how many levels into the API JSON that references will be returned.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: List of all ipv6 addresses for the Interface entry
    """
    int_name_percents = common_ops._replace_special_characters(int_name)

    if kwargs["url"].endswith("/v1/"):
        target_url = kwargs["url"] + "system/ports/%s/ip6_addresses" % int_name_percents
        logport = "Port"
    else:  # Updated else for when version is v10.04
        target_url = kwargs["url"] + "system/interfaces/%s/ip6_addresses" % int_name_percents
        logport = "Interface"

    payload = {
        "depth": depth
    }
    response = kwargs["s"].get(target_url, verify=False, params=payload, timeout=3)
    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting IPv6 list for %s table entry '%s' failed with status code %d"
              % (logport, int_name, response.status_code))
        result = []
    else:
        print("SUCCESS: Getting IPv6 list for %s table entry '%s' succeeded" % (logport, int_name))
        result = response.json()

    return result


def add_vlan_interface(vlan_int_name, vlan_port_name, vlan_id, ipv4, vrf_name, vlan_port_desc, int_type="vlan",
                       user_config=None, **kwargs):
    """
    Perform a POST call to add Interface table entry for a VLAN.

    :param vlan_int_name: Alphanumeric name for the VLAN interface
    :param vlan_port_name: Alphanumeric Port name to associate with the interface
    :param vlan_id: Numeric ID of VLAN
    :param ipv4: Optional IPv4 address to assign to the interface. Defaults to nothing if not specified.
    :param vrf_name: VRF to attach the SVI to. Defaults to "default" if not specified
    :param vlan_port_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param int_type: Type of interface; generally should be "vlan" for SVI's.
    As such, defaults to "internal" if not specified.
    :param user_config: User configuration to apply to interface. Defaults to {"admin": "up"} if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _add_vlan_interface_v1(vlan_int_name, vlan_port_name, int_type, user_config, **kwargs)
    else:  # Updated else for when version is v10.04
        _add_vlan_interface(vlan_int_name, vlan_id, ipv4, vrf_name, vlan_port_desc, int_type, user_config, **kwargs)


def _add_vlan_interface_v1(vlan_int_name, vlan_port_name, int_type="vlan", user_config=None, **kwargs):
    """
    Perform a POST call to add Interface table entry for a VLAN.

    :param vlan_int_name: Alphanumeric name for the VLAN interface
    :param vlan_port_name: Alphanumeric Port name to associate with the interface
    :param int_type: Type of interface; generally should be "vlan" for SVI's.
    As such, defaults to "internal" if not specified.
    :param user_config: User configuration to apply to interface. Defaults to {"admin": "up"} if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ints_list = get_all_interfaces(**kwargs)

    if "/rest/v1/system/interfaces/%s" % vlan_int_name not in ints_list:
        if user_config is None:
            # optional argument can't default to a dictionary type,
            # so make it None and change it to the dictionary {"admin": "up"} if it was None
            user_config = {"admin": "up"}

        vlan_int_data = {"name": vlan_int_name,
                         "referenced_by": "/rest/v1/system/ports/%s" % vlan_port_name,
                         "type": int_type,  # API says: "vlan: generally represents SVI - L3 VLAN interfaces."
                         "user_config": user_config
                         }

        target_url = kwargs["url"] + "system/interfaces"

        post_data = json.dumps(vlan_int_data, sort_keys=True, indent=4)

        response = kwargs["s"].post(target_url, data=post_data, verify=False)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Adding Interface table entry '%s' for SVI failed with status code %d"
                  % (vlan_int_name, response.status_code))
        else:
            print("SUCCESS: Adding Interface table entry '%s' for SVI succeeded" % vlan_int_name)
    else:
        print("SUCCESS: No need to create Interface table entry '%s' for SVI since it already exists"
              % vlan_int_name)


def _add_vlan_interface(vlan_int_name, vlan_id=None, ipv4=None, vrf_name="default", vlan_port_desc=None,
                        int_type="vlan", user_config=None, **kwargs):
    """
    Perform a POST call to add Interface table entry for a VLAN.

    :param vlan_int_name: Alphanumeric name for the VLAN interface
    :param vlan_port_name: Alphanumeric Port name to associate with the interface
    :param int_type: Type of interface; generally should be "vlan" for SVI's.
    As such, defaults to "internal" if not specified.
    :param user_config: User configuration to apply to interface. Defaults to {"admin": "up"} if not speicifed.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ints_dict = get_all_interfaces(**kwargs)

    if vlan_int_name not in ints_dict:
        if user_config is None:
            # optional argument can't default to a dictionary type,
            # so make it None and change it to the dictionary {"admin": "up"} if it was None
            user_config = {"admin": "up"}

        vlan_int_data = {"name": vlan_int_name,
                         "type": int_type,  # API says: "vlan: generally represents SVI - L3 VLAN interfaces."
                         "user_config": user_config,
                         "vrf": "/rest/v10.04/system/vrfs/%s" % vrf_name,
                         "vlan_tag": "/rest/v10.04/system/vlans/%s" % vlan_id
                         }

        if vlan_port_desc is not None:
            vlan_int_data['description'] = vlan_port_desc

        if ipv4 is not None:
            vlan_int_data['ip4_address'] = ipv4

        target_url = kwargs["url"] + "system/interfaces"

        post_data = json.dumps(vlan_int_data, sort_keys=True, indent=4)

        response = kwargs["s"].post(target_url, data=post_data, verify=False)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Adding Interface table entry '%s' for SVI failed with status code %d"
                  % (vlan_int_name, response.status_code))
        else:
            print("SUCCESS: Adding Interface table entry '%s' for SVI succeeded" % vlan_int_name)
    else:
        print("SUCCESS: No need to create Interface table entry '%s' for SVI since it already exists"
              % vlan_int_name)


def add_l2_interface(interface_name, interface_desc=None, interface_admin_state="up", **kwargs):
    """
    Perform a POST call to create an Interface table entry for physical L2 interface.

    :param interface_name: Alphanumeric Interface name
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param interface_admin_state: Optional administratively-configured state of the interface.
        Defaults to "up" if not specified
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        port.add_l2_port(interface_name, interface_desc, interface_admin_state, **kwargs)
    else:   # Updated else for when version is v10.04
        _add_l2_interface(interface_name, interface_desc, interface_admin_state, **kwargs)


def _add_l2_interface(interface_name, interface_desc=None, interface_admin_state="up", **kwargs):
    """
    Perform a PUT call to create an Interface table entry for physical L2 interface.
    :param interface_name: Alphanumeric Interface name
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param interface_admin_state: Optional administratively-configured state of the interface.
        Defaults to "up" if not specified
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)

    interface_data = {
        "admin": "up",
        "description": interface_desc,
        "routing": False,
        "user_config": {
            "admin": interface_admin_state
        },
    }

    target_url = kwargs["url"] + "system/interfaces/" + interface_name_percents
    post_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=post_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Adding Interface table entry '%s' failed with status code %d"
              % (interface_name, response.status_code))
    else:
        print("SUCCESS: Adding Interface table entry '%s' succeeded" % interface_name)


def add_l3_ipv4_interface(interface_name, ip_address=None, interface_desc=None, interface_admin_state="up",
                          vrf="default", **kwargs):
    """
    Perform a PUT or POST call to create an Interface table entry for a physical L3 Interface. If the Interface already
    exists, the function will enable routing on the Interface and update the IPv4 address if given.

    :param interface_name: Alphanumeric Interface name
    :param ip_address: IPv4 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param interface_admin_state: Optional administratively-configured state of the interface.
        Defaults to "up" if not specified
    :param vrf: Name of the VRF to which the Port belongs. Defaults to "default" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _add_l3_ipv4_interface_v1(interface_name, ip_address, interface_desc, interface_admin_state, vrf, **kwargs)
    else:   # Updated else for when version is v10.04
        _add_l3_ipv4_interface(interface_name, ip_address, interface_desc, interface_admin_state, vrf, **kwargs)


def _add_l3_ipv4_interface_v1(interface_name, ip_address=None, interface_desc=None, interface_admin_state="up",
                              vrf="default", **kwargs):
    """
    Perform a PUT or POST call to create an Interface table entry for a physical L3 Interface. If the Interface already
    exists, the function will enable routing on the Interface and update the IPv4 address if given.

    :param interface_name: Alphanumeric Interface name
    :param ip_address: IPv4 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param interface_admin_state: Optional administratively-configured state of the interface.
        Defaults to "up" if not specified
    :param vrf: Name of the VRF to which the Port belongs. Defaults to "default" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    port.add_l3_ipv4_port(interface_name, ip_address, interface_desc, interface_admin_state, vrf, **kwargs)


def _add_l3_ipv4_interface(interface_name, ip_address=None, interface_desc=None, interface_admin_state="up",
                           vrf="default", **kwargs):
    """
    Perform a PUT call to update an Interface table entry for a physical L3 Interface. If the Interface already
    exists, the function will enable routing on the Interface and update the IPv4 address if given.

    :param interface_name: Alphanumeric Interface name
    :param ip_address: IPv4 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param interface_admin_state: Optional administratively-configured state of the interface.
        Defaults to "up" if not specified
    :param vrf: Name of the VRF to which the Port belongs. Defaults to "default" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)

    interface_data = {
        "admin": interface_admin_state,
        "interfaces": ["/rest/v10.04/system/interfaces/%s" % interface_name_percents],
        "routing": True,
        "ip4_address": ip_address,
        "vrf": {vrf: "/rest/v10.04/system/vrfs/%s" % vrf}
    }

    if interface_desc is not None:
        interface_data['description'] = interface_desc

    target_url = kwargs["url"] + "system/interfaces/" + interface_name_percents
    put_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Adding Interface table entry '%s' failed with status code %d"
              % (interface_name, response.status_code))
    else:
        print("SUCCESS: Configuring Interface table entry '%s' succeeded" % interface_name)


def add_l3_ipv6_interface(interface_name, ip_address=None, interface_desc=None, interface_admin_state="up",
                          vrf="default", **kwargs):
    """
    Perform a PUT or POST call to create an Interface table entry for a physical L3 Interface. If the Interface already
    exists, the function will enable routing on the Interface and update the IPv6 address if given.

    :param interface_name: Alphanumeric Interface name
    :param ip_address: IPv6 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param interface_admin_state: Optional administratively-configured state of the interface.
        Defaults to "up" if not specified
    :param vrf: Name of the VRF to which the Port belongs. Defaults to "default" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _add_l3_ipv6_interface_v1(interface_name, ip_address, interface_desc, interface_admin_state, vrf, **kwargs)
    else:   # Updated else for when version is v10.04
        _add_l3_ipv6_interface(interface_name, ip_address, interface_desc, interface_admin_state, vrf, **kwargs)


def _add_l3_ipv6_interface_v1(interface_name, ip_address=None, interface_desc=None, interface_admin_state="up",
                              vrf="default", **kwargs):
    """
    Perform a PUT or POST call to create an Interface table entry for a physical L3 Interface. If the Interface already
    exists, the function will enable routing on the Interface and update the IPv6 address if given.

    :param interface_name: Alphanumeric Interface name
    :param ip_address: IPv6 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param interface_admin_state: Optional administratively-configured state of the interface.
        Defaults to "up" if not specified
    :param vrf: Name of the VRF to which the Port belongs. Defaults to "default" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    port.add_l3_ipv6_port(interface_name, ip_address, interface_desc, interface_admin_state, vrf, **kwargs)


def _add_l3_ipv6_interface(interface_name, ip_address=None, interface_desc=None, interface_admin_state="up",
                           vrf="default", **kwargs):
    """
    Perform a PUT call to update an Interface table entry for a physical L3 Interface, then a POST call to add an IPv6
    mapping. If the Interface already exists, the function will enable routing on the Interface and update the
    IPv6 address if given.

    :param interface_name: Alphanumeric Interface name
    :param ip_address: IPv6 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param interface_admin_state: Optional administratively-configured state of the interface.
        Defaults to "up" if not specified
    :param vrf: Name of the VRF to which the Port belongs. Defaults to "default" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)

    interface_data = {
        "admin": interface_admin_state,
        "interfaces": ["/rest/v10.04/system/interfaces/%s" % interface_name_percents],
        "routing": True,
        "vrf": {vrf: "/rest/v10.04/system/vrfs/%s" % vrf}
    }

    if interface_desc is not None:
        interface_data['description'] = interface_desc

    target_url = kwargs["url"] + "system/interfaces/" + interface_name_percents
    put_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Initial configuration of L3 IPv6 Interface table entry '%s' failed with status code %d"
              % (interface_name, response.status_code))
    else:
        print("SUCCESS: Initial configuration of L3 IPv6 Interface table entry '%s' succeeded" % interface_name)
        # IPv6 defaults
        ipv6_data = {
          "address": ip_address,
          "node_address": True,
          "origin": "configuration",
          "ra_prefix": True,
          "route_tag": 0,
          "type": "global-unicast"
        }

        target_url = kwargs["url"] + "system/interfaces/%s/ip6_addresses" % interface_name_percents
        post_data = json.dumps(ipv6_data, sort_keys=True, indent=4)

        response = kwargs["s"].post(target_url, data=post_data, verify=False)
        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Final configuration of L3 IPv6 Interface table entry '%s' failed with status code %d"
                  % (interface_name, response.status_code))
        else:
            print("SUCCESS: Final configuration of L3 IPv6 Interface table entry '%s' succeeded" % interface_name)


def delete_ipv6_address(interface_name, ip, **kwargs):
    """
    Perform a DELETE call to remove an IPv6 address from an Interface.

    :param interface_name: Alphanumeric Interface name
    :param ip: IPv6 address assigned to the interface that will be removed.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        port._delete_ipv6_address(interface_name, ip, **kwargs)
    else:   # Updated else for when version is v10.04
        _delete_ipv6_address(interface_name, ip, **kwargs)



def _delete_ipv6_address(interface_name, ip, **kwargs):
    """
    Perform a DELETE call to remove an IPv6 address from an Interface.

    :param interface_name: Alphanumeric Interface name
    :param ip: IPv6 address assigned to the interface that will be removed.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if ip in get_ipv6_addresses(interface_name, **kwargs):
        interface_name_percents = common_ops._replace_special_characters(interface_name)
        ip_address = common_ops._replace_special_characters(ip)
        target_url = kwargs["url"] + "system/interfaces/%s/ip6_addresses/%s" % (interface_name_percents, ip_address)

        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting IPv6 Address '%s' from Interface table entry '%s' failed with status code %d"
                  % (ip, interface_name, response.status_code))
        else:
            print("SUCCESS: Deleting IPv6 Address '%s' from Interface table entry '%s' succeeded"
                  % (ip, interface_name))
    else:
        print("SUCCESS: No need to delete IPv6 Address '%s' from Interface table entry '%s' since it does not exist"
              % (ip, interface_name))


def create_loopback_interface(interface_name, vrf="default", ipv4=None, interface_desc=None, **kwargs):
    """
    Perform a PUT and/or POST call to create a Loopback Interface table entry for a logical L3 Interface. If the
    Loopback Interface already exists and an IPv4 address is given, the function will update the IPv4 address.

    :param interface_name: Alphanumeric Interface name
    :param vrf: VRF to attach the SVI to. Defaults to "default" if not specified
    :param ipv4: IPv4 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _create_loopback_interface_v1(interface_name, vrf, ipv4, interface_desc, **kwargs)
    else:   # Updated else for when version is v10.04
        _create_loopback_interface(interface_name, vrf, ipv4, interface_desc, **kwargs)


def _create_loopback_interface_v1(interface_name, vrf, ipv4=None, interface_desc=None, **kwargs):
    """
    Perform a PUT and/or POST call to create a Loopback Interface table entry for a logical L3 Interface. If the
    Loopback Interface already exists and an IPv4 address is given, the function will update the IPv4 address.

    :param interface_name: Alphanumeric Interface name
    :param vrf: VRF to attach the SVI to. Defaults to "default" if not specified
    :param ipv4: IPv4 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    port.create_loopback_port(interface_name, vrf, ipv4, interface_desc, **kwargs)


def _create_loopback_interface(interface_name, vrf, ipv4=None, interface_desc=None, **kwargs):
    """
    Perform a PUT and/or POST call to create a Loopback Interface table entry for a logical L3 Interface. If the
    Loopback Interface already exists and an IPv4 address is given, the function will update the IPv4 address.

    :param interface_name: Alphanumeric Interface name
    :param vrf: VRF to attach the SVI to. Defaults to "default" if not specified
    :param ipv4: IPv4 address to assign to the interface. Defaults to nothing if not specified.
    :param interface_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)

    interface_data = {
        "name": interface_name,
        "referenced_by": "/rest/v1/system/ports/%s" % interface_name,
        "type": "loopback",
        "user_config": {
            "admin": "up"
        }
    }

    if interface_desc is not None:
        interface_data['description'] = interface_desc

    target_url = kwargs["url"] + "system/interfaces/" + interface_name_percents
    put_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Adding Interface table entry '%s' failed with status code %d"
              % (interface_name, response.status_code))
    else:
        print("SUCCESS: Configuring Interface table entry '%s' succeeded" % interface_name)


def _create_vxlan_interface(interface_name, source_ipv4=None, port_desc=None, dest_udp_port=4789, **kwargs):
    """
    Perform POST calls to create a VXLAN table entry for a logical L3 Interface. If the
    VXLAN Interface already exists and an IPv4 address is given, the function will update the IPv4 address.

    :param interface_name: Alphanumeric Interface name
    :param source_ipv4: Source IPv4 address to assign to the VXLAN interface. Defaults to nothing if not specified.
    :param port_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param dest_udp_port: Optional Destination UDP Port that the VXLAN will use.  Default is set to 4789
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interfaces_list = get_all_interfaces(**kwargs)

    if "/rest/v1/system/ports/%s" % interface_name not in interfaces_list:
        port_data = {
            "admin": "up",
            "interfaces": [],
            "name": interface_name,
            "routing": False
            }

        if port_desc is not None:
            port_data['description'] = port_desc

        port_url = kwargs["url"] + "system/ports"
        post_data = json.dumps(port_data, sort_keys=True, indent=4)

        response = kwargs["s"].post(port_url, data=post_data, verify=False)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Adding VXLAN Port table entry '%s' failed with status code %d"
                  % (interface_name, response.status_code))
        else:
            interface_data = {
                "name": interface_name,
                "options": {
                    "local_ip": source_ipv4,
                    "vxlan_dest_udp_port": str(dest_udp_port)
                },
                "type": "vxlan",
                "user_config": {
                    "admin": "up"
                }
            }
            interface_url = kwargs["url"] + "system/interfaces"
            post_data = json.dumps(interface_data, sort_keys=True, indent=4)

            response = kwargs["s"].post(interface_url, data=post_data, verify=False)

            if not common_ops._response_ok(response, "POST"):
                print("FAIL: Adding VXLAN Interface table entry '%s' failed with status code %d"
                      % (interface_name, response.status_code))
            else:
                print("SUCCESS: Adding VXLAN Port and Interface table entries '%s' succeeded" % interface_name)

    else:
        update_interface_ipv4(interface_name, source_ipv4, **kwargs)


def update_interface_ipv4(interface_name, ipv4, interface_admin_state, vrf, **kwargs):
    """
    Perform GET and PUT calls to update an L3 interface's ipv4 address

    :param interface_name: Alphanumeric name of the Port
    :param ipv4: IPv4 address to associate with the VLAN Port
    :param interface_admin_state: Administratively-configured state of the port.
    :param vrf: Name of the VRF to which the Port belongs.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)
    interface_data = get_interface(interface_name, depth=1, selector="writable", **kwargs)

    interface_data['ip4_address'] = ipv4
    interface_data['routing'] = True
    interface_data['admin'] = interface_admin_state
    interface_data['vrf'] = "/rest/v10.04/system/vrfs/%s" % vrf

    target_url = kwargs["url"] + "system/interfaces/%s" % interface_name_percents
    put_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Updating IPv4 addresses for Port '%s' to '%s' failed with status code %d"
              % (interface_name, repr(ipv4), response.status_code))
    else:
        print("SUCCESS: Updating IPv4 addresses for Port '%s' to '%s' succeeded"
              % (interface_name, repr(ipv4)))


def update_port_ipv6(interface_name, ipv6, addr_type="global-unicast", **kwargs):
    """
    Perform a POST call to update an L3 interface's ipv6 address

    :param interface_name: Alphanumeric name of the Port
    :param ipv6: IPv6 address to associate with the VLAN Port
    :param addr_type: Type of IPv6 address. Defaults to "global-unicast" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    ipv6_data = {"address": ipv6,
                 "type": addr_type}

    target_url = kwargs["url"] + "system/interfaces/%s/ip6_addresses" % interface_name
    post_data = json.dumps(ipv6_data, sort_keys=True, indent=4)

    response = kwargs["s"].post(target_url, data=post_data, verify=False)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Updating IPv6 address for Port '%s' to '%s' failed with status code %d"
              % (interface_name, ipv6, response.status_code))
    else:
        print("SUCCESS: Updating IPv6 address for Port '%s' to '%s' succeeded"
              % (interface_name, ipv6))


def enable_disable_interface(int_name, state="up", **kwargs):
    """
    Perform GET and PUT calls to either enable or disable the interface by setting Interface's admin_state to
        "up" or "down"

    :param int_name: Alphanumeric name of the interface
    :param state: State to set the interface to
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _enable_disable_interface_v1(int_name, state, **kwargs)
    else:  # Updated else for when version is v10.04
        _enable_disable_interface(int_name, state, **kwargs)


def _enable_disable_interface_v1(int_name, state="up", **kwargs):
    """
    Perform GET and PUT calls to either enable or disable the interface by setting Interface's admin_state to
        "up" or "down"

    :param int_name: Alphanumeric name of the interface
    :param state: State to set the interface to
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if state not in ['up', 'down']:
        raise Exception("Administratively-configured state of interface should be 'up' or 'down'")

    int_name_percents = common_ops._replace_special_characters(int_name)

    interface_list = get_all_interfaces(**kwargs)

    if "/rest/v1/system/interfaces/%s" % int_name_percents in interface_list:
        int_data = get_interface(int_name, 0, "configuration", **kwargs)
        int_data['user_config'] = {"admin": state}

        target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
        put_data = json.dumps(int_data, sort_keys=True, indent=4)

        response = kwargs["s"].put(target_url, data=put_data, verify=False)

        if not common_ops._response_ok(response, "PUT"):
            print("FAIL: Updating Interface '%s' with admin-configured state '%s' "
                  "failed with status code %d" % (int_name, state, response.status_code))
        else:
            print("SUCCESS: Updating Interface '%s' with admin-configured state '%s' "
                  "succeeded" % (int_name, state))
        port._enable_disable_port(int_name, state, **kwargs)

    else:
        print("Unable to update Interface '%s' because operation could not find interface" % int_name)


def _enable_disable_interface(int_name, state="up", **kwargs):
    """
    Perform GET and PUT calls to either enable or disable the interface by setting Interface's admin_state to
        "up" or "down"

    :param int_name: Alphanumeric name of the interface
    :param state: State to set the interface to
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if state not in ['up', 'down']:
        raise Exception("Administratively-configured state of interface should be 'up' or 'down'")

    int_name_percents = common_ops._replace_special_characters(int_name)

    int_data = get_interface(int_name, 1, "writable", **kwargs)
    int_data['user_config'] = {"admin": state}

    target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
    put_data = json.dumps(int_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Updating Interface '%s' with admin-configured state '%s' "
              "failed with status code %d" % (int_name, state, response.status_code))
    else:
        print("SUCCESS: Updating Interface '%s' with admin-configured state '%s' "
              "succeeded" % (int_name, state))


def delete_interface(interface_name, **kwargs):
    """
    Perform a DELETE call to either the Interface Table or Port Table to delete an interface

    :param interface_name: Name of interface's reference entry in Interface table
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _delete_interface_v1(interface_name, **kwargs)
    else:  # Updated else for when version is v10.04
        _delete_interface(interface_name, **kwargs)


def _delete_interface_v1(interface_name, **kwargs):
    """
    Perform DELETE call to Port Table to delete an interface

    Note: Interface API does not have delete methods.
    To delete an Interface, you remove its reference port.

    :param name: Name of interface's reference entry in Port table
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    port.delete_port(interface_name, **kwargs)


def _delete_interface(name, **kwargs):
    """
    Perform DELETE call to Interface table to delete an interface
    :param name: Name of interface
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ints_dict = get_all_interfaces(**kwargs)

    if name in ints_dict:

        target_url = kwargs["url"] + "system/interfaces/%s" % name

        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting Interface table entry '%s' failed with status code %d"
                  % (name, response.status_code))
        else:
            print("SUCCESS: Deleting Interface table entry '%s' succeeded" % name)
    else:
        print("SUCCESS: No need to delete Interface table entry '%s' because it doesn't exist"
              % name)


def delete_l2_interface(interface_name, **kwargs):
    """
    Perform either a PUT call to the Interface Table or DELETE call to Port Table to delete an interface
    If trying to re-initialize an L2 interface, use the function initialize_l2_interface()

    :param interface_name: Name of interface's reference entry in Interface table
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _delete_l2_interface_v1(interface_name, **kwargs)
    else:  # Updated else for when version is v10.04
        _delete_l2_interface(interface_name, **kwargs)


def _delete_l2_interface_v1(interface_name, **kwargs):
    """
    Perform DELETE call to Port Table to delete an L2 interface

    Note: Interface API does not have delete methods.
    To delete an Interface, you remove its reference port.

    :param name: Name of interface's reference entry in Port table
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    port.delete_port(interface_name, **kwargs)


def _delete_l2_interface(interface_name, **kwargs):
    """
    Perform a PUT call to the Interface Table to reset an interface to it's default values

    :param interface_name: Name of interface's reference entry in Interface table
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)
    target_url = kwargs["url"] + "system/interfaces/%s" % interface_name_percents

    interface_data = {}
    interface_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=interface_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Deleting Interface '%s' failed with status code %d" % (interface_name, response.status_code))
    else:
        print("SUCCESS: Deleting Interface '%s' succeeded" % interface_name)


def _port_set_vlan_mode(l2_port_name, vlan_mode, **kwargs):
    """
    Perform GET and PUT calls to set an L2 interface's VLAN mode (native-tagged, native-untagged, or access)

    :param l2_port_name: L2 interface's Interface table entry name
    :param vlan_mode: A string, either 'native-tagged', 'native-untagged', or 'access', specifying the desired VLAN
        mode
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if vlan_mode not in ['native-tagged', 'native-untagged', 'access']:
        raise Exception("ERROR: VLAN mode should be 'native-tagged', 'native-untagged', or 'access'")

    l2_port_name_percents = common_ops._replace_special_characters(l2_port_name)
    int_data = get_interface(l2_port_name_percents, depth=1, selector="writable", **kwargs)

    int_data['vlan_mode'] = vlan_mode
    int_data['routing'] = False

    target_url = kwargs["url"] + "system/interfaces/%s" % l2_port_name_percents
    put_data = json.dumps(int_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Setting port '%s' VLAN mode to '%s' failed with status code %d"
              % (l2_port_name, vlan_mode, response.status_code))
    else:
        print("SUCCESS: Setting port '%s' VLAN mode to '%s' succeeded" % (l2_port_name, vlan_mode))


def _port_set_untagged_vlan(l2_port_name, vlan_id, **kwargs):
    """
    Perform GET and PUT/POST calls to set a VLAN on an access port

    :param l2_port_name: L2 interface's Port table entry name
    :param vlan_id: Numeric ID of VLAN to set on access port
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    l2_port_name_percents = common_ops._replace_special_characters(l2_port_name)

    int_data = get_interface(l2_port_name_percents, depth=1, selector="writable", **kwargs)

    int_data['vlan_mode'] = "access"
    int_data['vlan_tag'] = "/rest/v10.04/system/vlans/%s" % vlan_id
    int_data['routing'] = False

    target_url = kwargs["url"] + "system/interfaces/%s" % l2_port_name_percents
    put_data = json.dumps(int_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not (common_ops._response_ok(response, "PUT") or common_ops._response_ok(response, "POST")):
        print("FAIL: Setting Port '%s' access VLAN to VLAN ID '%d' failed with status code %d"
              % (l2_port_name, vlan_id, response.status_code))
    else:
        print("SUCCESS: Setting Port '%s' access VLAN to VLAN ID '%d' succeeded"
              % (l2_port_name, vlan_id))


def _port_add_vlan_trunks(l2_port_name, vlan_trunk_ids={}, **kwargs):
    """
    Perform GET and PUT/POST calls to add specified VLANs to a trunk port. By default, this will also set the port to
    have 'no routing' and if there is not a native VLAN, will set the native VLAN to VLAN 1.

    :param l2_port_name: L2 interface's Port table entry name
    :param vlan_trunk_ids: Dictionary of VLANs to specify as allowed on the trunk port.  If empty, the interface will
        allow all VLANs on the trunk.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    l2_port_name_percents = common_ops._replace_special_characters(l2_port_name)

    trunk_list = {}
    for x in vlan_trunk_ids:
        x_keys = {str(x): "/rest/v10.04/system/vlans/%d" % x}
        trunk_list.update(x_keys)

    port_data = get_interface(l2_port_name, depth=1, selector="writable", **kwargs)

    if not port_data['vlan_tag']:
        port_data['vlan_tag'] = {"1": "/rest/v10.04/system/vlans/1"}
    if not port_data['vlan_mode']:
        port_data['vlan_mode'] = "native-untagged"
    port_data['routing'] = False

    if not trunk_list:
        port_data['vlan_trunks'] = []
    else:
        for key in trunk_list:
            if key not in port_data['vlan_trunks']:
                port_data['vlan_trunks'].append("/rest/v10.04/system/vlans/%s" % key)

    target_url = kwargs["url"] + "system/interfaces/%s" % l2_port_name_percents
    put_data = json.dumps(port_data, sort_keys=True, indent=4)
    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not (common_ops._response_ok(response, "PUT") or common_ops._response_ok(response, "POST")):
        print("FAIL: Adding VLANs '%s' to Port '%s' trunk failed with status code %d"
              % (vlan_trunk_ids, l2_port_name, response.status_code))
    else:
        print("SUCCESS: Adding VLANs '%s' to Port '%s' trunk succeeded"
              % (vlan_trunk_ids, l2_port_name))


def _port_set_native_vlan(l2_port_name, vlan_id, tagged=True, **kwargs):
    """
    Perform GET and PUT/POST calls to set a VLAN to be the native VLAN on the trunk. Also gives the option to set
    the VLAN as tagged.

    :param l2_port_name: L2 interface's Port table entry name
    :param vlan_id: Numeric ID of VLAN to add to trunk port
    :param tagged: Boolean to determine if the native VLAN will be set as the tagged VLAN.  If False, the VLAN
        will be set as the native untagged VLAN
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if tagged:
        vlan_mode = "native-tagged"
    else:
        vlan_mode = "native-untagged"

    l2_port_name_percents = common_ops._replace_special_characters(l2_port_name)
    vlan_key = {str(vlan_id): "/rest/v10.04/system/vlans/%d" % vlan_id}
    port_data = get_interface(l2_port_name_percents, depth=1, selector="writable", **kwargs)

    port_data['vlan_tag'] = vlan_key
    port_data['routing'] = False
    port_data['vlan_mode'] = vlan_mode

    if (port_data['vlan_trunks']) and (vlan_key not in port_data['vlan_trunks']):
        port_data['vlan_trunks'].update(vlan_key)

    target_url = kwargs["url"] + "system/interfaces/%s" % l2_port_name_percents
    put_data = json.dumps(port_data, sort_keys=True, indent=4)
    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not (common_ops._response_ok(response, "PUT") or common_ops._response_ok(response, "POST")):
        print("FAIL: Setting native VLAN ID '%d' to Port '%s' failed with status code %d"
              % (vlan_id, l2_port_name, response.status_code))
    else:
        print("SUCCESS: Setting native VLAN ID '%d' to Port '%s' succeeded"
              % (vlan_id, l2_port_name))


def _delete_vlan_port(l2_port_name, vlan_id, **kwargs):
    """
    Perform GET and PUT calls to remove a VLAN from a trunk port

    :param l2_port_name: L2 interface's Port table entry name
    :param vlan_id: Numeric ID of VLAN to remove from trunk port
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    l2_port_name_percents = common_ops._replace_special_characters(l2_port_name)

    port_data = get_interface(l2_port_name, depth=1, selector="writable", **kwargs)

    if str(vlan_id) in port_data['vlan_trunks']:
        # remove vlan from 'vlan_trunks'
        port_data['vlan_trunks'].pop(str(vlan_id))

    target_url = kwargs["url"] + "system/interface/%s" % l2_port_name_percents
    put_data = json.dumps(port_data, sort_keys=True, indent=4)
    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Removing VLAN ID '%d' from Port '%s' trunk failed with status code %d"
              % (vlan_id, l2_port_name, response.status_code))
    else:
        print("SUCCESS: Removing VLAN ID '%d' from Port '%s' trunk succeeded"
              % (vlan_id, l2_port_name))


def add_port_to_lag(int_name, lag_id, **kwargs):
    """
    Perform GET and PUT calls to configure a Port as a LAG member, and also enable the port. For v1,
    also perform DELETE call to remove the Port table entry for the port.

    :param int_name: Alphanumeric name of the interface
    :param lag_id: Numeric ID of the LAG to which the port is to be added
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _add_port_to_lag_v1(int_name, lag_id, **kwargs)
    else:  # Updated else for when version is v10.04
        _add_port_to_lag(int_name, lag_id, **kwargs)


def _add_port_to_lag_v1(int_name, lag_id, **kwargs):
    """
    Perform GET and PUT calls to configure a Port as a LAG member, and also enable the port.
    Also perform DELETE call to remove the Port table entry for the port.

    :param int_name: Alphanumeric name of the interface
    :param lag_id: Numeric ID of the LAG to which the port is to be added
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    int_name_percents = common_ops._replace_special_characters(int_name)

    int_data = get_interface(int_name, 0, "configuration", **kwargs)

    int_data['user_config'] = {"admin": "up"}
    int_data['other_config']['lacp-aggregation-key'] = lag_id

    target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
    put_data = json.dumps(int_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Adding Interface '%s' to LAG '%d' "
              "failed with status code %d" % (int_name, lag_id, response.status_code))
    else:
        print("SUCCESS: Adding Interface '%s' to LAG '%d' "
              "succeeded" % (int_name, lag_id))

    # Delete Port Table entry for the port
    port.delete_port(int_name_percents, **kwargs)


def _add_port_to_lag(int_name, lag_id, **kwargs):
    """
    Perform GET and PUT calls to configure a Port as a LAG member, and also enable the port

    :param int_name: Alphanumeric name of the interface
    :param lag_id: Numeric ID of the LAG to which the port is to be added
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    int_name_percents = common_ops._replace_special_characters(int_name)

    int_data = get_interface(int_name, 1, "writable", **kwargs)

    int_data['user_config'] = {"admin": "up"}
    int_data['other_config']['lacp-aggregation-key'] = lag_id

    target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
    put_data = json.dumps(int_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Adding Interface '%s' to LAG '%d' "
              "failed with status code %d" % (int_name, lag_id, response.status_code))
    else:
        print("SUCCESS: Adding Interface '%s' to LAG '%d' "
              "succeeded" % (int_name, lag_id))


def remove_port_from_lag(int_name, lag_id, **kwargs):
    """
    Perform GET and PUT calls to configure a Port as a LAG member, and also disable the port

    :param int_name: Alphanumeric name of the interface
    :param lag_id: Numeric ID of the LAG to which the port is to be added
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _remove_port_from_lag_v1(int_name, lag_id, **kwargs)
    else:  # Updated else for when version is v10.04
        _remove_port_from_lag(int_name, lag_id, **kwargs)


def _remove_port_from_lag_v1(int_name, lag_id, **kwargs):
    """
    Perform GET and PUT calls to remove a Port from a LAG, and also disable the port

    :param int_name: Alphanumeric name of the interface
    :param lag_id: Numeric ID of the LAG to which the port is to be added
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    # Create Port Table entry for the port
    add_l2_interface(int_name, **kwargs)

    int_name_percents = common_ops._replace_special_characters(int_name)

    int_data = get_interface(int_name, 0, "configuration", **kwargs)

    int_data['user_config'] = {"admin": "down"}
    int_data['other_config'].pop('lacp-aggregation-key', None)

    target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
    put_data = json.dumps(int_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Removing interface '%s' from LAG '%d' "
              "failed with status code %d" % (int_name, lag_id, response.status_code))
    else:
        print("SUCCESS: Removing interface '%s' from LAG '%d' "
              "succeeded" % (int_name, lag_id))


def _remove_port_from_lag(int_name, lag_id, **kwargs):
    """
    Perform GET and PUT calls to remove a Port from a LAG, and also disable the port

    :param int_name: Alphanumeric name of the interface
    :param lag_id: Numeric ID of the LAG to which the port is to be added
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    int_name_percents = common_ops._replace_special_characters(int_name)

    int_data = get_interface(int_name, 1, "writable", **kwargs)

    int_data['user_config'] = {"admin": "down"}
    int_data['other_config'].pop('lacp-aggregation-key', None)

    target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
    put_data = json.dumps(int_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Removing interface '%s' from LAG '%d' "
              "failed with status code %d" % (int_name, lag_id, response.status_code))
    else:
        print("SUCCESS: Removing interface '%s' from LAG '%d' "
              "succeeded" % (int_name, lag_id))


def _clear_interface_acl(interface_name, acl_type="aclv4_out", **kwargs):
    """
    Perform GET and PUT calls to clear an interface's ACL

    :param port_name: Alphanumeric name of the Port
    :param acl_type: Type of ACL, options are between 'aclv4_out', 'aclv4_in', and 'aclv6_in'
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if acl_type not in ['aclv4_out', 'aclv4_in', 'aclv6_in']:
        raise Exception("ERROR: acl_type should be 'aclv4_out', 'aclv4_in', or 'aclv6_in'")

    int_name_percents = common_ops._replace_special_characters(interface_name)

    interface_data = get_interface(interface_name, depth=1, selector="writable", **kwargs)

    cfg_type = acl_type + '_cfg'
    cfg_version = acl_type + '_cfg_version'

    interface_data.pop(cfg_type, None)
    interface_data.pop(cfg_version, None)

    target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
    put_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Clearing %s ACL on Interface '%s' failed with status code %d"
              % (cfg_type, interface_name, response.status_code))
    else:
        print("SUCCESS: Clearing %s ACL on Interface '%s' succeeded"
              % (cfg_type, interface_name))


def initialize_interface_entry(int_name, **kwargs):
    """
    Perform a PUT call on the interface to initialize it to it's default state.

    :param int_name: Alphanumeric name of the system interface
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    int_name_percents = common_ops._replace_special_characters(int_name)
    int_data = {}
    target_url = kwargs["url"] + "system/interfaces/%s" % int_name_percents
    put_data = json.dumps(int_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Initializing interface '%s' failed with status code %d" % (int_name, response.status_code))
    else:
        print("SUCCESS: Initializing interface '%s' succeeded" % int_name)
        # Remove all IPv6 entries for this interface
        ipv6_list = get_ipv6_addresses(int_name, **kwargs)
        if ipv6_list:
            for ipv6_address in ipv6_list:
                delete_ipv6_address(int_name, ipv6_address, **kwargs)



def initialize_interface(interface_name, **kwargs):
    """
    Perform a PUT call to the Interface Table or Port Table to initialize an interface to factory settings

    :param interface_name: Name of interface's reference entry in Interface table
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        port.initialize_port_entry(interface_name, **kwargs)
    else:  # Updated else for when version is v10.04
        initialize_interface_entry(interface_name, **kwargs)