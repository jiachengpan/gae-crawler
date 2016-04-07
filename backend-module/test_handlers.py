import unittest

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import testbed

import datetime
from models import proc_item
import fetch_handlers

class TestModels(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.testbed.init_datastore_v3_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    #@unittest.skip("skip temporarily")
    def testFetchRaw(self):
        content = {'abc': 'def'}
        proc_item.ProcItem.add_item('typeA', 'titleA', content)
        proc_item.ProcItem.add_item('typeA', 'titleB', content)
        proc_item.ProcItem.add_item('typeA', 'titleC', content)

        ret = fetch_handlers.fetch_raw_data()
        self.assertEqual(3, len(ret))

if __name__ == '__main__':
    unittest.main()

