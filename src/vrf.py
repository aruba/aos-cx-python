from src import common_ops

import json


def get_all_vrfs(**kwargs):
    """
    Perform a GET call to get a list (or dictionary) of all entries in VRF table

    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: List/dict of all VRFs in the table
    """
    target_url = kwargs["url"] + "system/vrfs"

    response = kwargs["s"].get(target_url, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting list/dict of all VRF table entries failed with status code %d"
              % response.status_code)
        vrfs = []
    else:
        print("SUCCESS: Getting list/dict of all VRF table entries succeeded")
        vrfs = response.json()

    return vrfs


def add_vrf(vrf_name, route_distinguisher=None, vrf_type="user", **kwargs):
    """
    Perform a POST call to create a new VRF, and add a route distinguisher if desired.

    :param vrf_name: Alphanumeric name of VRF
    :param route_distinguisher: Optional route distinguisher to add. Defaults to nothing if not specified.
    :param vrf_type: Optional VRF type. Defaults to "user" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        add_vrf_v1(vrf_name, route_distinguisher, vrf_type, **kwargs)
    else:  # Updated else for when version is v10.04
        _add_vrf(vrf_name, route_distinguisher, vrf_type, **kwargs)


def add_vrf_v1(vrf_name, route_distinguisher=None, vrf_type="user", **kwargs):
    """
    Perform a POST call to create a new VRF, and add a route distinguisher if desired.

    :param vrf_name: name of VRF
    :param route_distinguisher: Optional route distinguisher to add. Defaults to nothing if not specified.
    :param vrf_type: Optional VRF type. Defaults to "user" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    vrfs_list = get_all_vrfs(**kwargs)

    if "/rest/v1/system/vrfs/%s" % vrf_name not in vrfs_list:
        vrf_data = {"name": vrf_name, "type": vrf_type}

        if route_distinguisher is not None:
            vrf_data["rd"] = route_distinguisher

        target_url = kwargs["url"] + "system/vrfs"
        post_data = json.dumps(vrf_data, sort_keys=True, indent=4)

        response = kwargs["s"].post(target_url, data=post_data, verify=False)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Creating new VRF '%s' failed with status code %d" % (vrf_name, response.status_code))
        else:
            print("SUCCESS: Creating new VRF '%s' succeeded" % vrf_name)
    else:
        print("SUCCESS: No need to create VRF '%s' since it already exists" % vrf_name)


def _add_vrf(vrf_name, route_distinguisher=None, vrf_type="user", **kwargs):
    """
    Perform a POST call to create a new VRF, and add a route distinguisher if desired.

    :param vrf_name: name of VRF
    :param route_distinguisher: Optional route distinguisher to add. Defaults to nothing if not specified.
    :param vrf_type: Optional VRF type. Defaults to "user" if not specified.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    vrfs_dict = get_all_vrfs(**kwargs)

    if vrf_name not in vrfs_dict:
        vrf_data = {"name": vrf_name, "type": vrf_type}

        if route_distinguisher is not None:
            vrf_data["rd"] = route_distinguisher

        target_url = kwargs["url"] + "system/vrfs"
        post_data = json.dumps(vrf_data, sort_keys=True, indent=4)

        response = kwargs["s"].post(target_url, data=post_data, verify=False)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Creating new VRF '%s' failed with status code %d" % (vrf_name, response.status_code))
        else:
            print("SUCCESS: Creating new VRF '%s' succeeded" % vrf_name)
    else:
        print("SUCCESS: No need to create VRF '%s' since it already exists" % vrf_name)


def get_vrf(vrf_name, depth=0, selector=None, **kwargs):
    """
    Perform a GET call to get data for a VRF table entry

    :param vrf_name: Alphanumeric name of the VRF
    :param depth: Integer deciding how many levels into the API JSON that references will be returned.
    :param selector: Alphanumeric option to select specific information to return.  The options are 'configuration',
        'status', 'statistics' or 'writable'.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Dictionary containing the VRF data
    """
    if kwargs["url"].endswith("/v1/"):
        return _get_vrf_v1(vrf_name, depth, selector, **kwargs)
    else:   # Updated else for when version is v10.04
        return _get_vrf(vrf_name, depth, selector, **kwargs)


def _get_vrf_v1(vrf_name, depth=0, selector=None, **kwargs):
    """
    Perform a GET call to get data for a VRF table entry

    :param vrf_name: Alphanumeric name of the VRF
    :param depth: Integer deciding how many levels into the API JSON that references will be returned.
    :param selector: Alphanumeric option to select specific information to return.  The options are 'configuration',
        'status', 'statistics' or 'writable'.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Dictionary containing the VRF data
    """
    if selector not in ['configuration', 'status', 'statistics', None]:
        raise Exception("ERROR: Selector should be 'configuration', 'status', or 'statistics'")

    target_url = kwargs["url"] + "system/vrfs/%s" % vrf_name
    payload = {
        "depth": depth,
        "selector": selector
    }
    response = kwargs["s"].get(target_url, verify=False, params=payload, timeout=2)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting VRF table entry '%s' failed with status code %d" % (vrf_name, response.status_code))
        vrf = []
    else:
        print("SUCCESS: Getting VRF table entry '%s' succeeded" % vrf_name)
        vrf = response.json()

    return vrf


def _get_vrf(vrf_name, depth=1, selector=None, **kwargs):
    """
    Perform a GET call to get data for a VRF table entry

    :param vrf_name: Alphanumeric name of the VRF
    :param depth: Integer deciding how many levels into the API JSON that references will be returned.
    :param selector: Alphanumeric option to select specific information to return.  The options are 'configuration',
        'status', 'statistics' or 'writable'.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Dictionary containing the VRF data
    """

    if selector not in ['configuration', 'status', 'statistics', 'writable', None]:
        raise Exception("ERROR: Selector should be 'configuration', 'status', 'statistics', or 'writable'")

    target_url = kwargs["url"] + "system/vrfs/%s" % vrf_name
    payload = {
        "depth": depth,
        "selector": selector
    }
    response = kwargs["s"].get(target_url, verify=False, params=payload, timeout=2)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting VRF table entry '%s' failed with status code %d" % (vrf_name, response.status_code))
        vrf = []
    else:
        print("SUCCESS: Getting VRF table entry '%s' succeeded" % vrf_name)
        vrf = response.json()

    return vrf


def delete_vrf(vrf_name, **kwargs):
    """
    Perform a DELETE call to delete a VRF.
    Note that this functions has logic that works for both v1 and v10.04

    :param vrf_name: Alphanumeric name of VRF
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    vrf_list = get_all_vrfs(**kwargs)

    if kwargs["url"].endswith("/v1/"):
        vrf_check = "/rest/v1/system/vrfs/%s" % vrf_name
    else:
        # Else logic designed for v10.04 and later
        vrf_check = vrf_name

    if vrf_check in vrf_list:
        target_url = kwargs["url"] + "system/vrfs/%s" % vrf_name
        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting VRF '%s' failed with status code %d" % (vrf_name, response.status_code))
        else:
            print("SUCCESS: Deleting VRF '%s' succeeded" % vrf_name)
    else:
        print("SUCCESS: No need to delete VRF '%s' since it doesn't exist"
              % vrf_name)

