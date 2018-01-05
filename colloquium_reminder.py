#!/usr/bin/env python
"""
Colloquium Reminder
Version: v0.1
Author: Tommaso Soru <tsoru@informatik.uni-leipzig.de>
"""
from __future__ import print_function
import httplib2
import os
import sys
import re
from datetime import datetime
import smtplib

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

reload(sys)
sys.setdefaultencoding("utf-8")

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def fetch_200_rows(service, spreadsheetId):
    rangeName = '2017!A2:G200'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    data = list()
    
    if not values:
        print('All data processed.')
        return None
    else:
        for row in values:
            print(data)
            data.append((row[0], row[1:3], row[5:7]))
    
    return data

def send_email(user, pwd, recipient, subject, body):

    # TODO just for tests
    if recipient == "" + "@" + "":

        gmail_user = user
        gmail_pwd = pwd
        FROM = user
        TO = recipient if type(recipient) is list else [recipient]
        SUBJECT = subject
        TEXT = body

        # Prepare actual message
        message = """From: %s\nContent-Type: text/plain; charset=UTF-8\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            server.close()
            print('Email successfully sent.')
            return True
        except:
            print("Failed to send email.")
            return False
    else:
        print("Here we should have sent an email...")

def cron_job(date, emailText, email_pwd, presenter):
    if len(presenter) == 2:
        if not EMAIL_REGEX.match(presenter[1]):
            print("'{}' is not a valid email address.".format(presenter[1]))
        # get time gap between dates
        colloquium_date = datetime.strptime(date, '%d-%b-%Y')
        gap = colloquium_date - datetime.today()
        days_gap = gap.days + float(gap.seconds) / 3600 / 24
        # send email if 8.0 < days left < 15.0
        if days_gap <= 15 and days_gap > 8:
            # TODO check records... if not:
            print("*** DAYS LEFT = {} ***".format(days_gap))
            print("Sending email to: {}\n".format(presenter[1]))
            print(emailText.format(unicode(presenter[0]), date))
            send_email("dice.colloquium" + "@" + "gmail.com", email_pwd, presenter[1], "Your presentation at the DICE Colloquium", emailText.format(unicode(presenter[0]), date))
            # TODO record notification I
        # send email if 0.0 < days left < 8.0
        elif days_gap <= 8 and days_gap > 0:
            # TODO check records... if not:
            print("*** DAYS LEFT = {} ***".format(days_gap))
            print("Sending email to: {}\n".format(presenter[1]))
            print(emailText.format(unicode(presenter[0]), date))
            send_email("dice.colloquium" + "@" + "gmail.com", email_pwd, presenter[1], "Your presentation at the DICE Colloquium", emailText.format(unicode(presenter[0]), date))
            # TODO record notification II
        else:
            print("Days left = {}".format(days_gap))
    
def main():
    print("Colloquium Reminder v0.1 started.")
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1u91LlybzdmrhyGm5leXlFV06sDbds5GJ0BDqyHLdWNM'
    
    emailText = ""
    with open("email.txt") as f:
        for line in f:
            emailText += line
    
    email_pwd = None
    with open('email_pwd.txt') as f:
        for line in f:
            email_pwd = line
    
    print("Fetching data...")
    data = fetch_200_rows(service, spreadsheetId)
    for d in data:
        date, presenter1, presenter2 = d[:]
        print(date, presenter1, presenter2)
        
        cron_job(date, emailText, email_pwd, presenter1)
        cron_job(date, emailText, email_pwd, presenter2)

if __name__ == '__main__':
    main()

