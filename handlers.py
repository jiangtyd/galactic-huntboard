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
from basehandlers import BaseHandler, HUNT_2014_FOLDER_ID, HUNTBOARD_NAME, oauth_decorator
from google.appengine.api import urlfetch, users

'''
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])
'''
# DRIVE = discovery.build('drive', 'v2', http=httplib2.Http())



HUNT_2014_MAIN_SPREADSHEET = 'https://docs.google.com/spreadsheet/ccc?key=0Ao0dlaERwPXMdE9HdUdBT0Q1SUl3T0x2YndOM1F6aXc#gid=0'

class RootHandler(BaseHandler):
    @oauth_decorator.oauth_required
    def get(self):
        '''Handles default landing page'''
        if not self.logged_in:
            self.login_needed()
            return

        context = {
            'index': 0,
            'doc': HUNT_2014_MAIN_SPREADSHEET
        }
        self.render('main_puzzle.html', context)

class ChatHandler(BaseHandler):
    @oauth_decorator.oauth_required
    def get(self, number):
        '''Handles chat portion of the puzzle page.'''
        if not self.logged_in:
            self.login_needed()
            return

        nick = self.current_user.given_name + self.current_user.family_name

        chat_args = [
            ('channels', 'galdoge-callqueue,galdoge verytrendy!,verytrendy!'),
            ('nick', nick),
        ]
        # qwebirc requires quote, not quote_plus
        # http://hg.qwebirc.org/qwebirc/issue/323
        chat_frame = '//webchat.quakenet.org/?' + \
            '&'.join(urllib.quote(k) + '=' + urllib.quote(v)
                     for k, v in chat_args)

        context = {
            'chat_frame': chat_frame,
        }
        self.render('chat.html', context)

class PuzzleHandler(BaseHandler):
    @oauth_decorator.oauth_required
    def get(self, number):
        '''Handles puzzle page. Creates a spreadsheet for the page if none exists.'''
        if not self.logged_in:
            self.login_needed()
            return

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


    @oauth_decorator.oauth_required
    def createEmptySpreadsheet(self, number):
        http = oauth_decorator.http()
        drive_service = build('drive', 'v2', http=http)
        body = {
            'title': '2014.'+number,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [{'id': HUNT_2014_FOLDER_ID}]
        }
        file = drive_service.files().insert(body=body).execute()
        return (file['id'], file['alternateLink'])

    # Only trash, don't delete files in case something goes wrong
    def trashFile(self, file_id):
        http = oauth_decorator.http()
        url = 'https://www.googleapis.com/drive/v2/files/'+file_id+'/trash'
        http.request(url, method='POST')
