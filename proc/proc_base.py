import logging
from google.appengine.api import xmpp

from models.proc_item import ProcItem
from templates import JINJA_ENVIRONMENT

class ProcedureBase(object):
    xmpp_template = JINJA_ENVIRONMENT.get_template('templates/proc_base.xmpp.template')

    @classmethod
    def do_work_core(cls, args):
        """return ((title, content)...)"""
        raise NotImplemented

    @classmethod
    def render_msg(cls, args, new_items):
        return cls.xmpp_template.render({'message': [i[0] for i in new_items], 'name': args['__name__']})

    @classmethod
    def do_work(cls, args):
        logging.debug('%s working with %s' % (cls, args))
        result = []
        data = cls.do_work_core(args)
        for title, content in data:
            ret = ProcItem.add_item(cls.__module__ + '.' + cls.__name__, title, content)
            if ret:
                result.append((title, content))
            else:
                result.append((title, content))
                logging.debug('store item fail: %s' % title)

        if 'xmpp' in args and args['xmpp'].strip():
            msg = cls.render_msg(args, result)
            if msg: xmpp.send_message([args['xmpp']], msg)

        return result


