from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
from django.core import management
from django.conf import settings
# from plateformeweb.tasks import publish_events
import os
import django

# set the default Django settings module for the 'celery' program.
os.environ['DJANGO_SETTINGS_MODULE'] = 'ateliersoude.settings'

app = Celery('ateliersoude')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
	# every minute
	'every-minute': {
		'task': 'tasks.send_queued_mail',
		'schedule': crontab(),
                'args': ()
	},
	'every-minute2': {
		'task': 'tasks.publish_events',
		'schedule': crontab(),
                'args': ()
	}
}

# Load task modules from all registered Django app configs.
#app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)

@app.task()
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
