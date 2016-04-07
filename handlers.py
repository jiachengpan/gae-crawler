import webapp2

import logging
import os
import time

import json

from utils import rent_parser
from models import proc_item
from datetime import timedelta

def fetch_raw_data(minutes_diff=5):
    ret = proc_item.ProcItem.get_latest_items(timedelta(minutes=minutes_diff))
    result = []
    for item in ret:
        data = item.to_dict()
        del data['item_hash']
        data['last_update'] = data['last_update'].isoformat()
        result.append(data)
    return result

def fetch_parsed_for_rent_data(minutes_diff=5):
    data = fetch_raw_data(minutes_diff)
    result = rent_parser.RentParser.parse(data)
    return result


class FetchRawHandler(webapp2.RequestHandler):
    def get(self):
        minutes = self.request.get_range('minutes', 1, None, 15)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(
                json.dumps(fetch_raw_data(minutes),
                    ensure_ascii=False))

class FetchParsedForRentHandler(webapp2.RequestHandler):
    def get(self):
        minutes = self.request.get_range('minutes', 1, None, 15)
        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(
                json.dumps(fetch_parsed_for_rent_data(minutes),
                    ensure_ascii=False))

class CleanupDataStoreHandler(webapp2.RequestHandler):
    def get(self):
        pass

