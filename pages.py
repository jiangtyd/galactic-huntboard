import cPickle as pickle
import logging
from google.appengine.ext import db

PAGE = "page"

class Page(db.Model):
	spreadsheet_id = db.StringProperty(required=True)
	spreadsheet_link = db.StringProperty(required=True)
	tabs = db.ListProperty(db.Link)

# Should use oauth2client.files.Storage or keyring but getting OSError 40: Function not implemented
# Probably need to add some libraries.
class Cred(db.Model):
	credentials = db.TextProperty(required=True)

def setCred(app, user, credentials):
	key = app+":"+user
	logging.info(key)
	cred = Cred(key_name=key, credentials=pickle.dumps(credentials))
	cred.put()

def getCred(app, user):
	key = app+":"+user
	logging.info(key)
	logging.info(Cred.get_by_key_name(key))
	return pickle.loads(Cred.get_by_key_name(key).credentials.__str__())

# Returns None if no such index
def getPageForIndex(index):
	key = PAGE+index
	return Page.get_by_key_name(key)

def putPageForIndex(index, spreadsheet_id, spreadsheet_link):
	# Only put page if page does not already exist. This way, in case
	# of concurrent calls, oldest page is kept.
	# Return true if page.put() was called, spreadsheet_link of page otherwise (so that the
	# spare sheet generated can be discarded, and the existing id used)
	key = PAGE+index
	page = Page.get_by_key_name(key)
	if page != None:
		return page['spreadsheet_link']

	page = Page(key_name=key, spreadsheet_id=spreadsheet_id, spreadsheet_link=spreadsheet_link)
	page.put()
	return True