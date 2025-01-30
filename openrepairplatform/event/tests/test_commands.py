import datetime

import pytest
from django.core import mail
from django.core.management import call_command
from django.utils import timezone

pytestmark = pytest.mark.django_db


def test_command_notify_next_day_events(published_event_factory, user_log):
    event1 = published_event_factory(
        date=(timezone.now() + datetime.timedelta(days=1)).date(),
        starts_at=(timezone.now() + datetime.timedelta(days=1)).time(),
        ends_at=(
            timezone.now() + datetime.timedelta(days=1) + datetime.timedelta(hours=4)
        ).time(),
    )
    event1.registered.add(user_log)
    call_command("notify_next_day_events", "https://example.com")
    assert len(mail.outbox) == 1


def test_command_publish_events(event_factory, custom_user_factory):
    event1 = event_factory(
        published=False,
        publish_at=timezone.now() - timezone.timedelta(hours=1),
    )
    event1.organization.admins.add(custom_user_factory())
    event1.organization.actives.add(custom_user_factory())


#   call_command("publish_events", "https://example.com")
#   #event1.refresh_from_db()
#   #assert len(mail.outbox) == 2
#   #assert event1.published
