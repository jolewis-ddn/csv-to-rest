from bottle import route, run, template, response, static_file
import csv
import json
import os.path
from os import listdir
from os.path import isfile, join

LINE_RETURN_COUNT_MAX = 100 # How many records to return in a dump

csvpath = './data/'
csvfilename = 'IME-US-list.csv'
csvreader = None

csvfields = []
csvcontents = []
csvdict = {}

@route('/')
def home():
  return 'home page'

@route('/_admin')
def admin():
  return '<h1>admin page</h1><h2># of records</h2>' + str(len(csvcontents) - 1) + "<h2>Fields</h2><UL><LI>" + '</LI><LI>'.join(csvfields) + "</LI></UL>\n" + "<h2>Available data files</h2>" + listDataFiles()

@route('/_admin/showfields')
def adminShowfields():
  return "<UL><LI>" + '</LI><LI>'.join(csvcontents[0]) + "</LI></UL>"

@route('/_admin/getFields')
def admingGetFields():
  response.add_header('Content-type', 'application/json')
  return json.dumps(csvcontents[0])

@route('/_admin/dump')
def adminDump():
  return static_file(csvfilename, root=csvpath)

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
  return(buildResponseObjectSuccess(result_rows))

@route('/get/<field1>/<value1>/<field2>/<value2>')
def getFieldValueDouble(field1, value1, field2, value2):
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
  return(buildResponseObjectSuccess(result_rows))

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
  return(buildResponseObjectSuccess(result_rows))

@route('/count/<field>/<value>')
def countFieldValue(field, value):
  result_rows = []
  # Get the # of the field you're searching for
  fieldnum = csvfields.index(field)
  counter = 0
  for r in csvcontents:
    if r[fieldnum] == value: # Match, so increment the counter
      counter += 1
  return(buildResponseObjectSuccessCount(counter))

@route('/count/<field1>/<value1>/<field2>/<value2>')
def countFieldValueTwo(field1, value1, field2, value2):
  # Get the # of the field you're searching for
  fieldnum1 = csvfields.index(field1)
  fieldnum2 = csvfields.index(field2)
  counter = 0
  for r in csvcontents:
    if (r[fieldnum1] == value1) and (r[fieldnum2] == value2): # Match, so increment the counter
      counter += 1
  return(buildResponseObjectSuccessCount(counter))

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
  return(buildResponseObjectSuccessCount(counter))

@route('/_admin/redirect/<new_filename>')
def redirect(new_filename):
  if (os.path.isfile(csvpath + new_filename)):
    read_file(new_filename)
    return buildResponseObjectSuccessOk()
  else:
    return buildResponseObjectError(["File not found"])

@route('/_admin/reload')
def reload():
  return '<em>not yet implemented</em>'

def read_file(fname):
  global csvfields, csvfilename, csvcontents, csvdict
  csvfields = []
  csvfilename = fname
  csvcontents = []
  csvdict = {}
  with open(csvpath + csvfilename, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in csvreader:
      csvcontents.append(row)
      csvdict[row[0]] = row
    csvfields = csvcontents[0]

def buildResponseObjectSuccessCount(counter):
  result = {}
  result['meta'] = {}
  result['meta']['status'] = 'success'
  result['data'] = { 'count': counter }
  return result

def buildResponseObjectSuccessOk():
  result = {}
  result['meta'] = {}
  result['meta']['status'] = 'success'
  return result

def buildResponseObjectSuccess(data):
  result = {}
  result['meta'] = {}
  result['meta']['status'] = 'success'
  result['meta']['hit_count'] = len(data)
  result['data'] = data
  return result

def buildResponseObjectError(errors):
  result = {}
  result['meta'] = {}
  result['meta']['status'] = 'error'
  result['meta']['error_count'] = len(errors)
  result['errors'] = errors
  return result

def listDataFiles():
  global csvpath
  onlyfiles = [f for f in listdir(csvpath) if isfile(join(csvpath, f))]
  result = "<UL>"
  for f in onlyfiles:
    result += "<LI><A HREF='/_admin/redirect/" + f + "'>" + f + "</A></LI>"
  result += "</UL>"
  return result

read_file(csvfilename)

run(host='0.0.0.0', port=8983)