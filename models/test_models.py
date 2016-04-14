import unittest

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import testbed

import cron
import proc_item
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
        cron.CronJobs(
                interval='1hour',
                name='test0',
                parameters=None,
                last_update=datetime.datetime.now(),
                ).put()
        ret = cron.CronJobs.get_jobs_by_interval('1hour')
        self.assertEqual(1, len(ret))

    def testProItem(self):
        ret1 = proc_item.ProcItem.add_item('typeA', 'titleA', '')
        ret2 = proc_item.ProcItem.add_item('typeA', 'titleA', '')
        self.assertTrue(ret1)
        self.assertFalse(ret2)


if __name__ == '__main__':
    unittest.main()

