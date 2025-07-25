import pytest
from django.core import signing
from django.http import HttpRequest

from openrepairplatform import settings
from openrepairplatform.event.models import Event
from openrepairplatform.event.templatetags.app_filters import (
    tokenize,
    initial,
    filter_orga,
    query_transform,
    organization_fees,
)
from openrepairplatform.user.forms import MoreInfoCustomUserForm

pytestmark = pytest.mark.django_db


class MockId:
    def __init__(self, id):
        self.id = id


def test_token():
    signed = tokenize(MockId(1), MockId(2), "book")
    data = {"user_id": 1, "event_id": 2}
    signed_expected = signing.dumps(data, key=settings.SECRET_KEY, salt="book")
    assert signed == signed_expected
    assert signing.loads(signed, key=settings.SECRET_KEY, salt="book") == data


def test_initial(custom_user):
    form = MoreInfoCustomUserForm()
    assert form.initial.get("email") is None
    form = initial(form, custom_user)
    assert form.initial["email"] == custom_user.email


def test_filter_orga(organization, event_factory):
    _ = event_factory()
    event1 = event_factory(organization=organization)
    _ = event_factory()
    a = filter_orga(Event.objects, organization)
    assert a.pk == event1.pk


def test_query_transform():
    request = HttpRequest()
    request.GET["test"] = "coucou"
    request.GET["page"] = 10
    assert query_transform(request, page=11, add="3&") == "test=coucou&page=11&add=3%26"


def test_organization_fees(organization, custom_user, membership_factory, fee_factory):
    membership = membership_factory(user=custom_user, organization=organization)
    fee = fee_factory(membership=membership, organization=organization, amount=8)
    tags = organization_fees(organization, custom_user)
    assert fee in tags
