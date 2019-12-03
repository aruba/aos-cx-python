from src import common_ops, interface, port

import json


def get_ospf_routers(vrf, **kwargs):
    """
    Perform a GET call to get a list of all OSPF Router IDs
    :param vrf: Alphanumeric name of the VRF that we are retrieving all Router IDs from
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: List of all OSPF Router IDs in the table
    """
    target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers" % vrf

    response = kwargs["s"].get(target_url, verify=False)

    ospf_list = []
    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting list of all OSPF Router IDs failed with status code %d"
              % response.status_code)
    else:
        print("SUCCESS: Getting list of all OSPF Router IDs succeeded")
        ospf_list = response.json()

    return ospf_list


def create_ospf_id(vrf, ospf_id, redistribute=["connected", "static"], **kwargs):
    """
    Perform a POST call to create an OSPF ID
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param redistribute: List of types of redistribution methods for the OSPF Process, with the options being "bgp",
                         "connected", and "static"
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    ospf_data = {
        "instance_tag": ospf_id,
        "redistribute": redistribute
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers" % vrf

    post_data = json.dumps(ospf_data, sort_keys=True, indent=4)
    response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Creating OSPF ID '%s' on vrf %s failed with status code %d"
              % (ospf_id, vrf, response.status_code))
    else:
        print("SUCCESS: Creating OSPF ID '%s' succeeded on vrf %s" % (ospf_id, vrf))


def create_ospf_area(vrf, ospf_id, area_id, area_type='default', **kwargs):
    """
    Perform a POST call to create an OSPF Area for the specified OSPF ID
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param area_type: Alphanumeric defining how the external routing and summary LSAs for this area will be handled.
                      Options are "default","nssa","nssa_no_summary","stub","stub_no_summary"
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    if kwargs["url"].endswith("/v1/"):
        _create_ospf_area_v1(vrf, ospf_id, area_id, area_type, **kwargs)
    else:   # Updated else for when version is v10.04
        _create_ospf_area(vrf, ospf_id, area_id, area_type, **kwargs)


def _create_ospf_area_v1(vrf, ospf_id, area_id, area_type='default', **kwargs):
    """
    Perform a POST call to create an OSPF Area for the specified OSPF ID
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param area_type: Alphanumeric defining how the external routing and summary LSAs for this area will be handled.
                      Options are "default","nssa","nssa_no_summary","stub","stub_no_summary"
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    area_data = {
        "area_id": area_id,
        "area_type": area_type,
        "ipsec_ah": {},
        "ipsec_esp": {},
        "ospf_interfaces": {},
        "ospf_vlinks": {},
        "other_config": {}
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers/%s/areas" % (vrf, ospf_id)

    post_data = json.dumps(area_data, sort_keys=True, indent=4)
    response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Creating OSPF Area '%s' on OSPF ID  %s failed with status code %d"
              % (area_id, ospf_id, response.status_code))
    else:
        print("SUCCESS: Creating OSPF Area '%s' succeeded on OSPF ID %s" % (area_id, ospf_id))


def _create_ospf_area(vrf, ospf_id, area_id, area_type='default', **kwargs):
    """
    Perform a POST call to create an OSPF Area for the specified OSPF ID
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param area_type: Alphanumeric defining how the external routing and summary LSAs for this area will be handled.
                      Options are "default","nssa","nssa_no_summary","stub","stub_no_summary"
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    area_data = {
        "area_id": area_id,
        "area_type": area_type,
        "ipsec_ah": {},
        "ipsec_esp": {},
        "other_config": {
            "stub_default_cost": 1,
            "stub_metric_type": "metric_non_comparable"
        }
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers/%s/areas" % (vrf, ospf_id)

    post_data = json.dumps(area_data, sort_keys=True, indent=4)
    response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Creating OSPF Area '%s' on OSPF ID  %s failed with status code %d"
              % (area_id, ospf_id, response.status_code))
    else:
        print("SUCCESS: Creating OSPF Area '%s' succeeded on OSPF ID %s" % (area_id, ospf_id))


