import pytest

from pytest_factoryboy import register
from rest_framework.test import APIClient

from openrepairplatform.location.factories import PlaceFactory
from openrepairplatform.event.factories import (
    ActivityFactory,
    ConditionFactory,
    EventFactory,
    PublishedEventFactory,
    ParticipationFactory,
)

from openrepairplatform.user.factories import (
    USER_PASSWORD,
    CustomUserFactory,
    OrganizationFactory,
    MembershipFactory,
    FeeFactory,
)

register(CustomUserFactory)
register(PlaceFactory)
register(OrganizationFactory)
register(ActivityFactory)
register(ConditionFactory)
register(EventFactory)
register(PublishedEventFactory)
register(MembershipFactory)
register(ParticipationFactory)
register(FeeFactory)


@pytest.fixture
def user_log(custom_user_factory):
    user = custom_user_factory(email="user_log@example.com")
    return user


@pytest.fixture
def user_log_staff(custom_user_factory):
    return custom_user_factory(email="user_log@example.com", is_staff=True)


@pytest.fixture
def client_log(client, user_log):
    client.login(email=user_log.email, password=USER_PASSWORD)
    return client


@pytest.fixture
def client_log_staff(client, user_log_staff):
    client.login(email=user_log.email, password=USER_PASSWORD)
    return client


@pytest.fixture
def api_client_log(user_log):
    client = APIClient()
    client.login(email=user_log.email, password=USER_PASSWORD)
    return client
