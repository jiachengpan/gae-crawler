# coding: utf-8
import logging
import os
import re
import tempfile
import sys
import urllib
import api_config
import json

from google.appengine.api import urlfetch

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

zh_num = u'一两三四五六七八九二'
num2zh_num = { str(i+1): zh_num[i] for i in range(9) }

class RentParser(object):
    initialized = False

    regexp_room_type = re.compile(
            u'(([0-9%s][居房室厅卫]+)+)' % zh_num,
            re.UNICODE)
    regexp_fee = re.compile(
            u'(\d{3,4})([元]?[/每]?月|元)|(价格|租金|价)\D?(\d{3,4})\D',
            re.UNICODE)
    regexp_tele= re.compile(
            u'(1\d{2}-?\d{3}-?\d{5}|1\d{2}-?\d{4}-?\d{4})',
            re.UNICODE)

    jieba = None

    @classmethod
    def initialize(cls):
        logging.info('initialising jieba')
        import jieba
        # we cannot use tempfile in appengine, so cache files are generated in advance locally
        jieba.dt.tmp_dir = os.path.join(root_dir, 'resources/cache/')
        jieba.default_logger.removeHandler(jieba.log_console)
        jieba.dt.cache_file = os.path.join(root_dir, 'resources/cache/jieba.cache')
        jieba.load_userdict(os.path.join(root_dir, 'resources/dict/shanghai.dict'))

        import jieba.posseg

        cls.initialized = True
        cls.jieba   = jieba

    @classmethod
    def query_place(cls, text):
        URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'

        form_fields = {
                'query': text.encode('utf-8'),
                'key': api_config.api_key,
                'language': 'zh_cn',
                }
        form_data = urllib.urlencode(form_fields)
        try:
            response = urlfetch.fetch(
                    url=URL + form_data,
                    deadline=60,
                    )
        except Exception as e:
            logging.error(str(e))
            return

        data = json.loads(response.content)
        if data['status'] != 'OK':
            logging.warning('Status isnt ok: %s' % data['status'])
            if 'error_message' in data:
                logging.warning('Error: %s' % data['error_message'])
            return

        result = []
        for item in data['results']:
            result.append(item['geometry']['location'])
        return result

    @classmethod
    def parse_text(cls, text):
        if not cls.initialized: cls.initialize()

        """simple text parser, refer to zhaoxinwo/zufang"""
        def parse_room_type(text):
            result = set()
            for match in cls.regexp_room_type.findall(text):
                match = ''.join([num2zh_num[c] if c in num2zh_num else c for c in match[0]])
                result.add(match.replace(u'二', u'两'))
            return list(result)

        def parse_price(text):
            result = set()
            for match in cls.regexp_fee.findall(text):
                result.add(int(match[0] if match[0] else int(match[-1])))
            return list(result)

        def parse_address(text):
            result = set()
            for seg in cls.jieba.posseg.cut(text):
                if seg.flag in ('shanghai',):
                    result.add(seg.word)
            return list(result)

        def parse_telephone(text):
            result = set()
            for match in cls.regexp_tele.findall(text):
                result.add(match.replace('-', ''))
            return list(result)

        room_type   = parse_room_type(text)
        price       = parse_price(text)
        address     = parse_address(text)
        telephone   = parse_telephone(text)

        if len(address):
            location = cls.query_place(u'上海' + ' '.join(address))
        else:
            location = []
        return {
                'room_type':    room_type,
                'price':        price,
                'address':      address,
                'telephone':    telephone,
                'location':     location,
                }

    @classmethod
    def parse(cls, data):
        if not cls.initialized: cls.initialize()

        result = []
        for datum in data:
            try:
                more_context = cls.parse_text('%s,%s' % (datum['title'], datum['content']['text']))
                datum['content'].update(more_context)
                result.append(datum)
            except Exception as e:
                logging.error(e)
                logging.error(e.message)
                raise
        return result

