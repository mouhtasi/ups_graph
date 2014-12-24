import requests
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import pickle
import os.path

def login(session):
  login_form = {"value(action)" : "Login", "value(username)" : "admin",
                "value(password)" : "admin", "value(persistentCookie)" : "true",
                "value(button)" : "Login"}

  login_page = session.post("http://127.0.0.1:3052/agent/index",
                             data=login_form)

  if login_page.status_code == requests.codes.ok:
    return login_page
  else:
    return False

def retrieve_xml(session, num_requests):
  """Get the past 'num_requests' log entries"""
  headers = {'content-type': 'application/xml'}
  payload = '''<?xml version="1.0" encoding="UTF-8" ?>
            <ppbe>
            <target>
            <command>logs.status.present</command>
            </target>
            <inquire>
            <query>
            <state current="0" lastRequest="false" next="true" sizePerRequest="''' + num_requests + '''" />
            <filter>
            <sizePerPage>10000</sizePerPage>
            <date>
            <begin>-1</begin>
            <end>-1</end>
            </date>
            <time>
            <begin>-1</begin>
            <end>-1</end>
            </time>
            <day>
            <sun>true</sun>
            <mon>true</mon>
            <tue>true</tue>
            <wed>true</wed>
            <thu>true</thu>
            <fri>true</fri>
            <sat>true</sat>
            </day>
            <order>
            <column>TIME</column>
            <descending>true</descending>
            </order>
            </filter>
            </query>
            </inquire>
            </ppbe>'''
  log_xml_data = session.post('http://127.0.0.1:3052/agent/ppbe.xml',
                              data=payload, headers=headers)

  if log_xml_data.status_code == requests.codes.ok:
    return log_xml_data.content
  else:
    return False

def parse_log(log_xml):
  root = ET.fromstring(log_xml)
  records = root[0][0]

  log = []

  for record in records.findall('record'):
    # Dec 23, 2014 3:43:13  PM
    date = datetime.strptime(record.find('time').text, '%b %d, %Y %I:%M:%S  %p')
    capacity = record.find('capacity').text
    input_voltage = record.find('inputVolt').text
    output_voltage = record.find('outputVolt').text
    load = record.find('load').text
    runtime = record.find('runtime').text
    log.append((date, {"capacity" : capacity, "input_voltage" : input_voltage,
                       "output_voltage" : output_voltage, "load" : load,
                       "runtime" : runtime}))
  print("Parsed " + str(len(log)) + " records")
  return log

def pickle_log(log):
  pickle.dump(log, open('log.p', 'wb'))
  print("Saved pickled log")

if __name__ == "__main__":

  # the number of log entries to query when updating if log exists
  # this is later set to 10000 (theoretical maximum) if log does not exist
  num_requests = '10'

  # let's start the session so we can stay logged in
  session = requests.Session()
  login = login(session)
  if login:
    print("Logged in")
  else:
    print("Login failed")
    sys.exit(1)
  # we're now logged in

  if not os.path.isfile('log.p'):
  # if this is our first run, then we need to get all existing records
    # since there's no existing log, we'll set max requests
    num_requests = '10000'
    print("Querying full log")
    log_xml = retrieve_xml(session, num_requests)
    if log_xml:
      print("Retrieved full log")
    else:
      print("Query failed")
      sys.exit(1)
  else:
    # if not, then we'll just query for the past 'num_requests' entries
    print("Querying the last " + num_requests + " records")
    log_xml = retrieve_xml(session, num_requests)
    if log_xml:
      print("Retrieved last " + num_requests + " records")
    else:
      print("Query failed")
      sys.exit(1)


  # now we'll parse the xml and build a list with the data
  log = parse_log(log_xml)
  # we'll pickle the log so it's easier to read next time
  pickle_log(log)
