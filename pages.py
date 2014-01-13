from google.appengine.ext import db

PAGE = "page"

class Page(db.Model):
	spreadsheet_id = db.StringProperty(required=True)
	spreadsheet_link = db.StringProperty(required=True)
	tabs = db.ListProperty(db.Link)

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

	page = Page(key_name = PAGE+index, spreadsheet_id = spreadsheet_id, spreadsheet_link = spreadsheet_link)
	page.put()
	return True