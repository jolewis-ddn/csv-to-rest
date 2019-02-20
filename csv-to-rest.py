from bottle import route, run, template, response, static_file, debug
import csv
import json
import os.path
from os import listdir
from os.path import isfile, join
import argparse

# Constants
LINE_RETURN_COUNT_MAX = 100 # How many records to return in a dump
CSVPATH_DEFAULT = './data/'
CSVFILENAME_DEFAULT = 'IME-US-list.csv'
PORT_DEFAULT = 8983

# Globals
csvpath = './data/'
csvreader = None

csvfields = []
csvcontents = []
csvdict = {}

# Fetch arguments
parser = argparse.ArgumentParser(description='Expose CSV via REST')
parser.add_argument('-d', '--datapath', type=str, nargs='?', default=CSVPATH_DEFAULT)
parser.add_argument('-f', '--filename', type=str, nargs='?', default=CSVFILENAME_DEFAULT)
parser.add_argument('-p', '--port', type=int, nargs='?', default=PORT_DEFAULT)
parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
parser.add_argument('-q', '--quiet', help='No output', action='store_true')
parser.add_argument('-z', '--dev-mode', help='Dev mode - debug mode & reloading', action='store_true')
args = parser.parse_args()

csvpath = args.datapath
csvfilename = args.filename
port = args.port
verbose = args.verbose
quiet = args.quiet
devmode = args.dev_mode

# Don't allow -q and -v
if verbose and quiet:
  print("Cannot set both 'verbose' and 'quiet' parameters")
  exit(101)

# Verify that the path exists
if (not os.path.exists(os.sep.join([csvpath, csvfilename]))):
  print("Default file (%s) was not found... Please check the filename and try again..." % (os.sep.join([csvpath, csvfilename])))
  exit(1)
else:
  print("Parsing %s" % (os.sep.join([csvpath, csvfilename])))

# Routes
@route('/')
def home():
  return 'home page'

@route('/_admin')
def admin():
  return '<h1>admin page</h1><h2>Filename</h2>' + csvfilename + '<h2># of records</h2>' + str(len(csvcontents) - 1) + "<h2>Fields</h2><UL><LI>" + '</LI><LI>'.join(csvfields) + "</LI></UL>\n" + "<h2>Available data files</h2>" + listDataFiles()

@route('/_admin/show/fields')
def adminShowfields():
  return "<UL><LI>" + '</LI><LI>'.join(csvcontents[0]) + "</LI></UL>"

@route('/_admin/get/fields')
def adminGetFields():
  response.add_header('Content-type', 'application/json')
  return json.dumps(csvcontents[0])

@route('/_admin/get/filenames')
def adminGetFilenames():
  filelist = getDataFiles()
  return buildResponseObjectSuccess(filelist)

@route('/_admin/get/selectedFile')
def adminGetSelectedFile():
  return buildResponseObjectSuccess(csvfilename)

@route('/_admin/redirect/<new_filename>')
def adminRedirect(new_filename):
  if (os.path.isfile(os.sep.join([csvpath, new_filename]))):
    read_file(new_filename)
    return buildResponseObjectSuccessOk()
  else:
    return buildResponseObjectError(["File not found"])

@route('/get/<id_value>')
def getIdValue(id_value):
  result = {}
  row = csvdict[id_value]
  fieldCtr = 0
  for f in row:
    result[csvfields[fieldCtr]] = f
    fieldCtr += 1
  return buildResponseObjectSuccess(result)

@route('/get/<field>/<value>')
def getFieldValue(field, value):
  result_rows = []
  # Get the # of the field you're searching for
  fieldnum = csvfields.index(field)
  for r in csvcontents:
    if r[fieldnum] == value: # Match, so save the row
      hit = {}
      fieldCtr = 0
      # Add field names
      for f in r:
        hit[csvfields[fieldCtr]] = f
        fieldCtr += 1
      result_rows.append(hit)
  return buildResponseObjectSuccess(result_rows)

@route('/get/<field1>/<value1>/<field2>/<value2>')
def getFieldValueDouble(field1, value1, field2, value2):
  # Handle empty field spec
  if value2 == '""':
    value2 = ""
  result_rows = []
  # Get the # of the field you're searching for
  fieldnum1 = csvfields.index(field1)
  fieldnum2 = csvfields.index(field2)
  for r in csvcontents:
    if (r[fieldnum1] == value1) and (r[fieldnum2] == value2): # Match, so save the row
      hit = {}
      fieldCtr = 0
      # Add field names
      for f in r:
        hit[csvfields[fieldCtr]] = f
        fieldCtr += 1
      result_rows.append(hit)
  return buildResponseObjectSuccess(result_rows)

