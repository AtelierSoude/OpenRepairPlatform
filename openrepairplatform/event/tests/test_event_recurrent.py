import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from openrepairplatform.event.models import Event
from openrepairplatform.user.factories import USER_PASSWORD

pytestmark = pytest.mark.django_db


def _django_date(datetime):
    return str(datetime).split(".")[0]


@pytest.fixture
def event_recurrent_data(
    condition_factory, activity, custom_user_factory, place, organization
):
    cond1 = condition_factory(organization=organization)
    cond2 = condition_factory(organization=organization)
    user1 = custom_user_factory()
    user2 = custom_user_factory()
    user3 = custom_user_factory()
    user4 = custom_user_factory()
    organization.actives.add(user1, user2, user3, user4)
    fix_date = datetime.datetime(3019, 7, 4, 14, 19, 5, tzinfo=timezone.tzinfo())
    return {
        "activity": activity.pk,
        "available_seats": 12,
        "organizers": [user4.pk],
        "conditions": [cond1.pk, cond2.pk],
        "location": place.pk,
        "organization": organization,
        "recurrent_type": "MONTHLY",
        "date": fix_date.date().strftime("%Y-%m-%d"),
        "days": ["MO", "TH"],
        "weeks": ["1", "2"],
        "starts_at": (
            (fix_date + datetime.timedelta(hours=4)).time().strftime("%H:%M")
        ),
        "ends_at": ((fix_date + datetime.timedelta(hours=7)).time().strftime("%H:%M")),
        "end_date": (
            (fix_date + datetime.timedelta(days=90)).date().strftime("%Y-%m-%d")
        ),
        "period_before_publish": 2,
    }


def test_get_event_recurrent_create(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    response = client.get(reverse("event:recurrent_create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'un nouvel évènement" in html


def test_get_event_recurrent_create_403(client, user_log, organization):
    response = client.get(reverse("event:recurrent_create", args=[organization.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:recurrent_create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "pas actif" in html


def test_get_event_recurrent_create_403_not_in_orga(client_log, organization):
    response = client_log.get(reverse("event:recurrent_create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "pas actif" in html


def test_event_create(client, user_log, event_recurrent_data):
    organization = event_recurrent_data.pop("organization")
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    assert Event.objects.count() == 0
    response = client.post(
        reverse("event:recurrent_create", args=[organization.pk]),
        event_recurrent_data,
    )
    events = Event.objects.all()
    assert response.status_code == 302
    assert len(events) == 11
    assert response["Location"] == reverse("event:list")


def test_event_create_invalid(client, user_log, event_recurrent_data):
    organization = event_recurrent_data.pop("organization")
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    assert Event.objects.count() == 0
    data = event_recurrent_data
    del data["weeks"]
    response = client.post(
        reverse("event:recurrent_create", args=[organization.pk]), data
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert Event.objects.count() == 0
    assert "renseigner au moins une semaine de récurrence" in html
