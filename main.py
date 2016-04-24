import webapp2
import sys

import views
import crons
import handlers

app = webapp2.WSGIApplication([
    ('/', views.MainPage),
    ('/jobs/overview',  views.JobsOverview),
    ('/jobs/add',       views.JobsAdd),
    ('/jobs/delete',    views.JobsDelete),
    ('/_cron/5min',     crons.Cron5Min),
    ('/_cron/1hour',    crons.Cron1Hour),
], debug=True)