def add_vrf_address_family(vrf_name, family_type="ipv4_unicast", export_target=[], import_targets=[], **kwargs):
    """
    Perform a POST call to create a new VRF, and add a route distinguisher if desired.
    Note that this functions has logic that works for both v1 and v10.04

    :param vrf_name: Alphanumeric name of VRF
    :param family_type: Alphanumeric type of the Address Family.  The options are 'ipv4_unicast' and 'ipv6_unicast'.
        The default value is set to 'ipv4_unicast'.
    :param export_target: Optional list of export route targets.
    :param import_targets: Optional list of import route targets
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    vrf_list = get_all_vrfs(**kwargs)

    if family_type == "ipv4-unicast":
        family_type = "ipv4_unicast"
    elif family_type == "ipv6-unicast":
        family_type = "ipv6_unicast"

    if family_type not in ['ipv4_unicast', 'ipv6_unicast']:
        raise Exception("ERROR: family_type should be 'ipv4_unicast', or 'ipv6_unicast'")

    if kwargs["url"].endswith("/v1/"):
        vrf_check = "/rest/v1/system/vrfs/%s" % vrf_name
    else:
        # Else logic designed for v10.04 and later
        vrf_check = vrf_name

    if vrf_check in vrf_list:
        address_family_data = {
            "address_family": family_type,
            "export_route_targets": export_target,
            "import_route_targets": import_targets,
            "route_map": {}
        }

        target_url = kwargs["url"] + "system/vrfs/%s/vrf_address_families" % vrf_name
        post_data = json.dumps(address_family_data, sort_keys=True, indent=4)

        response = kwargs["s"].post(target_url, data=post_data, verify=False)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Creating '%s' Address Family on VRF '%s' failed with status code %d" % (family_type, vrf_name,
                                                                                                 response.status_code))
        else:
            print("SUCCESS: Creating '%s' Address Family on VRF '%s' succeeded" % (family_type, vrf_name))
    else:
        print("FAIL: Cannot add Address Family to VRF '%s' since the VRF has not been created yet" % vrf_name)


def delete_vrf_address_family(vrf_name, family_type="ipv4_unicast", **kwargs):
    """
    Perform a DELETE call to remove a VRF address family.
    Note that this functions has logic that works for both v1 and v10.04

    :param vrf_name: Alphanumeric name of VRF
    :param family_type: Alphanumeric type of the Address Family.  The options are 'ipv4_unicast' and 'ipv6_unicast'.
        The default value is set to 'ipv4_unicast'.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    vrf_list = get_all_vrfs(**kwargs)

    if family_type == "ipv4-unicast":
        family_type = "ipv4_unicast"
    elif family_type == "ipv6-unicast":
        family_type = "ipv6_unicast"

    if family_type not in ['ipv4_unicast', 'ipv6_unicast']:
        raise Exception("ERROR: family_type should be 'ipv4_unicast', or 'ipv6_unicast'")

    if kwargs["url"].endswith("/v1/"):
        vrf_check = "/rest/v1/system/vrfs/%s" % vrf_name
    else:
        # Else logic designed for v10.04 and later
        vrf_check = vrf_name

    if vrf_check in vrf_list:
        target_url = kwargs["url"] + "system/vrfs/%s/vrf_address_families/%s" % (vrf_name, family_type)
        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting '%s' Address Family on VRF '%s' failed with status code %d" % (family_type, vrf_name,
                                                                                                 response.status_code))
        else:
            print("SUCCESS: Deleting '%s' Address Family on VRF '%s' succeeded" % (family_type, vrf_name))
    else:
        print("SUCCESS: No need to delete Address Family to VRF '%s' since it does not exist" % vrf_name)
