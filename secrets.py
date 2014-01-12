# Copy this file into secrets.py and set keys, secrets and scopes.

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here: 
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = "au<OxI!\x86\x87\xc6)\xb8\x8eq\xf6\x9bfhmW\xf2#\xf2-N\x00\x11\x98'e\x8a\xb3\xc0\xeb\xc7wEd\xcb\xcej\x96m$\x89\x1eO3e\x8d\xc5\x986\xb3\x0c\x14\xb7\xfb\x8c\xc9\x96\xff\xe0\x18"

# Google APIs
GOOGLE_APP_ID = '994323699569-rhgb05bmjknl5megejrhq0ej5rg2n9v8.apps.googleusercontent.com'
GOOGLE_APP_SECRET = '9HMsRtgNWF1ZM1I6WkVkmLuJ'
GOOGLE_SCOPES = ('https://www.googleapis.com/auth/userinfo.profile ' # Don't forget trailing space here
                'https://www.googleapis.com/auth/drive '
                'https://www.googleapis.com/auth/userinfo.email '
                )

# config that summarizes the above
AUTH_CONFIG = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET, GOOGLE_SCOPES),
}