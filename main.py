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
import jinja2
import json
import logging
import os
import pickle
import random
import urllib2
import webapp2

from apiclient import discovery
from base import AuthHandler, BaseHandler
from google.appengine.api import memcache, urlfetch
from oauth2client.appengine import xsrf_secret_key
from oauth2client.client import OAuth2WebServerFlow
from webapp2_extras import sessions

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

DRIVE = discovery.build('drive', 'v2', http=httplib2.Http())

# Create a flow object. This object holds the client_id, client_secret, and
# scope. It assists with OAuth 2.0 steps to get user authorization and
# credentials. For this example, the client ID and secret are command-line
# arguments.
flow = OAuth2WebServerFlow('994323699569-rhgb05bmjknl5megejrhq0ej5rg2n9v8.apps.googleusercontent.com',
                         '9HMsRtgNWF1ZM1I6WkVkmLuJ',
                         [],
                         redirect_uri='http://galactichuntboard.appspot.com/oauth2callback')

# ('https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/apps.groups.settings')

def get_credentials():
    credentials = memcache.get('credentials')
    if not credentials:
        print 'loading from file'
        credentials = pickle.load(open('credentials', 'r'))
    if credentials.access_token_expired or not credentials.access_token:
        credentials.refresh(httplib2.Http())
        memcache.set('credentials', credentials)
    return credentials

def auth_http():
    return get_credentials().authorize(httplib2.Http())


def getFiles():
    items = DRIVE.files().list().execute(auth_http()).get('items')
    return [{'title': item.get('title'),
              'link': item.get('defaultOpenWithLink')} for item in items]

def makeFile(name):
    body = {
      'mimeType': 'application/vnd.google-apps.spreadsheet',
      'title': name,
      'parents': [    
            { # A reference to a file's parent.
              "isRoot": False, # Whether or not the parent is the root folder.
              "kind": "drive#parentReference", # This is always drive#parentReference.
              "id": "0B1zTSYJ9kTiqdlNwOGZvUmtRNnc", # The ID of the parent.
              "selfLink": "https://content.googleapis.com/drive/v2/files/1SBOd6WT7MAHUSGwsOF_nXOrkR_EONR11Ls5L8AC8O0c/parents", # A link back to this reference.
              "parentLink": "https://content.googleapis.com/drive/v2/files/0B1zTSYJ9kTiqdlNwOGZvUmtRNnc", # A link to the parent.
            }
        ]
    }

    file_id = DRIVE.files().insert(body=body).execute(auth_http()).get('id')


class MainHandler(AuthHandler):

    def get(self):
        variables = {
            'files': getFiles()
        }
        template = JINJA_ENVIRONMENT.get_template('files.html')
        self.response.write(template.render(variables))


class LoginHandler(BaseHandler):

    def get(self):

        logging.info("%s", str('loginll'))
        authurl = 'https://accounts.google.com/o/oauth2/auth?' + \
            'client_id=994323699569-rhgb05bmjknl5megejrhq0ej5rg2n9v8.apps.googleusercontent.com&' + \
            'response_type=code&' + \
            'scope=openid%20email&' + \
            'redirect_uri=http://galactichuntboard.appspot.com/oauth2callback&' + \
            'login_hint='+self.getEmail()+'&' + \
            'state='+ xsrf_secret_key()
        try:
            self.redirect(authurl)
        except:
            self.redirect('/loginfailed')


class LoginCallbackHandler(BaseHandler):
    def get(self):

        # Ensure that the request is not a forgery and that the user sending
        # this connect request is the expected user.

        try:
            if self.request.get_all('state') != appengine.xsrf_secret_key():
                self.redirect('/loginfailed')

            code = self.request.get_all('code')
            auth = RequestHandler.flow.step2_exchange(code)
            session['auth']=credentials
        except:
            self.redirect("/loginfailed")

        allowed = urllib2.urlopen('https://www.googleapis.com/groups/v1/groups/galactic-dogesetters@gmail.com?fields=email')
        allowed = json.loads(allowed)

        if not (self.session.get('auth').id_token.email in allowed):
            self.redirect("/loginfailed")


        template = JINJA_ENVIRONMENT.get_template('login-complete.html')
        self.response.write(template.render())


class LoginFailedHandler(BaseHandler):
    def get(self):
        logging.info("%s", str('loginfailed'))
        variables = {
            'username': getEmail()
        }
        template = JINJA_ENVIRONMENT.get_template('login-failed.html')
        self.response.write(template.render({ 'username': getEmail() }))


class LogoutHandler(BaseHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('_filelist.html')

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(
            { 'html': template.render({ 'files': getFiles() }) }
            )
        )

#        logging.info("%s", str('logout'))
#        self.session["auth"] = ''

#        template = JINJA_ENVIRONMENT.get_template('logout.html')
#        self.response.write(template.render())


class FileHandler(AuthHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('_filelist.html')

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(
            { 'html': template.render({ 'files': getFiles() }) }
            )
        )


class MakeFileHandler(AuthHandler):

    def post(self):
        makeFile(self.request.get('name'))

        template = JINJA_ENVIRONMENT.get_template('_filelist.html')

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(
            { 'html': template.render({ 'files': getFiles() }) }
            )
        )


class ClearAllHandler(AuthHandler):

    def get(self):
        http = auth_http()
        items = DRIVE.files().list().execute(http).get('items')
        fids = [item.get('id') for item in items]

        for fid in fids:
            DRIVE.files().delete(fileId=fid).execute(http)

        self.redirect('/')

routes = [
        (r'/', MainHandler),
        (r'/login', LoginHandler),
        (r'/loginfailed', LoginFailedHandler),
        (r'/oauth2callback', LoginCallbackHandler),
        (r'/leave', LogoutHandler),
        (r'/files', FileHandler),
        (r'/files/new', MakeFileHandler),
        (r'/clearall', ClearAllHandler),
        ]

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': '3t4yjumn2be8e2a6iwvqnkod54y4s89wb5fd',
}
app = webapp2.WSGIApplication(routes=routes, debug=True, config=config)
