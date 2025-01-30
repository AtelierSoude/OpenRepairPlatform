import factory
from factory.django import DjangoModelFactory

from faker import Factory

from openrepairplatform.location.models import Place
from openrepairplatform.user.factories import OrganizationFactory

faker = Factory.create()


class PlaceFactory(DjangoModelFactory):
    organization = factory.SubFactory(OrganizationFactory)
    name = faker.word()
    description = faker.text()
    category = faker.sentence()
    address = faker.address()

    class Meta:
        model = Place
