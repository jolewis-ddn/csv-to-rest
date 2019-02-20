from bottle import route, run, template, response, static_file, debug
import csv
import json
import os.path
from os import listdir
from os.path import isfile, join
import urllib2
import urllib
import math
import Rally
import subprocess

# ---------------------------------------#
# Globals                                #
# ---------------------------------------#
_csv_filename = "unset"

# ---------------------------------------#
# Constants                              #
# ---------------------------------------#
REST_SERVER_URL_DE = 'http://localhost:8982'
REST_SERVER_URL_US = 'http://localhost:8983'
INCLUDE_UNASSIGNED = True
# INCLUDE_UNASSIGNED = False

# ---------------------------------------#
# Functions                              #
# ---------------------------------------#

def getCurrentSprint():
    return('ime-1.3 Sprint 1'.replace(" ", ""))

def buildHtml(content, header=""):
    return(''.join([getHtmlHeader(header), content, getHtmlFooter()]))

def getLinkbar():
    return(''.join(['<p>',
            '<button type="button" id="toggleCompAcc" class="linkBarItem btn btn-outline-primary btn-sm" title="Toggle Completed/Accepted item visibility">Hide Completed/Accepted<!--i id="toggleCompAccIcon" class="fas fa-check-square"></i--></button>',
            '<button type="button" id="toggleNoSprint" class="linkBarItem btn btn-outline-primary btn-sm" title="Show only items that have a sprint set">Hide No-Sprint-Set<!--i id="toggleNoSprintIcon" class="fas fa-clock"></i--></button>',
            '</p>']))

def getHtmlHeader(header):
    return('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css">' +
        '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>' + 
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js"></script>' + 
        '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js"></script>' + 
        '<script>$(function() {' + 
            'showCompAcc = true; showNoSprint = 0;' +
            '$("div#filterBlock").html("<EM>Filter</EM>: Showing all items"); ' +
            '$("button#toggleCompAcc").click(function() { ' + 
                'showCompAcc = !showCompAcc;' +
                '$("li").removeClass("liHide").addClass("liShow").show(); showNoSprint = 0; ' +
                '$("button#toggleNoSprint").removeClass("btn-primary").addClass("btn-outline-primary");'
                '$("button#toggleNoSprint").html("Show Only Sprint-Set");' +
                'if (showCompAcc) {' +
                    '$("div#filterBlock").html("<EM>Filter</EM>: Showing all items"); ' +
                    '$("button#toggleNoSprint").prop("disabled", false); ' +
                    '$("li.ss_Completed").removeClass("liHide").addClass("liShow"); ' +
                    '$("li.ss_Accepted").removeClass("liHide").addClass("liShow"); ' +
                    '$("button#toggleCompAcc").html("Hide Completed/Accepted");' +
                    '$("button#toggleCompAcc").removeClass("btn-primary").addClass("btn-outline-primary");'
                '} else {' +
                    '$("div#filterBlock").html("<EM>Filter</EM>: Showing only incomplete items"); ' +
                    '$("button#toggleNoSprint").prop("disabled", true); ' +
                    '$("li.ss_Completed").removeClass("liShow").addClass("liHide"); ' +
                    '$("li.ss_Accepted").removeClass("liShow").addClass("liHide"); ' +
                    '$("button#toggleCompAcc").html("Show Completed/Accepted");' +
                    '$("button#toggleCompAcc").removeClass("btn-outline-primary").addClass("btn-primary");'
                '}; ' + 
                '$("li.liHide").hide(300);' +
            '}); ' + 
            '$("button#toggleNoSprint").click(function() { ' + 
                '$("li").removeClass("liHide").addClass("liShow").show(); showCompAcc = true;' +
                '$("button#toggleCompAcc").removeClass("btn-primary").addClass("btn-outline-primary");'
                '$("button#toggleCompAcc").html("Hide Completed/Accepted");' +
                'if (showNoSprint >= 2) { showNoSprint = 0; } else { showNoSprint += 1; };' +
                'if (showNoSprint == 0) {' +
                    '$("div#filterBlock").html("<EM>Filter</EM>: Showing all items"); ' +
                    '$("button#toggleCompAcc").prop("disabled", false); ' +
                    '$("li.NoSprintSet").removeClass("liHide").addClass("liShow"); ' +
                    '$("button#toggleNoSprint").html("Show Only Sprint-Set"); ' +
                    '$("button#toggleNoSprint").attr("title", "Show only items that have a sprint set"); ' +
                '} else if (showNoSprint == 1) {' + 
                    '$("div#filterBlock").html("<EM>Filter</EM>: Showing only items that have a sprint set"); ' +
                    '$("button#toggleCompAcc").prop("disabled", true); ' +
                    '$("li.NoSprintSet").removeClass("liShow").addClass("liHide");' +
                    '$("button#toggleNoSprint").html("Show Only No-Sprint-Set"); ' +
                    '$("button#toggleNoSprint").attr("title", "Show only items that do NOT have a sprint set"); ' +
                '} else {' +
                    '$("div#filterBlock").html("<EM>Filter</EM>: Showing only items that do NOT have a sprint set"); ' +
                    '$("button#toggleCompAcc").prop("disabled", true); ' +
                    '$("li").addClass("liShow").removeClass("liHide");' +
                    '$("li.SprintSet").addClass("liHide").removeClass("liShow");' +
                    '$("button#toggleNoSprint").html("Disable Sprint Filter"); ' +
                    '$("button#toggleNoSprint").attr("title", "Show all items (i.e. disable filter)"); ' +
                '}; ' + 
                '$("li.liHide").hide(300);' + "\n" +
            '}); ' + 
            '}); $(document).ready(function(){ $(' + "'" + '[data-toggle="tooltip"]' + "'" + ').tooltip(); });</script>' + 
        '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">' + 
        '</head>' + 
        '<body>')