@route('/get/<field1>/<value1>/<field2>/<value2>/<field3>/<value3>')
def getFieldValueTriple(field1, value1, field2, value2, field3, value3):
  result_rows = []
  # Get the # of the field you're searching for
  fieldnum1 = csvfields.index(field1)
  fieldnum2 = csvfields.index(field2)
  fieldnum3 = csvfields.index(field3)
  for r in csvcontents:
    if (r[fieldnum1] == value1) and (r[fieldnum2] == value2) and (r[fieldnum3] == value3): # Match, so save the row
      hit = {}
      fieldCtr = 0
      # Add field names
      for f in r:
        hit[csvfields[fieldCtr]] = f
        fieldCtr += 1
      result_rows.append(hit)
  return buildResponseObjectSuccess(result_rows)

@route('/count/<field>/<value>')
def countFieldValue(field, value):
  # Get the # of the field you're searching for
  fieldnum = csvfields.index(field)
  counter = 0
  for r in csvcontents:
    if r[fieldnum] == value: # Match, so increment the counter
      counter += 1
  return buildResponseObjectSuccessCount(counter)

@route('/count/<field1>/<value1>/<field2>/<value2>')
def countFieldValueTwo(field1, value1, field2, value2):
  # Get the # of the field you're searching for
  fieldnum1 = csvfields.index(field1)
  fieldnum2 = csvfields.index(field2)
  counter = 0
  for r in csvcontents:
    if (r[fieldnum1] == value1) and (r[fieldnum2] == value2): # Match, so increment the counter
      counter += 1
  return buildResponseObjectSuccessCount(counter)

@route('/count/<field1>/<value1>/<field2>/<value2>/<field3>/<value3>')
def countFieldValueThree(field1, value1, field2, value2, field3, value3):
  # Get the # of the field you're searching for
  fieldnum1 = csvfields.index(field1)
  fieldnum2 = csvfields.index(field2)
  fieldnum3 = csvfields.index(field3)
  counter = 0
  for r in csvcontents:
    if (r[fieldnum1] == value1) and (r[fieldnum2] == value2) and (r[fieldnum3] == value3): # Match, so increment the counter
      counter += 1
  return buildResponseObjectSuccessCount(counter)

@route('/list/<field>')
def listValuesByField(field):
  values = {}
  fieldnum = csvfields.index(field)
  for r in csvcontents:
    if not r[fieldnum] in values:
      values[r[fieldnum]] = 1
    else:
      values[r[fieldnum]] += 1
  return buildResponseObjectSuccess(values)

@route('/list/<field>/<filter>/<value>')
def listValuesByFieldFiltered(field, filter, value):
  values = {}
  fieldnum = csvfields.index(field)
  filternum = csvfields.index(filter)
  for r in csvcontents:
    if (r[filternum] == value):
      if not r[fieldnum] in values:
        values[r[fieldnum]] = 1
      else:
        values[r[fieldnum]] += 1
  return buildResponseObjectSuccess(values)

def read_file(fname):
  global csvfields, csvfilename, csvcontents, csvdict
  csvfields = []
  csvfilename = fname
  csvcontents = []
  csvdict = {}
  with open(os.sep.join([csvpath, csvfilename]), 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in csvreader:
      csvcontents.append(row)
      csvdict[row[0]] = row
    csvfields = csvcontents[0]

def buildBasicResponseObject(status, remainder = {}):
  response = {}
  response['meta'] = {}
  response['meta']['status'] = status
  response['meta']['path'] = csvpath
  response['meta']['filename'] = csvfilename
  response['meta'].update(remainder)
  return(response)

def buildResponseObjectSuccessCount(counter):
  result = buildBasicResponseObject('success')
  result['data'] = { 'count': counter }
  return result

def buildResponseObjectSuccessOk():
  result = buildBasicResponseObject('success')
  return result

def buildResponseObjectSuccess(data):
  result = buildBasicResponseObject('success', { 'hit_count': len(data) })
  result['data'] = data
  return result

def buildResponseObjectError(errors):
  result = buildBasicResponseObject('error', { 'error_count': len(errors) })
  result['errors'] = errors
  return result

def getDataFiles():
  global csvpath
  onlyfiles = [f for f in listdir(csvpath) if isfile(join(csvpath, f))]
  return sorted(onlyfiles, reverse=True)

def listDataFiles():
  result = "<UL>"
  filelist = getDataFiles()
  for f in filelist:
    result += "<LI><A HREF='/_admin/redirect/" + f + "'>" + f + "</A></LI>"
  result += "</UL>"
  return result

if __name__ == "__main__":
  if devmode:
    debug(True)
    print "In Developer Mode... debug(True)"

  if verbose or not quiet:
    print "Data path: %s" % (csvpath)
    print "Quiet? %s; Verbose? %s" % (quiet, verbose)

  read_file(csvfilename)

  if devmode:
    run(host='0.0.0.0', port=port, reloader=True)
  else:
    run(host='0.0.0.0', port=port)