def create_ospf_interface(vrf, ospf_id, area_id, interface_name, **kwargs):
    """
    Perform POST calls to attach an interface to an OSPF area.
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _create_ospf_interface_v1(vrf, ospf_id, area_id, interface_name, **kwargs)
    else:   # Updated else for when version is v10.04
        _create_ospf_interface(vrf, ospf_id, area_id, interface_name, **kwargs)


def _create_ospf_interface_v1(vrf, ospf_id, area_id, interface_name, **kwargs):
    """
    Perform POST calls to attach an interface to an OSPF area.
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    port_name_percents = common_ops._replace_special_characters(interface_name)
    port_uri = '/rest/v1/system/ports/' + port_name_percents

    port_data = {
        "interface_name": interface_name,
        "port": port_uri
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers/%s/areas/%s/ospf_interfaces" % (vrf, ospf_id, area_id)
    post_data = json.dumps(port_data, sort_keys=True, indent=4)

    response = kwargs["s"].post(target_url, data=post_data, verify=False)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Applying Interface '%s' to OSPF ID '%s' failed with status code %d"
              % (interface_name, ospf_id, response.status_code))
    else:
        print("SUCCESS: Applying Interface '%s' to OSPF ID '%s' succeeded"
              % (interface_name, ospf_id))


def _create_ospf_interface(vrf, ospf_id, area_id, interface_name, **kwargs):
    """
    Perform POST calls to attach an interface to an OSPF area.
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)
    port_uri = '/rest/v10.04/system/interfaces/' + interface_name_percents

    interface_data = {
        "interface_name": interface_name,
        "port": port_uri
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers/%s/areas/%s/ospf_interfaces" % (vrf, ospf_id, area_id)
    post_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].post(target_url, data=post_data, verify=False)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Applying Interface '%s' to OSPF ID '%s' failed with status code %d"
              % (interface_name, ospf_id, response.status_code))
    else:
        print("SUCCESS: Applying Interface '%s' to OSPF ID '%s' succeeded"
              % (interface_name, ospf_id))


def update_ospf_interface_authentication(vrf, ospf_id, interface_name, auth_type, digest_key, auth_pass, **kwargs):
    """
    Perform PUT calls to update an Interface with OSPF to have authentication
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param auth_type: Alphanumeric type of authentication, chosen between 'md5', 'null', and 'text'
    :param digest_key: Integer between 1-255 that functions as the digest key for the authentication method
    :param auth_pass: Alphanumeric text for the authentication password.  Note that this will be translated to a
                      base64 String in the configuration and json.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _update_ospf_interface_authentication_v1(vrf, ospf_id, interface_name, auth_type,
                                                 digest_key, auth_pass, **kwargs)
    else:   # Updated else for when version is v10.04
        _update_ospf_interface_authentication(vrf, ospf_id, interface_name, auth_type, digest_key, auth_pass, **kwargs)


def _update_ospf_interface_authentication_v1(vrf, ospf_id, interface_name, auth_type, digest_key, auth_pass, **kwargs):
    """
    Perform PUT calls to update an Interface with OSPF to have authentication
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param auth_type: Alphanumeric type of authentication, chosen between 'md5', 'null', and 'text'
    :param digest_key: Integer between 1-255 that functions as the digest key for the authentication method
    :param auth_pass: Alphanumeric text for the authentication password.  Note that this will be translated to a
                      base64 String in the configuration and json.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ports_list = port.get_all_ports(**kwargs)
    port_name_percents = common_ops._replace_special_characters(interface_name)

    if "/rest/v1/system/ports/%s" % port_name_percents not in ports_list:
        port.add_l3_ipv4_port(interface_name, vrf=vrf, **kwargs)

    port_data = port.get_port(interface_name, depth=0, selector="configuration", **kwargs)

    # must remove these fields from the data since they can't be modified
    port_data.pop('name', None)
    port_data.pop('origin', None)

    port_data['ospf_auth_type'] = auth_type
    port_data['ospf_auth_md5_keys'] = {str(digest_key): auth_pass}
    port_data['ospf_if_type'] = "ospf_iftype_broadcast"
    port_data['routing'] = True
    port_data['vrf'] = "/rest/v1/system/vrfs/" + vrf

    target_url = kwargs["url"] + "system/ports/%s" % port_name_percents
    put_data = json.dumps(port_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Updating OSPF %s Authentication for Port '%s' failed with status code %d"
              % (ospf_id, interface_name, response.status_code))
    else:
        print("SUCCESS: Updating OSPF %s Authentication for Port '%s' succeeded" % (ospf_id, interface_name))


def _update_ospf_interface_authentication(vrf, ospf_id, interface_name, auth_type, digest_key, auth_pass, **kwargs):
    """
    Perform PUT calls to update an Interface with OSPF to have authentication
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param auth_type: Alphanumeric type of authentication, chosen between 'md5', 'null', and 'text'
    :param digest_key: Integer between 1-255 that functions as the digest key for the authentication method
    :param auth_pass: Alphanumeric text for the authentication password.  Note that this will be translated to a
                      base64 String in the configuration and json.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)

    interface_data = interface.get_interface(interface_name, depth=1, selector="writable", **kwargs)

    interface_data['ospf_auth_type'] = auth_type
    interface_data['ospf_auth_md5_keys'] = {digest_key: auth_pass}
    interface_data['ospf_if_type'] = "ospf_iftype_broadcast"
    interface_data['routing'] = True
    interface_data['vrf'] = "/rest/v10.04/system/vrfs/" + vrf

    target_url = kwargs["url"] + "system/interfaces/%s" % interface_name_percents
    put_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Updating OSPF %s Authentication for Port '%s' failed with status code %d"
              % (ospf_id, interface_name, response.status_code))
    else:
        print("SUCCESS: Updating OSPF %s Authentication for Port '%s' succeeded" % (ospf_id, interface_name))


