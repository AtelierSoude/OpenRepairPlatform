from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from plateformeweb.models import Organization

class TestOrganizationView(TestCase):
    "organization views tests"
    def setUp(self):
        self.user = CustomUser.objects.create_superuser('sankara', 'password')
        self.client.login(username='sankara', password='password')
        self.org = Organization.objects.create(name="Atelier Soudé", slug="ateliersoude", owner=self.user, active=True)

    def test_organization_list_view(self):
        response = self.client.get(reverse("organization_list"))
        self.assertTemplateUsed(response, 'plateformeweb/organization_list.html')
        renderedView = response.render()
        self.assertEqual(renderedView.status_code, 200)

