#!/usr/bin/env python3
"""
This workflow performs the following steps:
1. Create a queue profile
    Ex:
      qos queue-profile QOS_PROFILE_OUT

2. Add entries to queue profile
    Ex:
      qos queue-profile QOS_PROFILE_OUT
          map queue 0 local-priority 0
          map queue 1 local-priority 1
          map queue 2 local-priority 2
          map queue 3 local-priority 3
          map queue 4 local-priority 4
          map queue 5 local-priority 6
          map queue 6 local-priority 7
          map queue 7 local-priority 5
          name queue 7 VOICE

3. Create a schedule profile
    Ex:
      qos schedule-profile QOS_OUT

4. Add entries to schedule profile
    Ex:
      qos schedule-profile QOS_OUT
          dwrr queue 0 weight 1
          dwrr queue 1 weight 2
          dwrr queue 2 weight 3
          dwrr queue 3 weight 4
          dwrr queue 4 weight 5
          dwrr queue 5 weight 6
          dwrr queue 6 weight 7
          strict queue 7

3. Apply the queue and schedule profiles globally
      Ex:
        apply qos queue-profile QOS_PROFILE_OUT schedule-profile QOS_OUT

4. Set QoS trust mode globally to DSCP
      Ex:
        qos trust dscp

5. Remap DSCP code points' priorities
      Ex:
        qos dscp-map 40 local-priority 6 color green name CS5
        qos dscp-map 41 local-priority 6 color green
        qos dscp-map 42 local-priority 6 color green
        qos dscp-map 43 local-priority 6 color green
        qos dscp-map 44 local-priority 6 color green
        qos dscp-map 45 local-priority 6 color green
        qos dscp-map 47 local-priority 6 color green

6. Create traffic class and traffic class entry
    a. Create empty traffic class
    b. Create traffic class entry
    c. Version-up the traffic class
      Ex:
        class ip wifi-port-qos-0
            10 match any any any

7. Create classifier policy and classifier policy entry
    a. Create empty classifier policy
    b. Create classifier policy entry
    c. Set action on classifier policy entry
    d. Version-up the classifier policy
      Ex:
        policy wifi-port-qos-0
            10 class ip wifi-port-qos-0 action pcp 0 action dscp CS0

8. Create LAGs and set trust mode on them
    a. Create LAG
    b. Set trust mode on LAG interface
      Ex:
        interface lag 10
            no shutdown
            no routing
            vlan trunk native 1
            vlan trunk allowed all
            lacp mode passive
            qos trust dscp
        interface lag 11
            no shutdown
            no routing
            vlan trunk native 1
            vlan trunk allowed all
            lacp mode passive
            qos trust cos
        interface 1/1/1
            no shutdown
            lag 10
        interface 1/1/2
            no shutdown
            lag 10
        interface 1/1/3
            no shutdown
            lag 11
        interface 1/1/4
            no shutdown
            lag 11

9. Create L2 interface and set the port's rate limits
    a. Create L2 interface
    b. Set port's rate limits
      Ex:
        interface 1/1/20
            no shutdown
            rate-limit broadcast 50 pps
            rate-limit multicast 40 pps
            no routing
            vlan access 1

10. Create L2 interface and update the port's policy
    a. Create L2 interface
    b. Update the port's policy
      Ex:
        interface 1/1/29
            no shutdown
            no routing
            vlan access 1
            apply policy wifi-port-qos-0 in


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
from src import session, qos, system, lag, interface

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

        system_info_dict = system.get_system_info(**session_dict)

        platform_name = system_info_dict['platform_name']

        # Create empty queue profile
        qos.create_queue_profile(data['queueprofilename'], **session_dict)

        # Add entries to queue profile
        for i in range(0, 5):
            qos.create_queue_profile_entry(data['queueprofilename'], i, [i], **session_dict)
        for i in range(5, 7):
            qos.create_queue_profile_entry(data['queueprofilename'], i, [i + 1], **session_dict)
        qos.create_queue_profile_entry(data['queueprofilename'], 7, [5], desc="VOICE", **session_dict)

        # Create empty schedule profile
        qos.create_schedule_profile(data['scheduleprofilename'], **session_dict)

        # Add entries to schedule profile
        # Scheduling algorithms: 8400 uses WFQ; other platforms use DWRR
        if "8400" in platform_name:
            algorithm = "wfq"
        else:
            algorithm = "dwrr"

        for i in range(0, 7):
            qos.create_schedule_profile_entry(data['scheduleprofilename'], i, algorithm, weight=i + 1, **session_dict)
        qos.create_schedule_profile_entry(data['scheduleprofilename'], 7, "strict", **session_dict)

        # Apply profiles globally
        qos.apply_profiles_globally(data['queueprofilename'], data['scheduleprofilename'], **session_dict)

        # Set trust globally
        qos.set_trust_globally('dscp', **session_dict)

        # Remap DSCP code points' priorities
        qos.remap_dscp_entry(40, color='green', local_priority=6, desc='CS5', **session_dict)
        for i in range(41, 46):
            qos.remap_dscp_entry(i, color='green', local_priority=6, **session_dict)
        qos.remap_dscp_entry(47, color='green', local_priority=6, **session_dict)

        # Create empty traffic class
        qos.create_traffic_class(data['trafficclass']['name'], data['trafficclass']['type'], **session_dict)

        # Create traffic class entry
        qos.create_traffic_class_entry(data['trafficclass']['name'], data['trafficclass']['type'], "match", 10,
                                       **session_dict)

        # Version-up the traffic class to complete the change
        qos.update_traffic_class(data['trafficclass']['name'], data['trafficclass']['type'], **session_dict)

        # Create empty classifier policy
        qos.create_policy(data['policy']['name'], **session_dict)

        # Add entry to classifier policy
        qos.create_policy_entry(data['policy']['name'], data['trafficclass']['name'], data['trafficclass']['type'],
                                10, **session_dict)

        # Set action on the policy entry
        qos.create_policy_entry_action(data['policy']['name'], 10, dscp=0, pcp=0, **session_dict)

        # Version-up the policy to complete the change
        qos.update_policy(data['policy']['name'], **session_dict)

        # Create LAGs and set trust mode on the LAG interfaces
        for lag_data in data['lags']:
            lag.create_l2_lag_interface(lag_data['name'], lag_data['interfaces'], **session_dict)
            qos.set_trust_interface(lag_data['name'], lag_data['qostrust'], **session_dict)

        # Create L2 interface
        interface.add_l2_interface(data['portrateinterface'], **session_dict)

        if platform_name.startswith("6"):
            unknown_unicast_limit = None
            unknown_unicast_units = None
        else:
            unknown_unicast_limit = 30
            unknown_unicast_units = 'pps'

        # Set rate limits on the L2 interface
        qos.update_port_rate_limits(data['portrateinterface'], broadcast_limit=50, broadcast_units='pps',
                                    multicast_limit=40, multicast_units='pps',
                                    unknown_unicast_limit=unknown_unicast_limit,
                                    unknown_unicast_units=unknown_unicast_units, **session_dict)

        # Create L2 interface
        interface.add_l2_interface(data['portpolicyinterface'], **session_dict)

        # Apply policy to L2 interface
        qos.update_port_policy(data['portpolicyinterface'], data['policy']['name'], **session_dict)

    except Exception as error:
        print('Ran into exception: {}. Logging out..'.format(error))
    session.logout(**session_dict)


if __name__ == '__main__':
    main()
