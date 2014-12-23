import requests
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

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

def first_run(session):
  """Get the past 10,000 log entries"""
  headers = {'content-type': 'application/xml'}
  payload = '''<?xml version="1.0" encoding="UTF-8" ?>
            <ppbe>
            <target>
            <command>logs.status.present</command>
            </target>
            <inquire>
            <query>
            <state current="0" lastRequest="false" next="true" sizePerRequest="10000" />
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
  return log

if __name__ == "__main__":

  # let's start the session so we can stay logged in
  session = requests.Session()
  login = login(session)
  if login:
    print("Logged in")
  else:
    sys.exit(1)
  # we're now logged in
  # if this is our first run, then we need to get all existing records
  log_xml = first_run(session)
  if log_xml:
    print("Retrieved full log")
  else:
    sys.exit(1)
  # now we'll parse the xml and build a list with the data
  log = parse_log(log_xml)
