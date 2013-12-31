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
"""Starting template for Google App Engine applications.

Use this project as a starting point if you are just beginning to build a Google
App Engine project. Remember to download the OAuth 2.0 client secrets which can
be obtained from the Developer Console <https://code.google.com/apis/console/>
and save them as 'client_secrets.json' in the project directory.
"""

import httplib2
import json
import logging
import os
import pickle
import random

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client

from google.appengine.api import memcache
from google.appengine.ext import db

import webapp2
import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

service = discovery.build('drive', 'v2', http=httplib2.Http())
credentials = pickle.load(open('credentials','r'))

def auth_http():
    if credentials.access_token_expired or not credentials.access_token:
      credentials.refresh(httplib2.Http())
    return credentials.authorize(httplib2.Http())

class MainHandler(webapp2.RequestHandler):
  def get(self):
    response = service.files().list().execute(auth_http())
    items = response.get('items')
    files = [{'title':item.get('title'),
              'link':item.get('defaultOpenWithLink')} for item in items]
    
    variables = {
        'files':files
    }
    template = JINJA_ENVIRONMENT.get_template('files.html')
    self.response.write(template.render(variables))

class MakeFileHandler(webapp2.RequestHandler):
  def get(self):
    body = {
      'mimeType': 'application/vnd.google-apps.spreadsheet',
      'title': 'Puzzle %i' % random.randint(0, 10000),
    }
    response = service.files().insert(body=body).execute(auth_http())
    
    file_id = response.get('id')
    perm = {'withLink': True, 'role': "writer", 'type': "anyone", 'value':''}
    response = service.permissions().insert(fileId = file_id, body=perm).execute(auth_http())
  
    self.redirect('/')
    
class ClearAllHandler(webapp2.RequestHandler):
    def get(self):
       http = auth_http()
       response = service.files().list().execute(http)
       items = response.get('items')
       fids = [item.get('id') for item in items]
       
       for fid in fids:
         service.files().delete(fileId=fid).execute(http)
    
       self.redirect('/')
    


app = webapp2.WSGIApplication(
    [
     ('/', MainHandler),
     ('/makefile', MakeFileHandler),
     ('/clearall', ClearAllHandler),
    ],
    debug=True)