def update_ospf_interface_type(vrf, ospf_id, interface_name, interface_type="pointtopoint", **kwargs):
    """
    Perform PUT calls to update the type of OSPFv2 Interface given, as well as enable routing on the interface
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param interface_type: Alphanumeric type of OSPF interface.  The options are 'broadcast', 'loopback', 'nbma',
        'none', 'pointomultipoint', 'pointopoint', and 'virtuallink'
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if interface_type not in ['broadcast', 'loopback', 'statistics', 'nbma', 'pointomultipoint',
                              'pointopoint', 'virtuallink', None]:
        raise Exception("ERROR: Incorrect value for interface type. The options are 'broadcast', 'loopback', 'nbma', "
                        "'none', 'pointomultipoint', 'pointopoint', and 'virtuallink'")
    if kwargs["url"].endswith("/v1/"):
        _update_ospf_interface_type_v1(vrf, ospf_id, interface_name, interface_type, **kwargs)
    else:   # Updated else for when version is v10.04
        _update_ospf_interface_type(vrf, ospf_id, interface_name, interface_type, **kwargs)


def _update_ospf_interface_type_v1(vrf, ospf_id, interface_name, interface_type, **kwargs):
    """
    Perform PUT calls to update the type of OSPFv2 Interface given, as well as enable routing on the interface
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param interface_type: Alphanumeric type of OSPF interface.  The options are 'broadcast', 'loopback', 'nbma',
        'none', 'pointomultipoint', 'pointopoint', and 'virtuallink'
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ports_list = port.get_all_ports(**kwargs)
    port_name_percents = common_ops._replace_special_characters(interface_name)

    if "/rest/v1/system/ports/%s" % port_name_percents not in ports_list:
        port.add_l3_ipv4_port(interface_name, vrf=vrf, **kwargs)

    port_data = port.get_port(interface_name, depth=0, selector="configuration", **kwargs)

    # must remove these fields from the data since they can't be modified
    port_data.pop('name', None)
    port_data.pop('origin', None)

    port_data['ospf_if_type'] = "ospf_iftype_%s" % interface_type
    port_data['routing'] = True
    port_data['vrf'] = "/rest/v1/system/vrfs/" + vrf

    target_url = kwargs["url"] + "system/ports/%s" % port_name_percents
    put_data = json.dumps(port_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Updating OSPF %s interface type for Port '%s' failed with status code %d"
              % (ospf_id, interface_name, response.status_code))
    else:
        print("SUCCESS: Updating OSPF %s interface type for Port '%s' succeeded" % (ospf_id, interface_name))


