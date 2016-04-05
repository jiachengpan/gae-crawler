import webapp2
from google.appengine.api import memcache

import logging
import os
import inspect
import yaml
from models import cron
from proc import douban, smzdm, xianyu

proc_type2proc_class = {}
for m in (douban, smzdm, xianyu):
    for name, obj in inspect.getmembers(m, inspect.isclass):
        if not name.startswith('Proc'): continue
        proc_type2proc_class[obj.__module__ + '.' + name] = obj


def run_jobs(interval):
    jobs = cron.CronJobs.get_jobs_by_interval(interval)
    for job_type, job_name, job_param in jobs:
        logging.debug('running job {}'.format(job_name))
        job_param['__name__'] = job_name
        try:
            proc_type2proc_class[job_type].do_work(job_param)
        except Exception as e:
            logging.error('Job {} failed due to: {}'.format(job_name, e.message))

class Cron1Hour(webapp2.RequestHandler):
    def get(self):
        result = ''
        run_jobs(cron.Interval.ONE_HOUR.value)
        self.response.write(result)


class Cron5Min(webapp2.RequestHandler):
    def get(self):
        result = ''
        run_jobs(cron.Interval.FIVE_MIN.value)
        self.response.write(result)


class Cron1Min(webapp2.RequestHandler):
    def get(self):
        result = 0
        run_jobs(cron.Interval.ONE_MIN.value)
        self.response.write(result)


def get_cron_descriptions():
    with open(os.path.join(os.path.dirname(__file__), 'cron_description.yaml')) as fh:
        descs = yaml.load(fh.read())

    for desc in descs:
        desc['interval'] = [{'name': name, 'value': member.value}
                for name, member in cron.Interval.__members__.items()]
    return descs

def get_cron_jobs():
    jobs = []
    for interval, member in cron.Interval.__members__.items():
        ret = cron.CronJobs.get_jobs_by_interval(member.value)
        jobs.extend([{'type': i[0], 'name': i[1], 'param': i[2], 'interval': interval} for i in ret])
    return jobs

def add_cron_job(interval, type_name, name, parameters):
    if not interval or not type_name or not name:
        return False
    return cron.CronJobs.add_job(interval, type_name, name, parameters)

def delete_cron_job(type_name, name):
    return cron.CronJobs.delete_job(type_name, name)

