#!/usr/bin/env python3
"""
This workflow performs the following steps:
1. Remove global application of the queue and schedule profiles
      Ex:
        No apply qos queue-profile QOS_PROFILE_OUT schedule-profile QOS_OUT

2. Delete queue profile
    a. Delete queue profile entries
    b. Delete queue profile
      Ex:
        qos queue-profile QOS_PROFILE_OUT
            no map queue 0 local-priority 0
            no map queue 1 local-priority 1
            no map queue 2 local-priority 2
            no map queue 3 local-priority 3
            no map queue 4 local-priority 4
            no map queue 5 local-priority 6
            no map queue 6 local-priority 7
            no map queue 7 local-priority 5
            no name queue 7 VOICE

        no qos queue-profile QOS_PROFILE_OUT

3. Delete schedule profile
    a. Delete schedule profile entries
    b. Delete schedule profile
      Ex:
        qos schedule-profile QOS_OUT
            no dwrr queue 0 weight 1
            no dwrr queue 1 weight 2
            no dwrr queue 2 weight 3
            no dwrr queue 3 weight 4
            no dwrr queue 4 weight 5
            no dwrr queue 5 weight 6
            no dwrr queue 6 weight 7
            no strict queue 7

        no qos schedule-profile QOS_OUT

4. Remove global setting of QoS trust mode
      Ex:
        no qos trust dscp

5. Reset DSCP code point mapping to default
      Ex:
        no qos dscp-map 40
        no qos dscp-map 41
        no qos dscp-map 42
        no qos dscp-map 43
        no qos dscp-map 44
        no qos dscp-map 45
        no qos dscp-map 47

6. Delete classifier policy
    a. Delete action on policy entry
    b. Delete policy entry
    c. Version-up the policy
    d. Delete policy
      Ex:
        no policy wifi-port-qos-0
            no 10

7. Delete traffic class
    a. Delete traffic class entry
    b. Version-up the traffic class
    b. Delete traffic class
      Ex:
        no class ip wifi-port-qos-0
            no 10

8. Delete LAGs
    a. Clear trust mode on LAG interface
    b. Delete LAG interface
        no interface lag 10
            no qos trust dscp
        no interface lag 11
            no qos trust cos
        interface 1/1/1
            no lag 10
        interface 1/1/2
            no lag 10
        interface 1/1/3
            no lag 11
        interface 1/1/4
            no lag 11

9. Reset L2 interface
    a. Remove port policy from L2 interface
    b. Initialize L2 interface
      Ex:
        interface 1/1/20
            no shutdown
            no rate-limit broadcast
            no rate-limit multicast
            no routing
            vlan access 1

10. Reset L2 interface
    a. Remove port rate limits from L2 interface
    b. Initialize L2 interface
      Ex:
        interface 1/1/29
            no shutdown
            no routing
            vlan access 1
            no apply policy wifi-port-qos-0 in


Preconditions:
Must have run the configure_qos workflow or have the equivalent settings.
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
from src import qos
from src import lag
from src import interface

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    data = yaml_ops.read_yaml("qos_data.yaml")

    if not data['switchip']:
        data['switchip'] = input("Switch IP Address: ")

    if data['bypassproxy']:
        os.environ['no_proxy'] = data['switchip']
        os.environ['NO_PROXY'] = data['switchip']

    base_url = "https://{0}/rest/{1}/".format(data['switchip'], data['version'])
    try:
        session_dict = dict(s=session.login(base_url, data['username'], data['password']), url=base_url)

        #  Remove global application of QoS queue profile and schedule profile
        qos.unapply_profiles_globally(**session_dict)

        # Delete queue profile entries
        for i in range(0, 8):
            qos.delete_queue_profile_entry(data['queueprofilename'], i, **session_dict)

        # Delete queue profile
        qos.delete_queue_profile(data['queueprofilename'], **session_dict)

        # Delete schedule profile entries
        for i in range(0, 8):
            qos.delete_schedule_profile_entry(data['scheduleprofilename'], i, **session_dict)

        # Delete schedule profile
        qos.delete_schedule_profile(data['scheduleprofilename'], **session_dict)

        #  Remove global setting of QoS trust mode
        qos.clear_trust_globally(**session_dict)

        # Reset DSCP code points to defaults
        qos.reset_dscp_entry(40, **session_dict)
        for i in range(41, 46):
            qos.reset_dscp_entry(i, **session_dict)
        qos.reset_dscp_entry(47, **session_dict)

        # Delete action on policy entry
        qos.delete_policy_entry_action(data['policy']['name'], 10, **session_dict)

        # Delete policy entry
        qos.delete_policy_entry(data['policy']['name'], 10, **session_dict)

        # Version-up the policy to complete the change
        qos.update_policy(data['policy']['name'], **session_dict)

        # Delete classifier policy
        qos.delete_policy(data['policy']['name'], **session_dict)

        # Delete traffic class entry
        qos.delete_traffic_class_entry(data['trafficclass']['name'], data['trafficclass']['type'], 10, **session_dict)

        # Version-up the traffic class to complete the change
        qos.update_traffic_class(data['trafficclass']['name'], data['trafficclass']['type'], **session_dict)

        # Delete traffic class
        qos.delete_traffic_class(data['trafficclass']['name'], data['trafficclass']['type'], **session_dict)

        # Clear trust mode on LAG interfaces and delete LAG interfaces
        for lag_data in data['lags']:
            qos.clear_trust_interface(lag_data['name'], **session_dict)

            lag.delete_lag_interface(lag_data['name'], lag_data['interfaces'], **session_dict)

        # Clear policy from L2 interface
        qos.clear_port_policy(data['portpolicyinterface'], **session_dict)

        interface.initialize_interface(data['portpolicyinterface'], **session_dict)

        # Clear rate limits from L2 interface
        qos.clear_port_rate_limits(data['portrateinterface'], **session_dict)

        interface.initialize_interface(data['portrateinterface'], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
