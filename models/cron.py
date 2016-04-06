from google.appengine.ext import ndb
from google.appengine.api import memcache

from enum import Enum

class Interval(Enum):
    ONE_HOUR = '1hour'
    FIVE_MIN = '5min'
#    ONE_MIN  = '1min'

class CronJobs(ndb.Model):
    interval    = ndb.StringProperty(
            choices=[member.value for name, member in Interval.__members__.items()])
    type_name   = ndb.StringProperty()
    name        = ndb.StringProperty()
    parameters  = ndb.JsonProperty()
    last_update = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_jobs_by_interval(cls, interval):
        ret = CronJobs.query(CronJobs.interval == interval).fetch(1000)
        ret = [(r.type_name, r.name, r.parameters) for r in ret]
        return ret

    @classmethod
    def get_jobs_by_type(cls, type_name):
        ret = CronJobs.query(CronJobs.type_name == type_name).fetch(1000)
        ret = [(r.type_name, r.name, r.parameters) for r in ret]
        return ret


    @classmethod
    def add_job(cls, interval, type_name, name, parameters):
        jobs = cls.get_jobs_by_type(type_name)

        job_search = set([j[1] for j in jobs])
        if name in job_search:
            return False

        CronJobs(
                interval=interval,
                type_name=type_name,
                name=name,
                parameters=parameters).put()
        return True

    @classmethod
    def delete_job(cls, type_name, name):
        ret = CronJobs.query(CronJobs.type_name == type_name, CronJobs.name == name).fetch(1000)
        for r in ret:
            r.key.delete()
        return True


