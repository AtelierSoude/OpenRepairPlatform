import factory

from factory import LazyAttribute
from django.core.files.base import ContentFile

from factory.django import DjangoModelFactory, ImageField

from faker import Factory

from ateliersoude.user.models import Organization, CustomUser, Membership

faker = Factory.create()
USER_PASSWORD = "hackmeplease2048"


class OrganizationFactory(DjangoModelFactory):
    name = faker.word()
    picture = LazyAttribute(
        lambda _: ContentFile(
            ImageField()._make_data({"width": 1024, "height": 768}),
            "example.jpg",
        )
    )

    class Meta:
        model = Organization


class CustomUserFactory(DjangoModelFactory):
    first_name = faker.word()
    last_name = faker.word()

    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: "user{0}@example.com".format(n))

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        self.set_password(USER_PASSWORD)
        self.save()


class MembershipFactory(DjangoModelFactory):
    organization = factory.SubFactory(OrganizationFactory)
    user = factory.SubFactory(CustomUserFactory)

    class Meta:
        model = Membership
