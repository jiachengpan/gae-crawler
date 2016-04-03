from bs4 import BeautifulSoup
from google.appengine.api import urlfetch
from google.appengine.api import memcache

from .proc_base import ProcedureBase
import logging
import gzip
import StringIO

HEADER = {
	"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
	"Accept-Encoding": 'gzip',
	"Accept-Language": 'zh,en-GB;q=0.8,en;q=0.6,en-US;q=0.4,zh-CN;q=0.2,zh-TW;q=0.2',
        #"Cookie": '__jsluid=69a744636a7d40e0aaf3730b176362ef; __jsl_clearance=1459684554.195|0|8CbvqQarDel3APMwTv923Kyhjoc%3D; smzdm_user_view=D5213364B546447774E885FEBBC186CC; smzdm_user_source=141572A247975F7D044FC79D7F822D52; PHPSESSID=794mdvr6kf6m0geundkht8nlu4; amvid=357b4c03b22e0a122677805bf58b6cfb',
    }


class ProcedureXianyu(ProcedureBase):
    @classmethod
    def do_work_core(cls, args):
        key = 'items_{}'.format(cls.__module__ + '.' + cls.__name__)
        cached_items = memcache.get(key)
        if not cached_items:
            cached_items = set()

        max_count = 100
        if 'max_count' in args:
            max_count = args['max_count']

        ret = urlfetch.fetch(
                url=args['url'],
                follow_redirects=True,
                headers=HEADER,
                deadline=60,
                )
        if ret.status_code not in (200, 302):
            logging.error('URL Fetch failed. status {0}; url {1}.'.format(ret.status_code, args['url']))
            return []

        try:
            content = gzip.GzipFile(fileobj=StringIO.StringIO(ret.content)).read()
        except IOError:
            content = ret.content
            if not content:
                logging.error('empty file')
                return None
        soup = BeautifulSoup(content, 'lxml')
        items = soup.find_all('li', attrs={'class': 'item-info-wrapper'})

        result = []
        msg = {}
        for item in items[:max_count]:
            title = item.find('h4', attrs={'class': 'item-title'}).get_text()
            detail = item.find('div', attrs={'class', 'item-description'}).get_text().strip()
            price = float(item.find('div', attrs={'class', 'item-price'}).find('em').get_text().strip())
            url = item.find('h4', attrs={'class': 'item-title'}).find('a').get('href')

            _k = title + url
            if _k in cached_items: continue

            result.append((title, {'text': detail, 'price': price, 'url': url}))
            cached_items.add(_k)

        memcache.set(key=key, value=cached_items)
        return result


    @classmethod
    def render_msg(cls, args, new_items):
        min_price = float(args['min_price']) if 'min_price' in args else 0.0
        max_price = float(args['max_price']) if 'max_price' in args else 9999999.99

        messages = []
        for title, content in new_items:
            if content['price'] >= max_price or content['price'] < min_price: continue

            msg = '%s\n%s\n%s' % (title, str(content['price']), content['url'])
            messages.append(msg)

        if not len(messages):
            return None
        return cls.xmpp_template.render({'messages': messages, 'name': args['__name__']})





