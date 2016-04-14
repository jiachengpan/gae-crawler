# coding: utf-8

import unittest

from google.appengine.ext import testbed
from rent_parser import RentParser

class TestModels(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.testbed.init_urlfetch_stub()

    def tearDown(self):
        self.testbed.deactivate()

    @unittest.skip("skip temporarily")
    def testParser(self):
        ret = RentParser.parse_text(u'xx一室一厅一卫xxx')
        self.assertEqual(ret['room_type'], [u'一室一厅一卫'])
        ret = RentParser.parse_text(u'xx3房xxx')
        self.assertEqual(ret['room_type'], [u'三房'])

    #@unittest.skip("skip temporarily")
    def testPlaceSearch(self):
        RentParser.query_place('上海 世纪大道')
        RentParser.query_place('上海 世纪大道 临平路 大连西路')


if __name__ == '__main__':
    unittest.main()

