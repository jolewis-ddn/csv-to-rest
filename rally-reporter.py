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

@route('/')
def home():
    return '<UL><LI><a href="/owners">/owners</a> to list all owners<LI>/owners/Release/<release> to list all owners who have something in that specific release<LI>/US/Owner/<owner> to list all US assigned to <owner></UL>'

REST_SERVER_URL = 'http://localhost:8983'

def getOwnerListJson(rel = -1):
    url = REST_SERVER_URL + '/list/Owner'
    if rel != -1:
        url += '/Release/' + urllib.quote(rel)
    resp = urllib2.urlopen(url)
    content = resp.read()
    jsonContent = json.loads(content)
    return(jsonContent)

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
    response = "<H1>Owner List for " + release + "</H1>" + str(total_count) + " total records found assigned to the following owners:<UL>"
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
    owners = getOwnerListJson()
    for owner in owners:
        response += "<LI>" + owner + "</LI>"
    return response

def getOwnerUS(owner):
    owner_clean = urllib.quote(owner)
    base_url = REST_SERVER_URL + '/get/Release/IME%201.3/Owner/'
    outurl = base_url + owner_clean
    getOwnerData = urllib2.urlopen(outurl).read()
    return(json.loads(getOwnerData)['data'])

def formatUS(entry):
    result = ''.join(["<a href='https://rally1.rallydev.com/#/9693447120d/search?keywords=", 
                     entry['ID'],
                     "' target='_blank'>", entry['ID'], "</a>: ", entry['Name'], " (Feature: <a href='https://rally1.rallydev.com/#/9693447120d/search?keywords=", entry['Feature'], "' target='_blank'>", entry['Feature'], "</a>; Rank: ", str(Rally.calculateRank(entry['DragAndDropRank'], 6)), ")"])
    return(result)

@route('/US/OwnerReport/Release/<release>')
def usOwnerReportByRelease(release):
    # Print for each owner
    response = "<UL>"
    owners = getOwnerListJson(release)
    for owner in owners:
        if (len(owner) > 0):
            response += "<LI>" + owner
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
    response = "<H1>Item List for " + owner + "</H1><p><em>In priority order</em></p><UL>"
    sortedList = {}
    for entry in getOwnerData_json:
        sortedList[Rally.calculateRank(entry['DragAndDropRank'], 6)] = "<LI>" + formatUS(entry)
    for key in sorted(sortedList):
        response += sortedList[key]
    response += "</UL>"
    return response

run(host='0.0.0.0', port=8984)