from src import common_ops


def get_system_info(params={}, **kwargs):
    """
    Perform a GET call to get system information
    :param params: Dictionary of optional parameters for the GET request
    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Dictionary containing system information
    """
    target_url = kwargs["url"] + "system"

    response = kwargs["s"].get(target_url, params=params, verify=False)

    if not common_ops._response_ok(response, "GET"):
        print("FAIL: Getting dictionary of system information failed with status code %d"
              % response.status_code)
        system_info_dict = {}
    else:
        print("SUCCESS: Getting dictionary of system information succeeded")
        system_info_dict = response.json()

    return system_info_dict
