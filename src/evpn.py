import json
from src import common_ops

def get_evpn_info(**kwargs):
    """
    Perform a GET call to receive the EVPN information on the system
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Information
    """
    target_url = kwargs["url"] + "system/evpns"

    response = kwargs["s"].get(target_url, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("SUCCESS: Getting EVPN information replied with status code %d, no EVPN information exists"
              % response.status_code)
        evpn_info = []
    else:
        print("SUCCESS: Getting EVPN information succeeded")
        evpn_info = response.json()

    return evpn_info



def create_evpn_instance(**kwargs):
    """
    Perform POST calls to create an EVPN instance
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    current_evpn = get_evpn_info(**kwargs)

    if current_evpn:
        print("SUCCESS: No need to create EVPN instance since it already exists")
    else:
        evpn_data = {}
        target_url = kwargs["url"] + "system/evpns"

        post_data = json.dumps(evpn_data, sort_keys=True, indent=4)
        response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

        if not common_ops._response_ok(response, "POST"):
            print("FAIL: Creating EVPN Instance failed with status code %d" % response.status_code)
        else:
            print("SUCCESS: Creating EVPN Instance succeeded")


def delete_evpn_instance(**kwargs):
    """
    Perform DELETE calls to remove an EVPN instance
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    current_evpn = get_evpn_info(**kwargs)

    if current_evpn:
        target_url = kwargs["url"] + "system/evpns"
        response = kwargs["s"].delete(target_url, verify=False)

        if not common_ops._response_ok(response, "DELETE"):
            print("FAIL: Deleting EVPN Instance failed with status code %d" % response.status_code)
        else:
            print("SUCCESS: Deleting EVPN Instance succeeded")
    else:
        print("SUCCESS: No need to delete EVPN instance since it doesn't exists")


def get_evpn_vlan_list(**kwargs):
    """
    Perform a GET call to receive a list of VLANs associated with the EVPN instance
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: List of EVPN VLANs
    """
    target_url = kwargs["url"] + "system/evpns/evpn_vlans"

    response = kwargs["s"].get(target_url, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting list of all EVPN VLANs failed with status code %d"
              % response.status_code)
        evpn_vlan_list = []
    else:
        print("SUCCESS: Getting list of all EVPN VLANs succeeded")
        evpn_vlan_list = response.json()

    return evpn_vlan_list


def add_evpn_vlan(vlan_id, export_route=["auto"], import_route=["auto"], rd="auto", **kwargs):
    """
    Perform POST call to create an EVPN VLAN association
    Note that this functions has logic that works for both v1 and v10.04

    :param vlan_id: Integer representing the VLAN ID
    :param export_route: List of route targets to be exported from the VLAN in ASN:nn format, or auto.
    :param import_route: List of route targets to be imported from the VLAN in ASN:nn format, or auto.
    :param rd: Alphanumeric EVPN RD in ASN:nn format or IP:nn format, or auto.
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    evpn_data = {
        "export_route_targets": export_route,
        "import_route_targets": import_route,
        "rd": rd
    }
    if kwargs["url"].endswith("/v1/"):
        evpn_data.update({'vlan': '/rest/v1/system/vlans/%s' % vlan_id})
    else:
        # Else logic designed for v10.04 and later
        evpn_data.update({'vlan': '/rest/v10.04/system/vlans/%s' % vlan_id})

    target_url = kwargs["url"] + "system/evpns/evpn_vlans"

    post_data = json.dumps(evpn_data, sort_keys=True, indent=4)
    response = kwargs["s"].post(target_url, data=post_data, verify=False, timeout=2)

    if not common_ops._response_ok(response, "POST"):
        print("FAIL: Creating EVPN VLAN '%s' association failed with status code %d" % (vlan_id, response.status_code))
    else:
        print("SUCCESS: Creating EVPN VLAN '%s' association succeeded" % vlan_id)