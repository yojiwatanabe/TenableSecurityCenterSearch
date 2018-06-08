#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
processDump.py
This module reads in the file created by dumpPluginOut.py and creates a usable matrix out of the data after searching
for the queried data or without searching. This matrix is then used to create a html table and is written to a html
file. For searching this file reads a file given by the user and makes one query out of a line from the file. Then it
compares the list with the data output from processDump.py and gives us relevant data
'''


import json
import numpy as np
import pandas as pd


DUMP_FILE   = 'pluginText.dump'
OUTPUT_FILE = 'results.html'

# Plugin IDs for the special cases that are supported
SOFTWARE_ENUMERATION = '22869'


# 		loadData()
#
# Function to load JSON information from a file stream
# Input  - none
# Output - Python dictionary with data
def loadData():
    f       = open(DUMP_FILE, 'r')
    rawData = json.load(f)
    f.close()
    return rawData


# 		readInput()
#
# Function to load JSON information from a file stream
# Input  - none
# Output - Python dictionary with data
def readInput(infile):
    f    = open(infile, 'r')
    data = f.read().splitlines()
    return data


def specialCaseProcessing(data, inputData, resultMat, pluginID):
    if pluginID == SOFTWARE_ENUMERATION:
        for i, host in enumerate(data):
            for j, inputProgram in enumerate(inputData):
                tempList = ''
                for program in host['CONTENT']:
                    if inputProgram.lower() in program.lower():
                        tempList += program + '<br>'
                resultMat[i][j] = tempList

    return resultMat


# 		createMatrix()
#
# Creates and populates a table containing software information about desired software from given hosts
# Input  - data: Host data dict object, dict with host IP, DNS, Repository, and Content
#          inputData: List of programs to search for (optional for special query)
# Output - Numpy matrix object, where each row represents a different host, and each column represents a different
#          software. This means matrix elements at row row index [i] will have software information about the host with
#          ID = i + 1. Elements along column [j] will be lists of the software on line number j + 1 in input_file.
#          E.G. if the second line of my input file is 'ssh', resultMat[0][1] will be all ssh programs installed on host
#          with ID 1.
def createMatrix(data, inputData, pluginID):
    if inputData:
        resultMat = np.empty((len(data), len(inputData)), dtype=object)
    else:
        resultMat = np.empty((len(data), 1), dtype=object)
    if inputData:           # TODO move this to another function that will handle special cases, also send the pluginID
        resultMat = specialCaseProcessing(data, inputData, resultMat, pluginID)
    else:
        for i, host in enumerate(data):
            tempList = ''
            for program in host['CONTENT']:
                tempList += program + '<br>'
            resultMat[i] = tempList
    return resultMat


# 		getHostInfo()
#
# Returns information from the host in a pd.to_html friendly format (string)
# Input  - hostData: Dictionary array with host info like DNS, IP, and REPO
# Output - String array with all of the hosts' information
def getHostInfo(hostData):
    hostInfo = []
    for host in hostData:
        temp = (host['DNS'] + '<br>' + host['IP'] + '<br>' + host['REPO']).encode('utf-8')
        hostInfo.append(temp)

    return hostInfo


def makeDataFrame(data, inputData, pluginID):
    if inputData:
        if pluginID == SOFTWARE_ENUMERATION:
            progFrame = pd.DataFrame(data, index=range(1, len(data) + 1), columns=inputData)
    else:
        progFrame = pd.DataFrame(data, index=range(1, len(data) + 1), columns=['Plugin Output:'])

    return progFrame


# 		writeToHTML()
#
# Writes the given numpy matrix to a table in a HTML file
# Input  - data: Installed program information about each requested program. m rows by n columns, where each row is a
#                host, and each column is a program that was specified to search for
#          inputData: List of programs to search for
#          hostData: List with host information
# Output - none, out to file
def writeToHTML(data, inputData, hostData, pluginID):
    hostFrame = pd.DataFrame(hostData, index=range(1, len(data) + 1), columns=['Host Info:'])
    progFrame = makeDataFrame(data, inputData, pluginID)

    pdFrame = pd.concat([hostFrame, progFrame], axis=1)
    pd.set_option('display.max_colwidth', -1)
    pdFrame.to_html(OUTPUT_FILE, escape=False)

    return


# 		createTable()
#
# Drives the processDump module. Loads data, processes it as necessary, and converts it to an HTML table, and writes out
# to a file 'results.html'.
# Input  - pluginID: String containing the plugin ID to be queried
#          infile: Special query modifier, optional argument. See README for more
# Output - none, out to file
def createTable(pluginID, infile=''):
    data      = loadData()
    inputData = ''

    if infile:
        inputData = readInput(infile)
    resultMat = createMatrix(data, inputData, pluginID)
    hostInfo  = getHostInfo(data)

    writeToHTML(resultMat, inputData, hostInfo, pluginID)

    return
