
# -*- coding: utf-8 -*-
import sys
from basehandlers import oauth_decorator
from secrets import SESSION_KEY

from webapp2 import WSGIApplication, Route

# inject './lib' dir in the path so that we can simply do "import ndb" 
# or whatever there's in the app lib dir.
if 'lib' not in sys.path:
    sys.path[0:0] = ['lib']

# webapp2 config
app_config = {
  'webapp2_extras.sessions': {
    'cookie_name': '_simpleauth_sess',
    'secret_key': SESSION_KEY
  },
  'webapp2_extras.auth': {
    'user_attributes': []
  }
}
    
# Map URLs to handlers
routes = [
  Route('/', handler='handlers.RootHandler'),
  Route(oauth_decorator.callback_path, oauth_decorator.callback_handler()),
  Route('/logout', handler='handlers.BaseHandler:logout', name='logout'),
  # Reserving 800-999 for testing
  Route('/2014/<number:[1-9]\d{,1}|[1-7]\d{2}>', handler='handlers.PuzzleHandler'),
  Route('/2014/chat/<number:0|[1-9]\d{,1}|[1-7]\d{2}>', handler='handlers.ChatHandler', name='chat'),
]

app = WSGIApplication(routes, config=app_config, debug=True)