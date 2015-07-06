#!/usr/bin/env python
# encoding: utf-8

import json
import gspread
import os
import ConfigParser
from oauth2client.client import SignedJwtAssertionCredentials

class gs_operate():
    def login(self):
        try:
            json_key = json.load(open('OAuth2.json'))
            scope = ['https://spreadsheets.google.com/feeds']
            credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

            self.gc = gspread.authorize(credentials)
        except IOError:
            print "auth failed!"

    def open_by_url(self):
        url  = "https://docs.google.com/spreadsheets/d/1UdZ6YCRRin5Y91rOU0d1s6R4qCLz5C4R1D8EVk23FOw/edit#gid=10397401"
        spreadsheet = self.gc.open_by_url(url)
        worksheet = spreadsheet.worksheet("sheet2")
        
        groupId = []
        row = 1
        while True:
            val = worksheet.acell('B' + str(row)).value
            url = worksheet.acell('A' + str(row)).value
            if val:
                groupId.append(val)
            if not url:
                break
            row += 1
        return groupId
'''
def main(): 
    gs = gs_operate()
    gs.login()
    groupId = gs.open_by_url()

if __name__ == '__main__':
    main()
'''
