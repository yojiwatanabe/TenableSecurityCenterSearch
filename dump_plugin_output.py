#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dump_plugin_output.py

This module works with Tenable Security Center's RESTful APIs to retrieve information about system scans. User is asked
to authenticate their session, after which they are able to get the plugin output from scans performed on hosts. This
module simply retrieves the data and saves it into 'pluginText.dump', after which it is processed by the 'processDump'
module and made human-friendly.
"""


import json
import getpass
# import ipaddress
import process_dump
from securitycenter import SecurityCenter5
from base64 import b64decode

HOST = 'sec-center-prod-01.uit.tufts.edu'
OUTPUT_FILE = 'pluginText.dump'
IP_LENGTH = 4


# 		login_sc()
#
# Function to open a connection with the specified Security Center 5 host. Asks user for their login information and
# then proceeds to try to establish an authenticated connection.
# Input  - none
# Output - authenticated SecurityCenter5 object
def login_sc():
    user = raw_input("Username: ")
    pw = getpass.getpass()
    sc = SecurityCenter5(HOST)

    sc.login(user, pw)
    return sc


# 		dump_data_repo_query()
#
# Function to save all queried information for hosts in a specified repository/repositories
# Input  - repo_list: string list with repositories to include in output
#          output: dictionary list with the plugin output from all hosts/repos with host information
# Output - dictionary list with the plugin output of hosts in the specified repository
# def dump_data_repo_query(repo_list, output):
#     case_num = 1
#     obj = []
#     temp_obj = {'ID': '', 'IP': '', 'DNS': '', 'REPO': '', 'CONTENT': []}
#     for case in output:
#         if case[u'repository'][u'name'] not in repo_list:
#             continue
#         temp_obj['ID'] = case_num
#         temp_obj['IP'] = case[u'ip']
#         temp_obj['MAC'] = case[u'macAddress']
#         temp_obj['DNS'] = case[u'dnsName']
#         temp_obj['REPO'] = case[u'repository'][u'name']
#         temp_obj['L_SEEN'] = case[u'lastSeen']
#         temp_obj['CONTENT'] = case[u'pluginText'].split("\n")

#         obj.append(temp_obj.copy())
#         case_num += 1

#     return obj


# 		dump_data_host_query()
#
# Function to save all queried information for the specified host/hosts
# Input  - host_list: string list with IP addresses of hosts to include in output
#          output: dictionary list with the plugin output from all hosts/repos with host information
# Output - dictionary list with the plugin output of hosts within the defined IP address range
# def dump_data_host_query(host_list, output):
#     case_num = 1
#     obj = []
#     temp_obj = {'ID': '', 'IP': '', 'DNS': '', 'REPO': '', 'CONTENT': []}
#     for case in output:
#         if case[u'ip'] not in host_list:
#             continue
#         temp_obj['ID'] = case_num
#         temp_obj['IP'] = case[u'ip']
#         temp_obj['MAC'] = case[u'macAddress']
#         temp_obj['DNS'] = case[u'dnsName']
#         temp_obj['REPO'] = case[u'repository'][u'name']
#         temp_obj['L_SEEN'] = case[u'lastSeen']
#         temp_obj['CONTENT'] = case[u'pluginText'].split('\n')

#         obj.append(temp_obj.copy())
#         case_num += 1

#     return obj


#       ip_in_range()
#
# Function to check if the given ip address is within a given range
# Input  - ip_min : String, with IP lower bound
#        - ip_max : String, with IP upper bound
#        - ip : String, with IP address to check
# Output -
# def ip_in_range(ip_min, ip_max, ip):
#     ip_min = ipaddress.IPv4Address(ip_min.decode('utf-8'))
#     ip_max = ipaddress.IPv4Address(ip_max.decode('utf-8'))
#     ip = ipaddress.IPv4Address(ip.decode('utf-8'))

#     if ip_min <= ip <= ip_max:
#         return True

#     return False


# 		dump_data_ip_range()
#
# Function to save all queried information that falls within the range of IPs
# Input  - ip_min: String, lower IP address boundary
#          ip_max: String, upper IP address boundary
#          output: dictionary list with the plugin output from all hosts/repos with host information
# Output - dictionary list with the plugin output of hosts within the defined IP address range
# def dump_data_ip_range(ip_min, ip_max, output):
#     case_num = 1
#     obj = []
#     temp_obj = {'ID': '', 'IP': '', 'DNS': '', 'REPO': '', 'CONTENT': []}
#     for case in output:
#         if ip_in_range(ip_min, ip_max, case[u'ip']):
#             temp_obj['ID'] = case_num
#             temp_obj['IP'] = case[u'ip']
#             temp_obj['MAC'] = case[u'macAddress']
#             temp_obj['DNS'] = case[u'dnsName']
#             temp_obj['REPO'] = case[u'repository'][u'name']
#             temp_obj['L_SEEN'] = case[u'lastSeen']
#             temp_obj['CONTENT'] = case[u'pluginText'].split('\n')

#             obj.append(temp_obj.copy())
#             case_num += 1

#     return obj

def repoID_gen(repo_list, repo_json):
    repo_IDs = []

    for repo_name in repo_list:
        for repos in repo_json['response']:
            if repo_name == repos['name']:
                repo_IDs.append(repos['id'])
                break

    return ",".join(repo_IDs)




# 		dump_plugin_data()
#
# Function that defines the flow in dumpPlugin.py. It opens a connection to Security Center, retrieves the information
# about the desired plugin, and dumps it all to a .dump file.
# Input  - plugin_id, a string of the plugin_id whose output is to be dumped
# Output - none, write to file
def dump_plugin_data(plugin_id, repo_list, host_list, ip_range, user, passwd):
    # Establish connection, retrieve data
    if user and passwd:
        sc = SecurityCenter5(HOST)
        sc.login(user, b64decode(passwd))
    else:
        sc = login_sc()
    arg_tuples = [('pluginID', '=', plugin_id)]

    if repo_list:
        repo_list = process_dump.read_input(repo_list)
        repo_data = sc.get('/repository')
        repo_comma_list = repoID_gen(repo_list, repo_data.json())
        arg_tuples.append(('repositoryIDs', '=', repo_comma_list))

    if host_list:
        hosts = process_dump.read_input(host_list)
        arg_tuples.append(('ip', '=', ",".join(hosts)))

    elif ip_range:
        arg_tuples.append(('ip', '=', ip_range))

    output = sc.analysis(*arg_tuples, tool = 'vulndetails')
    if not output:
        print 'No result found. Exitting program'
        exit(0)
    case_num = 1
    obj = []
    temp_obj = {'ID': '', 'IP': '', 'DNS': '', 'REPO': '', 'CONTENT': []}

    for case in output:
        temp_obj['ID'] = case_num
        temp_obj['IP'] = case[u'ip']
        temp_obj['MAC'] = case[u'macAddress']
        temp_obj['DNS'] = case[u'dnsName']
        temp_obj['REPO'] = case[u'repository'][u'name']
        temp_obj['L_SEEN'] = case[u'lastSeen']
        temp_obj['CONTENT'] = case[u'pluginText'].split('\n')

        obj.append(temp_obj.copy())
        case_num += 1

    # Convert to JSON, write to file
    ob = json.dumps(obj)
    f = open(OUTPUT_FILE, 'w')
    f.write(ob)
