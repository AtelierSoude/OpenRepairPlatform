import factory
from factory.django import DjangoModelFactory

from openrepairplatform.location.models import Place
from openrepairplatform.user.factories import OrganizationFactory

class PlaceFactory(DjangoModelFactory):
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker("word")
    description = factory.Faker("text")
    category = factory.Faker("word")
    address = factory.Faker("address")

    class Meta:
        model = Place