def _update_ospf_interface_type(vrf, ospf_id, interface_name, interface_type, **kwargs):
    """
    Perform PUT calls to update the type of OSPFv2 Interface given, as well as enable routing on the interface
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPF area
    :param interface_type: Alphanumeric type of OSPF interface.  The options are 'broadcast', 'loopback', 'nbma',
        'none', 'pointomultipoint', 'pointopoint', and 'virtuallink'
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)

    interface_data = interface.get_interface(interface_name, depth=1, selector="writable", **kwargs)

    interface_data['ospf_if_type'] = "ospf_iftype_%s" % interface_type
    interface_data['routing'] = True
    interface_data['vrf'] = "/rest/v10.04/system/vrfs/" + vrf

    target_url = kwargs["url"] + "system/interfaces/%s" % interface_name_percents
    put_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Updating OSPF %s interface type for Interface '%s' failed with status code %d"
              % (ospf_id, interface_name, response.status_code))
    else:
        print("SUCCESS: Updating OSPF %s interface type for Interface '%s' succeeded" % (ospf_id, interface_name))


def delete_ospf_id(vrf, ospf_id, **kwargs):
    """
    Perform a DELETE call to delete an OSPF Router ID
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _delete_ospf_id_v1(vrf, ospf_id, **kwargs)
    else:   # Updated else for when version is v10.04
        _delete_ospf_id(vrf, ospf_id, **kwargs)


def _delete_ospf_id_v1(vrf, ospf_id, **kwargs):
    """
    Perform a DELETE call to delete an OSPF Router ID
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ospf_list = get_ospf_routers(vrf, **kwargs)
    ospf_uri = "/rest/v1/system/vrfs/%s/ospf_routers/%s" % (vrf, ospf_id)
    ospf_id_key = str(ospf_id)

    if ospf_id_key in ospf_list and ospf_uri == ospf_list[ospf_id_key]:

        target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers/%s" % (vrf, ospf_id)

        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting OSPF ID '%s' on VRF '%s' failed with status code %d"
                  % (ospf_id, vrf, response.status_code))
        else:
            print("SUCCESS: Deleting OSPF ID %s on VRF '%s' succeeded" % (ospf_id, vrf))
    else:
        print("SUCCESS: No need to delete OSPF ID %s on VRF '%s' since it doesn't exist"
              % (ospf_id, vrf))


def _delete_ospf_id(vrf, ospf_id, **kwargs):
    """
    Perform a DELETE call to delete an OSPF Router ID
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ospf_list = get_ospf_routers(vrf, **kwargs)
    ospf_uri = "/rest/v10.04/system/vrfs/%s/ospf_routers/%s" % (vrf, ospf_id)
    ospf_id_key = str(ospf_id)

    if ospf_id_key in ospf_list and ospf_uri == ospf_list[ospf_id_key]:

        target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers/%s" % (vrf, ospf_id)

        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting OSPF ID '%s' on VRF '%s' failed with status code %d"
                  % (ospf_id, vrf, response.status_code))
        else:
            print("SUCCESS: Deleting OSPF ID %s on VRF '%s' succeeded" % (ospf_id, vrf))
    else:
        print("SUCCESS: No need to delete OSPF ID %s on VRF '%s' since it doesn't exist"
              % (ospf_id, vrf))


def delete_ospf_area(vrf, ospf_id, area_id, **kwargs):
    """
    Perform a DETELE call to remove an OSPF Area for the specified OSPF ID
    :param vrf: Alphanumeric name of the VRF the OSPF ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    target_url = kwargs["url"] + "system/vrfs/%s/ospf_routers/%s/areas/%s" % (vrf, ospf_id, area_id)

    response = kwargs["s"].delete(target_url, verify=False, timeout=2)

    if not common_ops._response_ok(response, "DELETE"):
        print("FAIL: Deleting OSPF Area '%s' on OSPF ID  %s failed with status code %d"
              % (area_id, ospf_id, response.status_code))
    else:
        print("SUCCESS: Deleting OSPF Area '%s' succeeded on OSPF ID %s" % (area_id, ospf_id))


def get_ospfv3_routers(vrf, **kwargs):
    """
    Perform a GET call to get a list of all OSPFv3 Router IDs
    :param vrf: Alphanumeric name of the VRF that we are retrieving all Router IDs from
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: List of all OSPFv3 Router IDs in the table
    """
    target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers" % vrf

    response = kwargs["s"].get(target_url, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting list of all OSPFv3 Router IDs failed with status code %d"
              % response.status_code)
    else:
        print("SUCCESS: Getting list of all OSPFv3 Router IDs succeeded")

    ospfv3_list = response.json()
    return ospfv3_list


def create_ospfv3_id(vrf, ospf_id,  **kwargs):
    """
    Perform a POST call to create an OSPFv3 ID
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPF process ID between numbers 1-63
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    ospf_data = {
        "instance_tag": ospf_id
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers" % vrf

    post_data = json.dumps(ospf_data, sort_keys=True, indent=4)

    response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Creating OSPFv3 ID '%s' on VRF %s failed with status code %d"
              % (ospf_id, vrf, response.status_code))
    else:
        print("SUCCESS: Creating OSPFv3 ID '%s' succeeded on VRF %s" % (ospf_id, vrf))


