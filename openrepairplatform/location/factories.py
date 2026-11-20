import factory
from django.contrib.gis.geos import Point
from factory.django import DjangoModelFactory
from faker import Faker

from openrepairplatform.location.models import Place
from openrepairplatform.user.factories import OrganizationFactory

fake = Faker()

class PlaceFactory(DjangoModelFactory):
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.LazyAttribute(lambda o: o._geo[2])  # city name
    description = factory.Faker("text")
    category = factory.Faker("word")
    address = factory.Faker("address")
    location = factory.LazyAttribute(lambda o: Point(float(o._geo[1]), float(o._geo[0])))

    _geo = factory.LazyFunction(lambda: fake.local_latlng(country_code="FR"))

    class Meta:
        model = Place
        exclude = ["_geo"]
