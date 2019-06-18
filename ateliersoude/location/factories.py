import factory
from factory.django import DjangoModelFactory

from faker import Factory

from ateliersoude.location.models import Place
from ateliersoude.user.factories import OrganizationFactory

faker = Factory.create()


class PlaceFactory(DjangoModelFactory):
    organization = factory.SubFactory(OrganizationFactory)
    name = faker.word()
    description = faker.text()
    category = faker.sentence()
    address = faker.address()
    longitude = faker.longitude()
    latitude = faker.latitude()

    class Meta:
        model = Place
