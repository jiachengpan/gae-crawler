import webapp2

import logging
import os
import time

import fetch_handlers
import json

class FetchRawHandler(webapp2.RequestHandler):
    def get(self):
        minutes = self.request.get_range('minutes', 1, None, 15)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(
                json.dumps(fetch_handlers.fetch_raw_data(minutes),
                    ensure_ascii=False))

class FetchParsedForRentHandler(webapp2.RequestHandler):
    def get(self):
        minutes = self.request.get_range('minutes', 1, None, 15)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(
                json.dumps(fetch_handlers.fetch_parsed_for_rent_data(minutes),
                    ensure_ascii=False))

class CleanupDataStoreHandler(webapp2.RequestHandler):
    def get(self):
        pass

