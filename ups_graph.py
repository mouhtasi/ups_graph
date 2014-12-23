import requests
import sys

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
    return log_xml_data
  else:
    return False

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
