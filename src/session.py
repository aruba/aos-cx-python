from src import common_ops

import getpass
import requests
import json


def login(base_url, username=None, password=None):
    """

    Perform a POST call to login and gain access to other API calls.
    If either username or password is not specified, user will be prompted to enter the missing credential(s).

    :param base_url: URL in main() function
    :param username: username
    :param password: password
    :return: requests.session object with loaded cookie jar
    """
    if username is None and password is None:
        username = input('Enter username: ')
        password = getpass.getpass()

    login_data = {"username": username, "password": password}

    s = requests.Session()
    try:
        response = s.post(base_url + "login", data=login_data, verify=False, timeout=5)
    except requests.exceptions.ConnectTimeout:
        print('ERROR: Error connecting to host: connection attempt timed out.')
        exit(-1)
    # Response OK check needs to be passed "PUT" since this POST call returns 200 instead of conventional 201
    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Login failed with status code %d" % response.status_code)
        exit(-1)
    else:
        print("SUCCESS: Login succeeded")
        return s


def logout(**kwargs):
    """
    Perform a POST call to logout and end session.

    :param kwargs:
        keyword s: requests.session object with loaded cookie jar
        keyword url: URL in main() function
    :return: Nothing
    """
    response = kwargs["s"].post(kwargs["url"] + "logout", verify=False)
    # Response OK check needs to be passed "PUT" since this POST call returns 200 instead of conventional 201
    if not common_ops._response_ok(response, "PUT"):
        print("FAIL: Logout failed with status code %d" % response.status_code)
    else:
        print("SUCCESS: Logout succeeded")
