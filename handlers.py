import webapp2

import logging
import os
import time

import json

from utils import rent_parser
from models import proc_item
import datetime

ISOFORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

def fetch_raw_data(time):
    ret = proc_item.ProcItem.get_latest_items(time)
    result = []
    for item in ret:
        data = item.to_dict()
        data['last_update'] = data['last_update'].isoformat()
        result.append(data)
    return result

def fetch_parsed_for_rent_data(time):
    data = fetch_raw_data(time)
    result = rent_parser.RentParser.parse(data)
    return result

class FetchRawHandler(webapp2.RequestHandler):
    def get(self):
	try:
            time = datetime.datetime.strptime(self.request.get('time'), ISOFORMAT)
        except:
            time = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(
                json.dumps(fetch_raw_data(time),
                    ensure_ascii=False))

class FetchParsedForRentHandler(webapp2.RequestHandler):
    def get(self):
	try:
            time = datetime.datetime.strptime(self.request.get('time'), ISOFORMAT)
        except:
            time = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(
                json.dumps(fetch_parsed_for_rent_data(time),
                    ensure_ascii=False))

class CleanupDataStoreHandler(webapp2.RequestHandler):
    def get(self):
        pass

