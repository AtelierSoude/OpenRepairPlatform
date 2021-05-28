import datetime

import pytest
from django.core.management import call_command
from django.utils import timezone

from openrepairplatform.user.models import CustomUser
from openrepairplatform.event.models import Event

pytestmark = pytest.mark.django_db


def test_command_clean_inactive_users(
    published_event_factory, user_log, custom_user_factory
):

    event_two_weeks_ago = published_event_factory(
        date=(timezone.now() - datetime.timedelta(days=15)).date()
    )
    event_one_week_ago = published_event_factory(
        date=(timezone.now() - datetime.timedelta(days=7)).date()
    )

    user_1 = custom_user_factory(first_name="", last_name="", email="toto@toto.fr")
    user_2 = custom_user_factory(first_name="", last_name="", email="test@test.fr")
    user_3 = custom_user_factory(first_name="", last_name="", email="pouet@pouet.fr")

    assert CustomUser.objects.count() == 4
    assert Event.objects.count() == 2

    event_two_weeks_ago.registered.add(user_1, user_2)
    event_two_weeks_ago.presents.add(user_3)

    event_one_week_ago.registered.add(user_2)

    call_command("clean_inactive_users")

    assert CustomUser.objects.count() == 3
