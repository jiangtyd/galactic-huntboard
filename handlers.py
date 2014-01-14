#!/usr/bin/env python
#
# Copyright 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import httplib2
import json
import logging
import pages
import pprint
import urllib
import urllib2
from apiclient.discovery import build
from basehandlers import AuthHandler, BaseHandler, HUNT_2014_FOLDER_ID, HUNTBOARD_NAME
from google.appengine.api import urlfetch

'''
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])
'''
# DRIVE = discovery.build('drive', 'v2', http=httplib2.Http())



HUNT_2014_FOLDER = 'https://docs.google.com/spreadsheet/ccc?key=0Ao0dlaERwPXMdE9HdUdBT0Q1SUl3T0x2YndOM1F6aXc#gid=0'

class RootHandler(BaseHandler):
    def get(self):
        '''Handles default landing page'''
        if not self.logged_in:
            self.login_needed()
            return;

        context = {
            'index': 0,
            'doc': HUNT_2014_FOLDER
        }
        self.render('puzzle.html', context)

class ChatHandler(BaseHandler):
    def get(self, number):
        '''Handles chat portion of the puzzle page.'''
        if not self.logged_in:
            self.login_needed()
            return;

        context = {
            'index': number
        },
        self.render('chat.html', context)

class MainChatHandler(BaseHandler):
    def get(self):
        '''Handles chat portion of the puzzle page.'''
        if not self.logged_in:
            self.login_needed()
            return;

        context = {
            'index': 0
        },
        self.render('chat.html')

class PuzzleHandler(BaseHandler):
    def get(self, number):
        '''Handles puzzle page. Creates a spreadsheet for the page if none exists.'''
        if not self.logged_in:
            self.login_needed()
            return;

        page = pages.getPageForIndex(number)
        if page != None:
            sheet_link = page.spreadsheet_link
        else:
            sheet_id, sheet_link = self.createEmptySpreadsheet(number)
            # Spreadsheet creation failed
            if sheet_id == '':
                raise Exception('Spreadsheet creation failed.')
            result = pages.putPageForIndex(number, sheet_id, sheet_link)
            # If while we were doing this, a page was already added for this index
            # in the database, delete the page we just created and use the link to
            # the existing page.
            if result != True:
                self.trashFile(sheet_id)
                sheet_link = result
        context = {
            'index': number,
            'doc': sheet_link
        }
        self.render('puzzle.html', context)


    def createEmptySpreadsheet(self, number):
        credentials = pages.getCred(HUNTBOARD_NAME, self.current_user.id)
        http = credentials.authorize(httplib2.Http())
        drive_service = build('drive', 'v2', http=http)
        body = {
            'title': '2014.'+number,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [{'id': HUNT_2014_FOLDER_ID}]
        }
        logging.info("#$%^&*()(*&^&*(&^%$^&*(^%$^&*(&^%$^&*&^%&")
        logging.info(body);
        file = drive_service.files().insert(body=body).execute()
        return (file['id'], file['alternateLink'])

    # Only trash, don't delete files in case something goes wrong
    def trashFile(self, file_id):
        url = 'https://www.googleapis.com/drive/v2/files/'+file_id+'/trash'
        result = urlfetch.fetch(url=url,
            method=urlfetch.POST,
            headers={
                'Authorization': 'Bearer '+auth_info['access_token'],
            }
        )