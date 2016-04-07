import webapp2
import sys
import handlers

app = webapp2.WSGIApplication([
    ('/_fetch/raw',             handlers.FetchRawHandler),
    ('/_fetch/parsed_for_rent', handlers.FetchParsedForRentHandler),
], debug=True)
