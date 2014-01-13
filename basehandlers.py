import datetime
import httplib2
import json
import logging
import pages
import secrets
import urllib
import urllib2
import webapp2
from google.appengine.api import urlfetch
from jinja2.runtime import TemplateNotFound
from oauth2client.client import AccessTokenCredentials
from simpleauth import SimpleAuthHandler
from webapp2_extras import auth, sessions, jinja2



HUNT_2014_FOLDER_ID = "0B1zTSYJ9kTiqbkIzR3BWTnlhc3M"
HUNTBOARD_NAME = "Huntboard"

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
      
    @webapp2.cached_property
    def logged_in(self):
        """Returns true if a user is currently logged in, false otherwise"""
        return self.auth.get_user_by_session() is not None

    def login_needed(self):
        context = {}
        context['authfailed'] = self.request.get('authfailed')
        context['attempt'] = self.request.get('attempt')
        self.render('main.html', context)

    def render(self, template_name, template_vars={}):
        # Preset values for the template
        values = {
          'url_for': self.uri_for,
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


class AuthHandler(BaseHandler, SimpleAuthHandler):
#Authentication handler for all kinds of auth.

    # Enable optional OAuth 2.0 CSRF guard
    OAUTH2_CSRF_STATE = True
    USER_ATTRS = {
        'google': {
          'name'        : 'name',
          'id'          : 'id',
          'given_name'  : 'given_name',
          'email'       : 'email',
        }
    }

    def _on_signin(self, data, auth_info, provider):
        """Callback whenever a new or existing user is logging in.
        data is a user info dictionary.
        auth_info contains access token or oauth token and secret.

        See what's in it with logging.info(data, auth_info)
        """

        if self.logged_in:
            logging.info('Logging out currently logged in user')
            self.auth.unset_session()
       
        logging.info('Checking for access rights')
        inGroup = self.checkForAccessRights(data,auth_info)
        if not inGroup:
            logging.info("Unauthorized user "+data['email']+", id"+data['id']+" attempted access")
            self.redirectFailedLogin(data)
            return

        auth_id = '%s:%s' % (provider, data['id'])
        logging.info('Looking for a user with id %s', auth_id)
        user = self.auth.store.user_model.get_by_auth_id(auth_id)
        _attrs = self._to_user_model_attrs(data, self.USER_ATTRS[provider])

        if user:
            logging.info('Found existing user to log in')
            # Existing users might've changed their profile data so we update our
            # local model anyway. This might result in quite inefficient usage
            # of the Datastore, but we do this anyway for demo purposes.
            #
            # In a real app you could compare _attrs with user's properties fetched
            # from the datastore and update local user in case something's changed.
            user.populate(**_attrs)
            user.put()
            self.auth.set_session(self.auth.store.user_to_dict(user))
            self.setCredentials(data, auth_info)
        else:
            # Create a new user if nobody's signed in, and the user is on the
            # galactic-dogesetters google group,

            logging.info('Creating a brand new user')
            ok, user = self.auth.store.user_model.create_user(auth_id, **_attrs)
            if ok:
                self.auth.set_session(self.auth.store.user_to_dict(user))
                self.setCredentials(data, auth_info)
            else:
                self.redirectFailedLogin(data)
                return

        # Go to the main page
        self.redirect('/')

    def setCredentials(self, data, auth_info) :
        credentials = AccessTokenCredentials(auth_info['access_token'], None)
        pages.setCred(HUNTBOARD_NAME, data['id'], credentials)
       
    def checkForAccessRights(self, data, auth_info):
        # Allow login to the website iff user has access to Hunt 2014 folder
        
        try:
            # Get permission ID for this user
            url = "https://www.googleapis.com/drive/v2/permissionIds/"+data['email']
            req = urllib2.Request(url)
            req.add_header('Authorization', 'Bearer '+auth_info['access_token'])
            resp = urllib2.urlopen(req)
            contents = json.loads(resp.read())
            pId = contents["id"]

            # Check for permission on the file
            url = "https://www.googleapis.com/drive/v2/files/"+HUNT_2014_FOLDER_ID+"/permissions/"+pId
            req = urllib2.Request(url)
            req.add_header('Authorization', 'Bearer '+auth_info['access_token'])
            resp = urllib2.urlopen(req)

        except urllib2.URLError, e:
            contents = json.loads(e.read())
            logging.error(e)
            logging.info(contents)
            return False
        return True

    def redirectFailedLogin(self, data):
        self.redirect('/?authfailed=true&attempt='+data['email'])

    def logout(self):
       self.auth.unset_session()
       self.redirect('/')

    '''
    # Commenting this out; not like our error page looks any better than app engine's.
    def handle_exception(self, exception, debug):
        logging.error(exception)
        self.render('error.html', {'exception': exception})
    '''

    def _callback_uri_for(self, provider):
       return self.uri_for('auth_callback', provider=provider, _full=True)

    def _get_consumer_info_for(self, provider):
        """Returns a (key, secret, desired_scopes) tuple.

        For OAuth 2.0 it should be a 3 elements tuple:
        (client_ID, client_secret, scopes)
        """
        return secrets.AUTH_CONFIG[provider]
    
    def _to_user_model_attrs(self, data, attrs_map):
        """Get the needed information from the provider dataset."""
        user_attrs = {}
        for k, v in attrs_map.iteritems():
            attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
            user_attrs.setdefault(*attr)

        return user_attrs