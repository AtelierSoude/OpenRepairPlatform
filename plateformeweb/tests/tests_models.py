import datetime
from django.test import TestCase
from users.models import CustomUser
from plateformeweb.models import *

class TestPlaceTypeModel(TestCase):
    "placetype must have name:string, slug:string"

    def test_place_type(self):
        slug = "atelier"
        latelier = PlaceType.objects.create(name=slug)
        self.assertEqual(latelier.slug, slug)

class TestOrganizationModel(TestCase):
    "organization must have name:string, owner:customUser, active:bool"

    def setUp(self):
        self.user = CustomUser.objects.create_superuser('sankara', 'password')

    def test_valid_type(self):
        self.org = Organization.objects.create(name="Atelier Soudé", slug="ateliersoude", owner=self.user, active=True)
        self.assertTrue(self.org)

class TestPlaceModel(TestCase):
    "place must have name, type, organization"
    def setUp(self):
        user = CustomUser.objects.create_superuser('sankara', 'password')
        self.placetype = PlaceType.objects.create(name="repaircafe", slug="repaircafe")
        self.org = Organization.objects.create(name="Atelier Soudé", slug="ateliersoude", owner=user, active=True)

    def test_valid_type(self):
        self.place = Place.objects.create(name="croixluizet", type=self.placetype, slug="croixluizet", organization=self.org, address="")
        self.assertTrue(self.place)


class TestOrganizationPersonModel(TestCase):
    "organizationperson must have user, organization"
    def setUp(self):
        self.user = CustomUser.objects.create_superuser('sankara', 'password')
        self.org = Organization.objects.create(name="Atelier Soudé", slug="ateliersoude", owner=self.user, active=True)
        self.org_person = OrganizationPerson.objects.create(user=self.user, organization=self.org)

    def test_valid_type(self):
        self.assertTrue(self.org_person)

    def test_visitor_role_by_default(self):
        self.assertEqual(self.org_person.role, 0)
