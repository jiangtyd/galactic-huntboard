# Authentication handler and extensible handler. All other handlers should go in handlers.py,
# extend BaseHandler and follow the if logged_in pattern.

import datetime
import json
import logging
import os
import pages
import secrets
import webapp2
from apiclient.discovery import build
from apiclient.errors import HttpError
from functools import wraps
from google.appengine.api import users
from jinja2.runtime import TemplateNotFound
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets
from oauth2client.client import TokenRevokeError
from webapp2_extras import jinja2



HUNT_2014_FOLDER_ID = "0B1zTSYJ9kTiqcGxvdHFYU2pGckk"
HUNTBOARD_NAME = "Huntboard"

GOOGLE_SCOPES = ' '.join([
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly.metadata',
    'https://www.googleapis.com/auth/userinfo.email',
])

oauth_decorator = OAuth2DecoratorFromClientSecrets(
    os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
    GOOGLE_SCOPES)

oauth2_service = build('oauth2', 'v2')
drive_service = build('drive', 'v2')

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property    
    def jinja2(self):
        """Returns a Jinja2 renderer cached in the app registry"""
        return jinja2.get_jinja2(app=self.app)

    def login_needed(self):
        context = {}
        context['authfailed'] = self.request.get('authfailed')
        context['attempt'] = self.request.get('attempt')
        self.render('main.html', context)

    def render(self, template_name, template_vars={}):
        # Preset values for the template
        values = {
          'uri_for': self.uri_for,
          'logged_in': self.logged_in,
          'user': users.get_current_user(),
        }
        
        # Add manually supplied template values
        values.update(template_vars)
        
        # read the template or 404.html
        try:
          self.response.write(self.jinja2.render_template(template_name, **values))
        except TemplateNotFound:
          self.abort(404)

    USER_ATTRS = {
        'google': {
          'name'        : 'name',
          'id'          : 'id',
          'given_name'  : 'given_name',
          'family_name' : 'family_name',
          'email'       : 'email',
        }
    }

    @webapp2.cached_property
    def logged_in(self):
        logging.info('Checking for access rights')
        user = users.get_current_user()
        inGroup = self.checkForAccessRights(user)
        if not inGroup:
            logging.info("Unauthorized user " + user.email() + ", id " + user.user_id() + " attempted access")
            return False

        return True

    def checkForAccessRights(self, user):
        # Allow login to the website iff user has access to Hunt 2014 folder
        
        try:
            http = oauth_decorator.http()
            pId = drive_service.permissions().getIdForEmail(email=user.email()).execute(http=http)['id']
            drive_service.permissions().get(fileId=HUNT_2014_FOLDER_ID, permissionId=pId).execute(http=http)
        except HttpError, e:
            logging.error(e)
            return False
        return True

    @oauth_decorator.oauth_aware
    def logout(self):
        if oauth_decorator.has_credentials():
            try:
                oauth_decorator.credentials.revoke(oauth_decorator.http())
            except TokenRevokeError:
                pass
        self.redirect('/')

    def _to_user_model_attrs(self, data, attrs_map):
        """Get the needed information from the provider dataset."""
        user_attrs = {}
        for k, v in attrs_map.iteritems():
            attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
            user_attrs.setdefault(*attr)

        return user_attrs