def create_ospfv3_area(vrf, ospf_id, area_id, area_type='default', **kwargs):
    """
    Perform a POST call to create an OSPFv3 Area for the specified OSPF ID
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param area_type: Alphanumeric defining how the external routing and summary LSAs for this area will be handled.
                      Options are "default","nssa","nssa_no_summary","stub","stub_no_summary"
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    if kwargs["url"].endswith("/v1/"):
        _create_ospfv3_area_v1(vrf, ospf_id, area_id, area_type, **kwargs)
    else:   # Updated else for when version is v10.04
        _create_ospfv3_area(vrf, ospf_id, area_id, area_type, **kwargs)


def _create_ospfv3_area_v1(vrf, ospf_id, area_id, area_type='default', **kwargs):
    """
    Perform a POST call to create an OSPFv3 Area for the specified OSPF ID
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param area_type: Alphanumeric defining how the external routing and summary LSAs for this area will be handled.
                      Options are "default","nssa","nssa_no_summary","stub","stub_no_summary"
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """

    area_data = {
        "area_id": area_id,
        "area_type": area_type,
        "ipsec_ah": {},
        "ipsec_esp": {},
        "ospf_interfaces": {},
        "ospf_vlinks": {},
        "other_config": {}
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers/%s/areas" % (vrf, ospf_id)

    post_data = json.dumps(area_data, sort_keys=True, indent=4)

    response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Creating OSPFv3 Area '%s' on OSPFv3 ID %s failed with status code %d"
              % (area_id, ospf_id, response.status_code))
    else:
        print("SUCCESS: Creating OSPFv3 Area '%s' succeeded on OSPFv3 ID %s" % (area_id, ospf_id))


def _create_ospfv3_area(vrf, ospf_id, area_id, area_type='default', **kwargs):
    """
    Perform a POST call to create an OSPFv3 Area for the specified OSPFv3 ID
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param area_type: Alphanumeric defining how the external routing and summary LSAs for this area will be handled.
                      Options are "default","nssa","nssa_no_summary","stub","stub_no_summary"
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    area_data = {
        "area_id": area_id,
        "area_type": area_type,
        "ipsec_ah": {},
        "ipsec_esp": {},
        "other_config": {
            "stub_default_cost": 1,
            "stub_metric_type": "metric_non_comparable"
        }
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers/%s/areas" % (vrf, ospf_id)

    post_data = json.dumps(area_data, sort_keys=True, indent=4)
    response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Creating OSPFv3 Area '%s' on OSPFv3 ID %s failed with status code %d"
              % (area_id, ospf_id, response.status_code))
    else:
        print("SUCCESS: Creating OSPFv3 Area '%s' succeeded on OSPFv3 ID %s" % (area_id, ospf_id))


def create_ospfv3_interface(vrf, ospf_id, area_id, interface_name, **kwargs):
    """
    Perform POST calls to attach an interface to an OSPFv3 area.
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPFv3 area
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _create_ospfv3_interface_v1(vrf, ospf_id, area_id, interface_name, **kwargs)
    else:   # Updated else for when version is v10.04
        _create_ospfv3_interface(vrf, ospf_id, area_id, interface_name, **kwargs)


def _create_ospfv3_interface_v1(vrf, ospf_id, area_id, interface_name, **kwargs):
    """
    Perform POST calls to attach an interface to an OSPFv3 area.
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPFv3 area
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    port_name_percents = common_ops._replace_special_characters(interface_name)
    port_uri = '/rest/v1/system/ports/' + port_name_percents

    port_data = {
        "interface_name": interface_name,
        "port": port_uri
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers/%s/areas/%s/ospf_interfaces" % (vrf, ospf_id, area_id)
    post_data = json.dumps(port_data, sort_keys=True, indent=4)

    response = kwargs["s"].post(target_url, data=post_data, verify=False)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Applying Interface '%s' to OSPFv3 ID '%s' failed with status code %d"
              % (interface_name, ospf_id, response.status_code))
    else:
        print("SUCCESS: Applying Interface '%s' to OSPFv3 ID '%s' succeeded"
              % (interface_name, ospf_id))


