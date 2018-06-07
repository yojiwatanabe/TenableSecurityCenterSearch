#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import getpass
from sys import exit
from securitycenter import SecurityCenter5

HOST         = 'sec-center-prod-01.uit.tufts.edu'
OUTPUT_FILE  = 'pluginText.dump'


# 		loginSC()
#
# Function to open a connection with the specified Security Center 5 host. Asks
# user for their login information and then proceeds to try to establish an 
# authenticated connection.
# Input  - none
# Output - SecurityCenter5 object of an authenticated connection
def loginSC():
    user = raw_input("Username: ")
    pw   = getpass.getpass()
    sc   = SecurityCenter5(HOST)

    try:
        sc.login(user, pw)
    except Exception as e:
        print str(e)
        exit(1)
    return sc

def dumpPluginData(pluginID):
    # Establish connection, retrieve data
    sc = loginSC()
    output = sc.analysis(('pluginID', '=', pluginID), tool='vulndetails')

    # Build JSON structure with data retrieved
    case_num = 1
    obj = []
    temp_obj = {'ID': '', 'IP': '', 'DNS': '', 'REPO': '', 'CONTENT': []}
    for case in output:
        temp_obj['ID']      = case_num
        temp_obj['IP']      = case[u'ip']
        temp_obj['DNS']     = case[u'dnsName']
        temp_obj['REPO']    = case[u'repository'][u'name']
        temp_obj['CONTENT'] = case[u'pluginText'].split("\n")

        obj.append(temp_obj.copy())
        case_num += 1

    # Convert to JSON, write to file
    ob = json.dumps(obj)
    f = open(OUTPUT_FILE, 'w')
    f.write(ob)