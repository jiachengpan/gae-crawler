import webapp2

import logging
import os
import time

from crons import get_cron_descriptions, get_cron_jobs, add_cron_job, delete_cron_job
from templates import JINJA_ENVIRONMENT

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.redirect('/jobs/overview')

class JobsOverview(webapp2.RequestHandler):
    def get(self):
        logging.info('overview')
        template = JINJA_ENVIRONMENT.get_template('templates/jobs.html')
        context = {}
        context['descriptions'] = get_cron_descriptions()
        context['jobs'] = get_cron_jobs()
        context['laststatus'] = {}
        if self.request.get('success'):
            context['laststatus']['success'] = int(self.request.get('success'))

        self.response.headers['Cache-Control'] = 'no-cache'
        self.response.write(template.render(context))

class JobsAdd(webapp2.RequestHandler):
    def get(self):
        interval    = self.request.get('interval')
        type_name   = self.request.get('type_name')
        name        = self.request.get('name')

        param_keys = [k for k in self.request.arguments() if k.startswith('param_')]
        parameters = {k[6:]: self.request.get(k) for k in param_keys}

        self.response.headers['Content-Type'] = 'text/plain'
        ret = add_cron_job(interval, type_name, name, parameters)

        time.sleep(1)
        self.redirect('/jobs/overview?success=%d' % ret)

class JobsDelete(webapp2.RequestHandler):
    def get(self):
        type_name   = self.request.get('type_name')
        name        = self.request.get('name')

        ret = delete_cron_job(type_name, name)

        time.sleep(1)
        self.redirect('/jobs/overview?success=%d' % ret)

