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
    }


class ProcedureDouban(ProcedureBase):
    @classmethod
    def do_work_core(cls, args):
        cache_key = 'cached_threads_{}'.format(cls.__class__.__name__)
        cached_threads = memcache.get(cache_key)
        if not cached_threads:
            cached_threads = set()

        max_count = 100
        if 'max_count' in args:
            max_count = args['max_count']

        try:
            ret = urlfetch.fetch(
                    url=args['url'],
                    follow_redirects=False,
                    headers=HEADER,
                    deadline=60,
                    )
        except Exception as e:
            logging.error(e.message)
            return []

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
        threads = soup.find('table', attrs={'class': 'olt'}).find_all('td', attrs={'class': 'title'})

        result = []
        msg = {}
        for thread in threads[:max_count]:
            a = thread.find('a')
            data = (a.get('title'), a.get('href'))
            if data in cached_threads:
                continue

            ret = cls.fetch_thread(data[0], data[1])
            cached_threads.add((a.get('title'), a.get('href')))
            if ret:
                result.append(ret)

        memcache.set(key=cache_key, value=cached_threads)
        return result

    @classmethod
    def fetch_thread(cls, title, url):
        logging.debug('loading %s @ %s' % (title, url))
        try:
            ret = urlfetch.fetch(
                    url=url,
                    follow_redirects=False,
                    headers=HEADER,
                    deadline=60,
                    )
        except Exception as e:
            logging.error(e.message)
            return None

        if ret.status_code not in (200, 302):
            logging.error('URL Fetch failed. status {0}; url {1}.'.format(ret.status_code, url))
            return None

        _title = title
        _content = ''
        _pics = []

        try:
            content = gzip.GzipFile(fileobj=StringIO.StringIO(ret.content)).read()
        except IOError:
            content = ret.content
            if not content:
                logging.error('empty file')
                return None
        soup = BeautifulSoup(content, 'lxml')

        infobox = soup.find('table', attrs={'class': 'infobox'})
        if infobox:
            for strong in infobox.find_all('strong'):
                strong.extract()
            _title = infobox.text.strip()

        topic_content = soup.select('#link-report > div.topic-content')
        if topic_content:
            _content = topic_content[0].get_text().strip()
            for img in topic_content[0].find_all('img'):
                _pics.append(img.get('src'))

        return (_title, {
            'text': _content,
            'pics': _pics,
            },)

