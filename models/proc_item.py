from google.appengine.ext import ndb
from google.appengine.api import memcache
import hashlib
import datetime

class ProcItem(ndb.Model):
    type_name   = ndb.StringProperty(required=True)
    item_hash   = ndb.StringProperty(required=True)
    last_update = ndb.DateTimeProperty(auto_now=True)
    title       = ndb.StringProperty(required=True)
    content     = ndb.JsonProperty()

    # TODO: implement a batch add
    @classmethod
    def add_item(cls, type_name, title, content):
        text = ''
        if 'text' in content:
            text = content['text']
        digest = hashlib.sha256(type_name + title.encode('utf-8') + text.encode('utf-8')).hexdigest()

        key = 'proc_item_hash_{}'.format(type_name)
        cache_ret = memcache.get(key)

        if not cache_ret:
            digests = ProcItem.query(ProcItem.type_name == type_name, projection=[ProcItem.item_hash]).fetch(1000)
            digests = [r.item_hash for r in digests]
        else:
            digests = cache_ret

        if digest in digests:
            if not cache_ret: memcache.set(key=key, value=digests)
            return False

        digests.append(digest)
        ProcItem(
                type_name=type_name,
                item_hash=digest,
                title=title,
                content=content,
                ).put()
        memcache.set(key=key, value=digests)
        return True

    @classmethod
    def get_latest_items(cls, timediff=datetime.timedelta(minutes=5)):
        time = datetime.datetime.utcnow()-timediff
        records = ProcItem.query(ProcItem.last_update > time).fetch()
        return records

    @classmethod
    def get_old_items(cls, timediff=datetime.timedelta(days=30)):
        time = datetime.datetime.utcnow()-timediff
        records = ProcItem.query(ProcItem.last_update < time).fetch()
        return records

