from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
from django.core import management
import os
import django
import tasks

# set the default Django settings module for the 'celery' program.
os.environ['DJANGO_SETTINGS_MODULE'] = 'ateliersoude.settings'

app = Celery('ateliersoude')

app.conf.broker_url = 'redis://redis:6379/0'
app.conf.result_backend = 'redis://redis:6379/0'
app.conf.accept_content = ['application/json']
app.conf.result_serializer = 'json'
app.conf.task_serializer = 'json'
app.conf.timezone = 'Europe/Paris'
app.conf.beat_schedule = {
	# every minute
	'every-minute': {
		'task': 'tasks.send_queued_mail',
		'schedule': crontab(),
                'args': ()
	}
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task()
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task(name='tasks.send_queued_mail')
def send_queued_mail():
    management.call_command('send_queued_mail')
