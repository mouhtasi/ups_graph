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

if __name__ == "__main__":

  # let's start the session so we can stay logged in
  session = requests.Session()
  login = login(session)
  if login:
    print(login.content)
  else:
    sys.exit(1)
  # we're now logged in
