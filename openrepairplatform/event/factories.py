import datetime
import random

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Factory

from openrepairplatform.event.models import Activity, Event, Condition, Participation
from openrepairplatform.location.factories import PlaceFactory
from openrepairplatform.user.factories import OrganizationFactory, CustomUserFactory

faker = Factory.create()


class ConditionFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Name {faker.word()} #{n}")
    description = factory.Sequence(lambda n: f"descr: {faker.text()[:50]} #{n}")
    organization = factory.SubFactory(OrganizationFactory)
    price = random.randrange(100, 1000) / 100

    class Meta:
        model = Condition


class ActivityFactory(DjangoModelFactory):
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Sequence(lambda n: f"Name {faker.word()} #{n}")
    description = factory.Sequence(lambda n: f"descr: {faker.text()} #{n}")

    class Meta:
        model = Activity


class EventFactory(DjangoModelFactory):
    organization = factory.SubFactory(OrganizationFactory)
    location = factory.SubFactory(PlaceFactory)
    activity = factory.SubFactory(ActivityFactory)
    available_seats = random.randrange(100, 1000)
    date = faker.date_this_year(before_today=False, after_today=True)
    starts_at = faker.time(pattern="%H:%M", end_datetime=None)
    ends_at = faker.time(pattern="%H:%M", end_datetime=None)
    published = False
    publish_at = faker.date_time_between_dates(datetime_start=None, datetime_end=None)

    class Meta:
        model = Event


def _in_hours(nb_hours):
    return timezone.now() + datetime.timedelta(hours=nb_hours)


class PublishedEventFactory(EventFactory):
    date = faker.date_this_year(before_today=False, after_today=True)
    published = True
    publish_at = faker.date_time_between_dates(
        datetime_start=_in_hours(-5), datetime_end=_in_hours(-2)
    )
    ends_at = datetime.time(hour=23, minute=59)


class ParticipationFactory(DjangoModelFactory):
    user = factory.SubFactory(CustomUserFactory)
    event = factory.SubFactory(EventFactory)

    class Meta:
        model = Participation