def getHtmlFooter():
    return('</body></html>')

def getClass(perc):
    if (perc == 0):
        return('danger')
    elif (perc < 60):
        return('warning')
    elif (perc < 80):
        return('info')
    elif (perc < 100):
        return('success')
    elif (perc == 100):
        return('primary')
    else:
        return('dark')

def getListItemClass(entry):
    return(' '.join(['ss_' + entry['ScheduleState'], (' '.join([entry['Iteration'].replace(" ", ""), "SprintSet"]) if entry['Iteration'] else "NoSprintSet")]))

def buildDEListItem(entry):
    return(''.join(["<LI ", "class='%s'" % (getListItemClass(entry)), ">", formatDE(entry), "</LI>"]))

def buildUSListItem(entry):
    return(''.join(["<LI ", "class='%s'" % (getListItemClass(entry)), ">", formatUS(entry), "</LI>"]))

def buildListItem(entry):
    return(buildUSListItem(entry))

def buildStatsTag(label, perc, suffix):
    # return('<button type="button" class="btn btn-%s">%s <span class="badge badge-light">%s%%</span></button>' % (getClass(perc), label, str(perc)))
    return('<span class="badge badge-pill badge-%s">%s</span>' % (getClass(perc), ''.join([label, str(perc), suffix])))

def setFilename(fn):
    global _csv_filename
    _csv_filename = fn

def getFilename():
    global _csv_filename
    # print("getFilename() called...")
    return(_csv_filename)

def getFilenameBlock():
    return("<p><em>Filename: %s</em></p>" % (getFilename()))

def getFilterBlock():
    return("<div id='filterBlock'></div>")

def getOwnerListJson(rel = -1):
    url = REST_SERVER_URL_US + '/list/Owner'
    if rel != -1:
        url += '/Release/' + urllib.quote(rel)
    resp = urllib2.urlopen(url)
    content = resp.read()
    jsonContent = json.loads(content)
    return(jsonContent)

def getOwnerDE(owner):
    owner_clean = urllib.quote(owner)
    if owner_clean == '""':
        owner_clean = ""
    base_url = REST_SERVER_URL_DE + '/get/Release/IME%201.3/Owner/'
    outurl = base_url + owner_clean
    getOwnerData = urllib2.urlopen(outurl).read()
    response = json.loads(getOwnerData)
    setFilename(response['meta']['filename'])
    return(response['data'])

