from bottle import route, run, template, response, static_file
import csv
import json
import os.path
from os import listdir
from os.path import isfile, join
import urllib2
import urllib
import math
import Rally

# Globals
_csv_filename = "unset"
# Constants
REST_SERVER_URL = 'http://localhost:8983'
INCLUDE_UNASSIGNED = True
# INCLUDE_UNASSIGNED = False

# ---------------------------------------#
# Functions                              #
# ---------------------------------------#

def setFilename(fn):
    global _csv_filename
    _csv_filename = fn

def getFilename():
    global _csv_filename
    print("getFilename() called...")
    return(_csv_filename)

def getFilenameBlock():
    return("<p><em>Filename: %s</em></p>" % (getFilename()))

def getOwnerListJson(rel = -1):
    url = REST_SERVER_URL + '/list/Owner'
    if rel != -1:
        url += '/Release/' + urllib.quote(rel)
    resp = urllib2.urlopen(url)
    content = resp.read()
    jsonContent = json.loads(content)
    return(jsonContent)

def getOwnerUS(owner):
    owner_clean = urllib.quote(owner)
    if owner_clean == '""':
        owner_clean = ""
    base_url = REST_SERVER_URL + '/get/Release/IME%201.3/Owner/'
    outurl = base_url + owner_clean
    getOwnerData = urllib2.urlopen(outurl).read()
    response = json.loads(getOwnerData)
    setFilename(response['meta']['filename'])
    return(response['data'])

def buildStyleTag(entry):
    resp = ""
    if (entry['ScheduleState'] == 'Completed'):
        resp = "style='color:gray;'"
    return(resp)

def formatUS(entry):
    # print(entry)
    result = ''.join(["<span id='", entry['ID'], "' ", buildStyleTag(entry), "><a href='https://rally1.rallydev.com/#/9693447120d/search?keywords=", 
                     entry['ID'],
                     "' target='_blank'>", entry['ID'], "</a>: ", entry['Name'], " (<a href='https://rally1.rallydev.com/#/9693447120d/search?keywords=", entry['Feature'], "' target='_blank'>", entry['Feature'], "</a>/<!-- Rank: ", str(Rally.calculateRank(entry['DragAndDropRank'], 6)), ";-->", entry['Release'], "/", entry['ScheduleState'], "/Est.:", (entry['PlanEstimate'] if entry['PlanEstimate'] else "<em>not estimated</em>"), "/", (entry['Iteration'] if entry['Iteration'] else "<em>No sprint set</em>"), ")", "</span>"])
    return(result)

# ---------------------------------------#
# Routes                                 #
# ---------------------------------------#
@route('/')
def home():
    return '<UL><LI><a href="/owners">/owners</a> to list all owners<LI>/owners/Release/<release> to list all owners who have something in that specific release<LI>/US/Owner/<owner> to list all US assigned to <owner></UL>'

@route('/owners')
def ownerList():
    getListContent_json = getOwnerListJson()
    response = ""
    for k in getListContent_json:
        response += "<LI>" + k + " (" + str(getListContent_json[k]) + ")"
    return response

@route('/owners/Release/<release>')
def ownerList13(release):
    getListContent_json = getOwnerListJson(release)
    total_count = sum(getListContent_json.values())
    response = "<H1>Owner List for " + release + "</H1>%" + str(total_count) + " total records found assigned to the following owners:<UL>" % (getFilenameBlock())
    for k in getListContent_json:
        perc = 100.0*(100*((1.0*getListContent_json[k])/total_count))/100
        # TODO: Fix rounding error... the next line doesn't work
        # perc = math.floor(perc/100)
        # response += "<LI><A HREF='" + REST_SERVER_URL + "/get/Release/" + release_clean + "/Owner/" + (urllib.quote(k)) + "'>" + k + "</a> (" + str(getListContent_json[k]) + "; " + str(perc) + "%)"
        response += "<LI><A HREF='/US/Owner/" + (urllib.quote(k)) + "'>" + k + "</a> (" + str(getListContent_json[k]) + "; " + str(perc) + "%)"
    response += "</UL>"
    return response

@route('/US/OwnerReport')
def usOwnerReport():
    # Print for each owner
    response = "<UL>"
    ownerResponse = getOwnerListJson()
    setFilename(ownerResponse['meta']['filename'])
    for owner in ownerResponse['data']:
        response += "<LI>" + owner + "</LI>"
    return response

@route('/US/OwnerReport/Release/<release>')
def usOwnerReportByRelease(release):
    # Print for each owner
    ownerListResponse = getOwnerListJson(release)
    setFilename(ownerListResponse['meta']['filename'])
    response = "<H1>Owner Report for %s</H1>%s" % (release, getFilenameBlock())
    response += "<UL>"
    for owner in sorted(ownerListResponse['data']):
        if (INCLUDE_UNASSIGNED or len(owner) > 0):
            if owner == '':
                owner = '""'
            response += "<LI><a name='" + owner + "'>" + (owner if owner != '""' else "Unassigned") + "</a>"
            print("Fetching US for owner: " + owner + "!")
            ownerUS = getOwnerUS(owner)
            if len(ownerUS) > 0:
                response += "<UL>"
                sortedList = {}
                for entry in ownerUS:
                    sortedList[Rally.calculateRank(entry['DragAndDropRank'], 6)] = formatUS(entry)
                    # response += sortedList[key]
                for us in sorted(sortedList):
                    response += "<LI>" + sortedList[us] + "</LI>"
                response += "</UL>"
            response += "</LI>"
    return response

@route('/US/Owner/<owner>')
def usByOwner(owner):
    getOwnerData_json = getOwnerUS(owner)
    response = "<H1>Item List for " + owner + "</H1>%s<p><em>In priority order</em></p><UL>" % (getFilenameBlock())
    sortedList = {}
    for entry in getOwnerData_json:
        sortedList[Rally.calculateRank(entry['DragAndDropRank'], 6)] = "<LI>" + formatUS(entry)
    for key in sorted(sortedList):
        response += sortedList[key]
    response += "</UL>"
    return response

run(host='0.0.0.0', port=8984)