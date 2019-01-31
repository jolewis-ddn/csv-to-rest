from bottle import route, run, template, response, static_file
import csv
import json
import os.path
from os import listdir
from os.path import isfile, join
import urllib2
import urllib
import math

@route('/')
def home():
    return '<UL><LI><a href="/owners">/owners</a> to list all owners<LI>/owners/Release/<release> to list all owners who have something in that specific release<LI>/US/Owner/<owner> to list all US assigned to <owner></UL>'

REST_SERVER_URL = 'http://localhost:8983'
@route('/owners')
def ownerList():
    response = ""
    getListResponse = urllib2.urlopen(REST_SERVER_URL + '/list/Owner')
    getListContent = getListResponse.read()
    getListContent_json = json.loads(getListContent)
    for k in getListContent_json:
        response += "<LI>" + k + " (" + str(getListContent_json[k]) + ")"
    return response

@route('/owners/Release/<release>')
def ownerList13(release):
    release_clean = urllib.quote(release)
    base_url = REST_SERVER_URL + '/list/Owner/Release/'
    outurl = base_url + release_clean
    getListResponse = urllib2.urlopen(outurl)
    getListContent = getListResponse.read()
    getListContent_json = json.loads(getListContent)
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

@route('/US/Owner/<owner>')
def usByOwner(owner):
    owner_clean = urllib.quote(owner)
    base_url = REST_SERVER_URL + '/get/Release/IME%201.3/Owner/'
    outurl = base_url + owner_clean
    getOwnerData = urllib2.urlopen(outurl).read()
    getOwnerData_json = json.loads(getOwnerData)
    response = "<H1>Item List for " + owner + "</H1><UL>"
    for entry in getOwnerData_json['data']:
        response += "<LI><a href='https://rally1.rallydev.com/#/9693447120d/search?keywords=" + entry['ID'] + "' target='_blank'>" + entry['ID'] + "</a>: " + entry['Name'] + " (Feature: " + entry['Feature'] + ")"
    response += "</UL>"
    return response

run(host='0.0.0.0', port=8984)