def getOwnerUS(owner):
    owner_clean = urllib.quote(owner)
    if owner_clean == '""':
        owner_clean = ""
    base_url = REST_SERVER_URL_US + '/get/Release/IME%201.3/Owner/'
    outurl = base_url + owner_clean
    getOwnerData = urllib2.urlopen(outurl).read()
    response = json.loads(getOwnerData)
    setFilename(response['meta']['filename'])
    return(response['data'])

def getDataFileList():
    resp = urllib2.urlopen(REST_SERVER_URL_US + '/_admin/get/filenames').read()
    list = json.loads(resp)['data']
    setFilename(json.loads(resp)['meta']['filename'])
    return(list)

def getSelectedFile():
    resp = urllib2.urlopen(REST_SERVER_URL_US + '/_admin/get/selectedFile').read()
    list = json.loads(resp)['data']
    setFilename(list[0])
    return(list)

def getStats(us_list):
    response = ""
    total_count = len(us_list)
    estimated = 0
    est_total = 0
    sprints = {}
    for us in us_list:
        iter = us['Iteration'] if us['Iteration'] != "" else "none"
        if iter in sprints:
            sprints[iter] += 1
        else:
            sprints[iter] = 1
        est_total += float(us['PlanEstimate']) if us['PlanEstimate'] != "" else 0
        estimated += 1 if us['PlanEstimate'] != "" else 0
    if (estimated > 0):
        est_perc = int(round(100*((1.0*estimated)/total_count), 0))
    else:
        est_perc = 0
    label = "Estimated %s of %s (" % (str(estimated), str(int(total_count)))
    suffix = "%)"
    response = "Total est: %s; %s; Sprint breakdown: " % (str(est_total), buildStatsTag(label, est_perc, suffix))
    for sprint in sprints:
        response += "<B>%s</B>: %s; " % (sprint, str(sprints[sprint]))
    return response[:-2]

def buildStyleTag(entry):
    resp = ""
    if ((entry['ScheduleState'] == 'Completed') or (entry['ScheduleState'] == 'Accepted')):
        resp = "style='color:gray;'"
    return(resp)

def selectLatestFile():
    selectedFile = getSelectedFile()
    if getLatestFile() != selectedFile:
        url = REST_SERVER_URL_US + '/_admin/redirect/' + getLatestFile()
        print(url)
        resp = urllib2.urlopen(url).read()
        result = json.loads(resp)
        setFilename(result['meta']['filename'])
        print("Latest file is not selected... changing to " + getFilename())
        return(result['meta']['filename'])
    else:
        print("Latest file already selected... not changing..")
        return(selectedFile)

def getLatestFile():
    FILENAME_TEMPLATE = "IME-US-list-20????????????.csv"
    US_FILE_PREFIX = "IME-US-list-"
    FILE_TYPE = ".csv"
    start_date_pos = 12
    end_date_pos = 26
    files = getDataFileList()
    lastTimestamp = -1
    for f in files:
        # Ignore files that don't match IME-US-list-20????????????.csv
        if (len(f) == len(FILENAME_TEMPLATE) and f[0:12] == US_FILE_PREFIX and f[-4:] == FILE_TYPE):
            timestamp = int(f[start_date_pos:end_date_pos])
            if (timestamp > lastTimestamp):
                lastTimestamp = timestamp
    if (lastTimestamp > -1):
        return US_FILE_PREFIX + str(lastTimestamp) + FILE_TYPE
    else:
        return "Error - couldn't determine latest file"

def formatDE(entry):
    # print(entry)
    result = ''.join(["<span id='", entry['ID'], "' ", buildStyleTag(entry), "><a href='https://rally1.rallydev.com/#/9693447120d/search?keywords=", 
                     entry['ID'],
                     "' target='_blank'>", entry['ID'], "</a>: ", entry['Name'], " (", entry['Release'], "/", entry['ScheduleState'], "/Est.:", (entry['PlanEstimate'] if entry['PlanEstimate'] else "<em>not estimated</em>"), "/", (entry['Iteration'] if entry['Iteration'] else "<em>No sprint set</em>"), ")", "</span>"])
    return(result)

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