def _create_ospfv3_interface(vrf, ospf_id, area_id, interface_name, **kwargs):
    """
    Perform POST calls to attach an interface to an OSPFv3 area.
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPFv3 area
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)
    port_uri = '/rest/v10.04/system/interfaces/' + interface_name_percents

    interface_data = {
        "interface_name": interface_name,
        "port": port_uri
    }

    target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers/%s/areas/%s/ospf_interfaces" % (vrf, ospf_id, area_id)
    post_data = json.dumps(interface_data, sort_keys=True, indent=4)

    response = kwargs["s"].post(target_url, data=post_data, verify=False)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Applying Interface '%s' to OSPFv3 ID '%s' failed with status code %d"
              % (interface_name, ospf_id, response.status_code))
    else:
        print("SUCCESS: Applying Interface '%s' to OSPFv3 ID '%s' succeeded"
              % (interface_name, ospf_id))


def update_ospfv3_interface_authentication(vrf, ospf_id, interface_name, auth_type, digest_key, auth_pass, **kwargs):
    """
    Perform PUT calls to update an Interface with OSPFv3 to have authentication
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPFv3 area
    :param auth_type: Alphanumeric type of authentication, chosen between 'md5', 'null', and 'text'
    :param digest_key: Integer between 1-255 that functions as the digest key for the authentication method
    :param auth_pass: Alphanumeric text for the authentication password.  Note that this will be translated to a
                      base64 String in the configuration and json.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _update_ospfv3_interface_authentication_v1(vrf, ospf_id, interface_name, auth_type,
                                                   digest_key, auth_pass, **kwargs)
    else:   # Updated else for when version is v10.04
        _update_ospfv3_interface_authentication(vrf, ospf_id, interface_name, auth_type,
                                                digest_key, auth_pass, **kwargs)


def _update_ospfv3_interface_authentication_v1(vrf, ospf_id, interface_name, auth_type,
                                               digest_key, auth_pass, **kwargs):
    """
    Perform PUT calls to update an Interface with OSPFv3 to have authentication
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPFv3 area
    :param auth_type: Alphanumeric type of authentication, chosen between 'md5', 'null', and 'text'
    :param digest_key: Integer between 1-255 that functions as the digest key for the authentication method
    :param auth_pass: Alphanumeric text for the authentication password.  Note that this will be translated to a
                      base64 String in the configuration and json.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ports_list = port.get_all_ports(**kwargs)
    port_name_percents = common_ops._replace_special_characters(interface_name)

    if "/rest/v1/system/ports/%s" % port_name_percents not in ports_list:
        port.add_l3_ipv4_port(interface_name, vrf=vrf, **kwargs)

    port_data = port.get_port(interface_name, depth=0, selector="configuration", **kwargs)

    # must remove these fields from the data since they can't be modified
    port_data.pop('name', None)
    port_data.pop('origin', None)

    port_data['ospf_auth_type'] = auth_type
    port_data['ospf_auth_md5_keys'] = {str(digest_key): auth_pass}
    port_data['ospf_if_type'] = "ospf_iftype_broadcast"
    port_data['routing'] = True
    port_data['vrf'] = "/rest/v1/system/vrfs/" + vrf

    target_url = kwargs["url"] + "system/ports/%s" % port_name_percents
    put_data = json.dumps(port_data, sort_keys=True, indent=4)

    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Updating OSPFv3 %s Authentication for Port '%s' failed with status code %d"
              % (ospf_id, interface_name, response.status_code))
    else:
        print("SUCCESS: Updating OSPFv3 %s Authentication for Port '%s' succeeded" % (ospf_id, interface_name))


def _update_ospfv3_interface_authentication(vrf, ospf_id, interface_name, auth_type, digest_key, auth_pass, **kwargs):
    """
    Perform PUT calls to update an Interface with OSPFv3 to have authentication
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param interface_name: Alphanumeric name of the interface that will be attached to the OSPFv3 area
    :param auth_type: Alphanumeric type of authentication, chosen between 'md5', 'null', and 'text'
    :param digest_key: Integer between 1-255 that functions as the digest key for the authentication method
    :param auth_pass: Alphanumeric text for the authentication password.  Note that this will be translated to a
                      base64 String in the configuration and json.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    interface_name_percents = common_ops._replace_special_characters(interface_name)

    interface_data = interface.get_interface(interface_name, 2, "writable", **kwargs)

    interface_data['ospf_auth_type'] = auth_type
    interface_data['ospf_auth_md5_keys'] = {digest_key: auth_pass}
    interface_data['ospf_if_type'] = "ospf_iftype_broadcast"
    interface_data['routing'] = True
    interface_data['vrf'] = "/rest/v10.04/system/vrfs/" + vrf

    target_url = kwargs["url"] + "system/interfaces/%s" % interface_name_percents
    put_data = json.dumps(interface_data, sort_keys=True, indent=4)
    response = kwargs["s"].put(target_url, data=put_data, verify=False)

    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Updating OSPFv3 %s Authentication for Port '%s' failed with status code %d"
              % (ospf_id, interface_name, response.status_code))
    else:
        print("SUCCESS: Updating OSPFv3 %s Authentication for Port '%s' succeeded" % (ospf_id, interface_name))


