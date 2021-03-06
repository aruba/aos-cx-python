import json
from src import common_ops, port, interface


def create_vxlan_interface(port_name, source_ipv4=None, port_desc=None, dest_udp_port=4789, **kwargs):
    """
    Perform POST calls to create a VXLAN table entry for a logical L3 Interface. If the
    VXLAN Interface already exists and an IPv4 address is given, the function will update the IPv4 address.
    :param port_name: Alphanumeric Interface name
    :param source_ipv4: Source IPv4 address to assign to the VXLAN interface. Defaults to nothing if not specified.
    :param port_desc: Optional description for the interface. Defaults to nothing if not specified.
    :param dest_udp_port: Optional Destination UDP Port that the VXLAN will use.  Default is set to 4789
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        port._create_vxlan_port(port_name, source_ipv4, port_desc, dest_udp_port, **kwargs)
    else:   # Updated else for when version is v10.04
        interface._create_vxlan_interface(port_name, source_ipv4, port_desc, dest_udp_port, **kwargs)


def get_vni_list(**kwargs):
    """
    Perform a GET call to receive a list of Virtual Network IDs on the system
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: List of Virtual Network IDs
    """
    target_url = kwargs["url"] + "system/virtual_network_ids"

    response = kwargs["s"].get(target_url, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting list of all Virtual Network IDs failed with status code %d"
              % response.status_code)
        vni_list = []
    else:
        print("SUCCESS: Getting list of all Virtual Network IDs succeeded")
        vni_list = response.json()

    return vni_list


def add_vni_mapping(vni, vxlan, vlan, **kwargs):
    """
    Perform POST call to create a Virtual Network ID and Map it to VLANs for a supplied VXLAN
    :param vni: Integer representing the Virtual Network ID
    :param vxlan: Alphanumeric of the VXLAN that the VNI will be associated with
    :param vlan: VLAN that the VNI will be mapped to
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _add_vni_mapping_v1(vni, vxlan, vlan, **kwargs)
    else:   # Updated else for when version is v10.04
        _add_vni_mapping(vni, vxlan, vlan, **kwargs)


def _add_vni_mapping_v1(vni, vxlan, vlan, **kwargs):
    """
    Perform POST call to create a Virtual Network ID and Map it to VLANs for a supplied VXLAN
    :param vni: Integer representing the Virtual Network ID
    :param vxlan: Alphanumeric of the VXLAN that the VNI will be associated with
    :param vlan: VLAN that the VNI will be mapped to
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    current_vni = get_vni_list(**kwargs)

    if "/rest/v1/system/virtual_network_ids/vxlan_vni/%d" % vni not in current_vni:
        vni_data = {
          "id": vni,
          "interface": "/rest/v1/system/interfaces/%s" % vxlan,
          "type": "vxlan_vni",
          "vlan": "/rest/v1/system/vlans/%d" % vlan
        }

        target_url = kwargs["url"] + "system/virtual_network_ids"

        post_data = json.dumps(vni_data, sort_keys=True, indent=4)
        response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Creating VNI '%s' for VXLAN '%s' failed with status code %d"
                  % (vni, vxlan, response.status_code))
        else:
            print("SUCCESS: Creating VNI '%s' for VXLAN '%s' succeeded" % (vni, vxlan))
    else:
        print("SUCCESS: No need to create VNI '%s' for VXLAN '%s' as it already exists" % (vni, vxlan))


def _add_vni_mapping(vni, vxlan, vlan, **kwargs):
    """
    Perform POST call to create a Virtual Network ID and Map it to VLANs for a supplied VXLAN
    :param vni: Integer representing the Virtual Network ID
    :param vxlan: Alphanumeric of the VXLAN that the VNI will be associated with
    :param vlan: VLAN that the VNI will be mapped to
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    vni_list = get_vni_list(**kwargs)

    if "vxlan_vni,%d" % vni not in vni_list:
        vni_data = {
          "id": vni,
          "interface": "/rest/v10.04/system/interfaces/%s" % vxlan,
          "type": "vxlan_vni",
          "vlan": "/rest/v10.04/system/vlans/%d" % vlan
        }

        target_url = kwargs["url"] + "system/virtual_network_ids"

        post_data = json.dumps(vni_data, sort_keys=True, indent=4)
        response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Creating VNI '%s' for VXLAN '%s' failed with status code %d"
                  % (vni, vxlan, response.status_code))
        else:
            print("SUCCESS: Creating VNI '%s' for VXLAN '%s' succeeded" % (vni, vxlan))
    else:
        print("SUCCESS: No need to create VNI '%s' for VXLAN '%s' as it already exists" % (vni, vxlan))


def delete_vni_mapping(vni, **kwargs):
    """
    Perform DELETE call to remove a Virtual Network ID for a VXLAN
    :param vni: Integer representing the Virtual Network ID
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    if kwargs["url"].endswith("/v1/"):
        _delete_vni_mapping_v1(vni, **kwargs)
    else:   # Updated else for when version is v10.04
        _delete_vni_mapping(vni, **kwargs)


def _delete_vni_mapping_v1(vni, **kwargs):
    """
    Perform DELETE call to remove a Virtual Network ID for a VXLAN
    :param vni: Integer representing the Virtual Network ID
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    vni_list = get_vni_list(**kwargs)

    if "/rest/v1/system/virtual_network_ids/vxlan_vni/%d" % vni in vni_list:

        target_url = kwargs["url"] + "system/virtual_network_ids/vxlan_vni/%d" % vni
        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting VNI '%s' failed with status code %d" % (vni, response.status_code))
        else:
            print("SUCCESS: Deleting VNI '%s' succeeded" % vni)
    else:
        print("SUCCESS: No need to delete VNI '%s' since it doesn't exist" % vni)


def _delete_vni_mapping(vni, **kwargs):
    """
    Perform DELETE call to remove a Virtual Network ID for a VXLAN
    :param vni: Integer representing the Virtual Network ID
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    vni_list = get_vni_list(**kwargs)

    if "vxlan_vni,%d" % vni in vni_list:
        target_url = kwargs["url"] + "system/virtual_network_ids/vxlan_vni,%d" % vni
        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting VNI '%s' failed with status code %d" % (vni, response.status_code))
        else:
            print("SUCCESS: Deleting VNI '%s' succeeded" % vni)
    else:
        print("SUCCESS: No need to delete VNI '%s' since it doesn't exist" % vni)