@route('/_admin/get/latestFile')
def adminGetLatestFile():
    return getLatestFile()

@route('/_admin/get/isLatestFileSelected')
def adminIsLatestFileSelected():
    return str(getLatestFile() == getSelectedFile())

@route('/_admin/get/selectedFile')
def adminGetSelectedFile():
    return getSelectedFile()

@route('/_admin/get/files')
def adminGetFiles():
    response = {}
    response['data'] = getDataFileList()
    return response

@route('/_admin/selectLatestFile')
def adminSelectLatestFile():
    selectLatestFile()
    return getFilename()

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
        # response += "<LI><A HREF='" + REST_SERVER_URL_US + "/get/Release/" + release_clean + "/Owner/" + (urllib.quote(k)) + "'>" + k + "</a> (" + str(getListContent_json[k]) + "; " + str(perc) + "%)"
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
    selectLatestFile()
    # Print for each owner
    ownerListResponse = getOwnerListJson(release)
    setFilename(ownerListResponse['meta']['filename'])
    response = "<H1>Owner Report for %s</H1>%s<P>%s</P>%s" % (release, getFilenameBlock(), getFilterBlock(), getLinkbar())
    response += "<UL>"
    for owner in sorted(ownerListResponse['data']):
        if (INCLUDE_UNASSIGNED or len(owner) > 0):
            if owner == '':
                owner = '""'
            ownerUS = getOwnerUS(owner)
            owner_clean = owner if owner != '""' else "Unassigned"
            response += "<LI><a href='/US/Owner/" + owner_clean + "' name='" + owner_clean + "'>" + owner_clean + "</a> (" + getStats(ownerUS) + ")"
            print("Fetching US for owner: " + owner + "!")
            if len(ownerUS) > 0:
                response += "<UL>"
                sortedList = {}
                for entry in ownerUS:
                    # sortedList[Rally.calculateRank(entry['DragAndDropRank'], 6)] = formatUS(entry)
                    sortedList[Rally.calculateRank(entry['DragAndDropRank'], 6)] = entry
                    # response += sortedList[key]
                for us in sorted(sortedList):
                    response += buildListItem(sortedList[us])
                response += "</UL>"
            response += "</LI>"
    return buildHtml(response)

@route('/US/Owner/<owner>')
def usByOwner(owner):
    selectLatestFile()
    getOwnerData_json = getOwnerUS(owner)
    response = "<H1>Item List for " + owner + "</H1>%s<P>%s</P><p>Stats: %s</p>%s<p><em>In priority order</em></p><UL>" % (getFilenameBlock(), getFilterBlock(), getStats(getOwnerData_json), getLinkbar())
    sortedList = {}
    for entry in getOwnerData_json:
        sortedList[Rally.calculateRank(entry['DragAndDropRank'], 6)] = buildListItem(entry)
    for key in sorted(sortedList):
        response += sortedList[key]
    response += "</UL>"
    return buildHtml(response)

@route('/DE/Owner/<owner>')
def deByOwner(owner):
    selectLatestFile()
    getOwnerData_json = getOwnerDE(owner)
    response = "<H1>Defect List for " + owner + "</H1>%s<P>%s</P><p>Stats: %s</p>%s<p><em>In priority order</em></p><UL>" % (getFilenameBlock(), getFilterBlock(), getStats(getOwnerData_json), getLinkbar())
    sortedList = {}
    for entry in getOwnerData_json:
        sortedList[Rally.calculateRank(entry['DragAndDropRank'], 6)] = buildDEListItem(entry)
    for key in sorted(sortedList):
        response += sortedList[key]
    response += "</UL>"
    return buildHtml(response)

@route('/updateDataFile')
def updateDataFile():
    subprocess.call(["python", "/home/jolewis/code/python/get-IME-US-list.py"], cwd="/home/jolewis/code/csv-to-rest/data")
    return buildHtml("CSV file update completed!")

# debug(True)
# run(host='0.0.0.0', port=8984, reloader=True)
run(host='0.0.0.0', port=8984)