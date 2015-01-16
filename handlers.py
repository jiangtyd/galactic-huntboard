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

import json
import httplib2
import logging
import pages
import urllib
from apiclient.discovery import build
from basehandlers import BaseHandler, HUNT_2015_FOLDER_ID, HUNTBOARD_NAME, drive_service, oauth_decorator, oauth2_service
from google.appengine.api import urlfetch, users

'''
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])
'''

HUNT_2015_MAIN_SPREADSHEET = 'https://docs.google.com/spreadsheet/ccc?key=0AlzTSYJ9kTiqdGlsLXZQUDFJem5UT0kzNEUxdzVpQ3c#gid=0'

class RootHandler(BaseHandler):
    @oauth_decorator.oauth_required
    def get(self):
        '''Handles default landing page'''
        if not self.logged_in:
            self.login_needed()
            return

        context = {
            'index': 0,
            'doc': HUNT_2015_MAIN_SPREADSHEET
        }
        self.render('main_puzzle.html', context)

class ChatHandler(BaseHandler):
    @oauth_decorator.oauth_required
    def get(self, number):
        '''Handles chat portion of the puzzle page.'''
        if not self.logged_in:
            self.login_needed()
            return

        http = oauth_decorator.http()
        data = oauth2_service.userinfo().get().execute(http=http)
        nick = data['given_name'] + data['family_name']

        if number == '0':
            channels = 'galactic-trendsetters verytrendy!'
        else:
            channels = 'galactic-trendsetters-%s verytrendy!' % (number,)

        chat_args = [
            ('channels', channels),
            ('nick', nick),
        ]
        # qwebirc requires quote, not quote_plus
        # http://hg.qwebirc.org/qwebirc/issue/323
        chat_frame = '//webchat.freenode.net/?' + \
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
        #self.render('puzzle.html', context)
        self.redirect(sheet_link)


    @oauth_decorator.oauth_required
    def createEmptySpreadsheet(self, number):
        resp, content = httplib2.Http().request('http://galdoge.kaseorg.com/cgi-bin/suchbot-new-channel.cgi?' + urllib.urlencode({'id': number}))
        assert resp.status == 200

        http = oauth_decorator.http()
        body = {
            'title': '2015.'+number,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [{'id': HUNT_2015_FOLDER_ID}]
        }
        file = drive_service.files().insert(body=body).execute(http=http)
        return (file['id'], file['alternateLink'])

    # Only trash, don't delete files in case something goes wrong
    def trashFile(self, file_id):
        http = oauth_decorator.http()
        drive_service.files().trash(fileId=file_id).execute(http=http)