def delete_ospfv3_id(vrf, ospf_id, **kwargs):
    """
    Perform a DELETE call to delete an OSPFv3 Router ID
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _delete_ospfv3_id_v1(vrf, ospf_id, **kwargs)
    else:   # Updated else for when version is v10.04
        _delete_ospfv3_id(vrf, ospf_id, **kwargs)


def _delete_ospfv3_id_v1(vrf, ospf_id, **kwargs):
    """
    Perform a DELETE call to delete an OSPFv3 Router ID
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ospf_list = get_ospfv3_routers(vrf, **kwargs)
    ospf_uri = "/rest/v1/system/vrfs/%s/ospfv3_routers/%s" % (vrf, ospf_id)
    ospf_id_key = str(ospf_id)

    if ospf_id_key in ospf_list and ospf_uri == ospf_list[ospf_id_key]:

        target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers/%s" % (vrf, ospf_id)

        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting OSPFv3 ID '%s' on VRF '%s' failed with status code %d"
                  % (ospf_id, vrf, response.status_code))
        else:
            print("SUCCESS: Deleting OSPFv3 ID %s on VRF '%s' succeeded" % (ospf_id, vrf))
    else:
        print("SUCCESS: No need to delete OSPFv3 ID %s on VRF '%s' since it doesn't exist"
              % (ospf_id, vrf))


def _delete_ospfv3_id(vrf, ospf_id, **kwargs):
    """
    Perform a DELETE call to delete an OSPFv3 Router ID
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    ospf_list = get_ospfv3_routers(vrf, **kwargs)
    ospf_uri = "/rest/v10.04/system/vrfs/%s/ospfv3_routers/%s" % (vrf, ospf_id)
    ospf_id_key = str(ospf_id)

    if ospf_id_key in ospf_list and ospf_uri == ospf_list[ospf_id_key]:

        target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers/%s" % (vrf, ospf_id)

        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting OSPFv3 ID '%s' on VRF '%s' failed with status code %d"
                  % (ospf_id, vrf, response.status_code))
        else:
            print("SUCCESS: Deleting OSPFv3 ID %s on VRF '%s' succeeded" % (ospf_id, vrf))
    else:
        print("SUCCESS: No need to delete OSPFv3 ID %s on VRF '%s' since it doesn't exist"
              % (ospf_id, vrf))


def delete_ospfv3_area(vrf, ospf_id, area_id, **kwargs):
    """
    Perform a DETELE call to remove an OSPFv3 Area for the specified OSPFv3 ID
    :param vrf: Alphanumeric name of the VRF the OSPFv3 ID belongs to
    :param ospf_id: OSPFv3 process ID between numbers 1-63
    :param area_id: Unique identifier as a string in the form of x.x.x.x
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    target_url = kwargs["url"] + "system/vrfs/%s/ospfv3_routers/%s/areas/%s" % (vrf, ospf_id, area_id)

    response = kwargs["s"].delete(target_url, verify=False, timeout=2)

    if not common_ops._response_ok(response, "DELETE"):
        print("FAIL: Deleting OSPFv3 Area '%s' on OSPFv3 ID %s failed with status code %d"
              % (area_id, ospf_id, response.status_code))
    else:
        print("SUCCESS: Deleting OSPFv3 Area '%s' succeeded on OSPFv3 ID %s" % (area_id, ospf_id))
