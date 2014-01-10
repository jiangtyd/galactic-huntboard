import webapp2

import logging
from webapp2_extras import sessions

# ('https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/apps.groups.settings')


# Extend the base handler for session configuration
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):

        logging.info("%s", str('basesesese'))
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

    def getEmail(self):
        email = ''
        if self.session.get('auth') != None:
            email = self.session.get('auth').id_token.email
        return email

# Extend the base handler to make your page login-access only.
class AuthHandler(BaseHandler):
    def dispatch(self):

        logging.info("%s", str('authththt'))
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        if self.session.get('auth') == None or self.session.get('auth') == '':
            self.redirectToAuth()
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        except AccessTokenRefreshError:
            self.redirectToAuth()
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    def redirectToAuth(self):
        self.redirect("/login")