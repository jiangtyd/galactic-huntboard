# Authentication handler and extensible handler. All other handlers should go in handlers.py,
# extend BaseHandler and follow the if logged_in pattern.

import datetime
import httplib2
import json
import logging
import os
import pages
import secrets
import urllib
import webapp2
from functools import wraps
from google.appengine.api import users
from jinja2.runtime import TemplateNotFound
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets
from webapp2_extras import auth, sessions, jinja2



HUNT_2014_FOLDER_ID = "0B1zTSYJ9kTiqbkIzR3BWTnlhc3M"
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

# Extend the base handler for session configuration
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):

        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)


    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    @webapp2.cached_property    
    def jinja2(self):
        """Returns a Jinja2 renderer cached in the app registry"""
        return jinja2.get_jinja2(app=self.app)

    @webapp2.cached_property
    def session(self):
        """Returns a session using the default cookie key"""
        return self.session_store.get_session()

    @webapp2.cached_property
    def auth(self):
      return auth.get_auth()

    @webapp2.cached_property
    def current_user(self):
        """Returns currently logged in user"""
        user_dict = self.auth.get_user_by_session()
        if user_dict == None:
            return None
        return self.auth.store.user_model.get_by_id(user_dict['user_id'])

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
          'user': self.current_user,
          'flashes': self.session.get_flashes()
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

        auth_id = 'google:%s' % (user.user_id(),)
        logging.info('Looking for a user with id %s', auth_id)
        user = self.auth.store.user_model.get_by_auth_id(auth_id)

        if user:
            logging.info('Found existing user to log in')
            self.auth.set_session(self.auth.store.user_to_dict(user))
            return True
        else:
            # Create a new user if nobody's signed in, and the user is on the
            # galactic-dogesetters google group,

            http = oauth_decorator.http()
            resp, content = http.request('https://www.googleapis.com/oauth2/v3/userinfo')
            if resp.status != 200:
                return False
            data = json.loads(content)
            _attrs = self._to_user_model_attrs(data, self.USER_ATTRS['google'])

            logging.info('Creating a brand new user')
            ok, user = self.auth.store.user_model.create_user(auth_id, **_attrs)
            if ok:
                self.auth.set_session(self.auth.store.user_to_dict(user))
                return True
            else:
                return False

    def checkForAccessRights(self, user):
        # Allow login to the website iff user has access to Hunt 2014 folder
        
        try:
            # Get permission ID for this user
            url = "https://www.googleapis.com/drive/v2/permissionIds/"+user.email()
            http = oauth_decorator.http()
            resp, content = http.request(url)
            if resp.status != 200:
                logging.info(content)
                return False
            contents = json.loads(content)
            pId = contents["id"]

            # Check for permission on the file
            url = "https://www.googleapis.com/drive/v2/files/"+HUNT_2014_FOLDER_ID+"/permissions/"+pId
            resp, content = http.request(url)
            if resp.status != 200:
                logging.info(content)
                return False

        except httplib2.HttpLib2Error, e:
            logging.error(e)
            return False
        return True

    @oauth_decorator.oauth_aware
    def logout(self):
       if oauth_decorator.has_credentials():
           oauth_decorator.credentials.revoke(oauth_decorator.http())
       self.auth.unset_session()
       self.redirect('/')

    def _to_user_model_attrs(self, data, attrs_map):
        """Get the needed information from the provider dataset."""
        user_attrs = {}
        for k, v in attrs_map.iteritems():
            attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
            user_attrs.setdefault(*attr)

        return user_attrs
