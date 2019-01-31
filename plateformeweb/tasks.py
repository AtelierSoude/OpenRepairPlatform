from __future__ import absolute_import, unicode_literals

from celery.schedules import crontab
from django.core import management

# from plateformeweb.tasks import publish_events
import os
import django
from celery import shared_task

@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param

@shared_task(name='tasks.send_queued_mail')
def send_queued_mail():
    management.call_command('send_queued_mail')

@shared_task(name='tasks.publish_events')
def publish_events():
    from plateformeweb.models import Event
    from django.utils import timezone
    today = timezone.now()
    unpublished_events = Event.objects.filter(publish_at__lte=today, starts_at__gte=today, published=False)
    unpublished_events.update(published=True)
