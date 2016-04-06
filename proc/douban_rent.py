# coding: utf-8
from .douban import ProcedureDouban

import logging
import os
import re
import jieba
import jieba.posseg as pseg

# TODO: move this to backend
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

jieba.load_userdict(os.path.join(root_dir, 'resources/dict/shanghai.dict'))

zh_num = u'一两三四五六七八九二'
num2zh_num = { str(i+1): zh_num[i] for i in range(9) }

class ProcedureDoubanRent(ProcedureDouban):
    regexp_room_type = re.compile(
            u'[0-9{}]室[0-9{}]厅|[0-9{}]居室?'.format(zh_num, zh_num, zh_num),
            re.UNICODE)
    regexp_fee = re.compile(
            u'(\d{3,4})[元]?[/每]?月|(价格|租金)\D?(\d{3,4})\D',
            re.UNICODE)

    @classmethod
    def parse_text(cls, text):
        """simple text parser, refer to zhaoxinwo/zufang"""
        def parse_room_type(text):
            result = set()
            for match in cls.regexp_room_type.findall(text):
                match = ''.join([num2zh_num[c] if c in num2zh_num else c for c in match])
                result.add(match)
            return list(result)

        def parse_price(text):
            result = set()
            for match in cls.regexp_fee.findall(text):
                result.add(int(match[0] if match[0] else int(match[2])))
            return list(result)

        def parse_address(text):
            result = set()
            for seg in pseg.cut(text):
                if seg.flag in ('shanghai',):
                    result.add(seg.word)
            return list(result)

        room_type   = parse_room_type(text)
        price       = parse_price(text)
        address     = parse_address(text)
        return {
                'room_type':    room_type,
                'price':        price,
                'address':      address,
                }

    @classmethod
    def do_work_core(cls, args):
        ret = super(ProcedureDoubanRent, cls).do_work_core(args)

        for title, context in ret:
            more_context = cls.parse_text(context['text'])
            context.update(more_context)

        return ret

