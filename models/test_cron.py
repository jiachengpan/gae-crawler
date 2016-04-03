import unittest

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import testbed

import cron as models
import datetime

class TestModels(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def testQueryJobsByInterval(self):
        models.CronJobs(
                interval='1hour',
                name='test0',
                parameters=None,
                last_update=datetime.datetime.now(),
                ).put()
        ret = models.CronJobs.get_jobs_by_interval('1hour')
        self.assertEqual(1, len(ret))

if __name__ == '__main__':
    unittest.main()

