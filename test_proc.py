import unittest

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import testbed

import datetime
import proc.douban

class TestModels(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.testbed.init_datastore_v3_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testBasic(self):
        URL = "https://www.douban.com/group/173252/"
        MAX = 3

        ret = proc.douban.ProcedureDouban.do_work({
            'url': URL,
            'max_count': MAX,
            })
        self.assertEqual(MAX, len(ret))

        # test repeat and cache
        ret = proc.douban.ProcedureDouban.do_work({
            'url': URL,
            'max_count': MAX,
            })
        self.assertEqual(0, len(ret))


if __name__ == '__main__':
    unittest.main()

