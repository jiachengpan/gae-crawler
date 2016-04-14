from google.appengine.ext import ndb
from google.appengine.api import memcache
import hashlib
import datetime
import logging

class ProcItem(ndb.Model):
    type_name   = ndb.StringProperty(required=True)
    last_update = ndb.DateTimeProperty(auto_now=True)
    title       = ndb.StringProperty(required=True)
    content     = ndb.JsonProperty()

    # TODO: implement a batch add
    @classmethod
    def add_item(cls, type_name, title, content):
        text = ''
        if 'text' in content:
            text = content['text']
        item_id = hashlib.sha256('%s_%s_%s' % (type_name, title.encode('utf-8'), text.encode('utf-8'))).hexdigest()
        cache_key = 'ProcItem_%s' % item_id

        if memcache.get(cache_key): return False

        key = ndb.Key(cls, item_id)
        if key.get():
            memcache.set(cache_key, True)
            return False

        ProcItem(
                key=key,
                type_name=type_name,
                title=title,
                content=content,
                ).put()
        memcache.set(cache_key, True)
        return True

    @classmethod
    def get_latest_items(cls, time=datetime.datetime.utcnow()):
        if isinstance(time, datetime.timedelta):
            time = datetime.datetime.utcnow()-time
        logging.debug(time)
        logging.debug([i.last_update for i in ProcItem.query().order(-ProcItem.last_update).fetch(2)])
        records = ProcItem.query(ProcItem.last_update > time).fetch()
        return records

