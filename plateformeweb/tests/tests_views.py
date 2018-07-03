from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from plateformeweb.models import *

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

    def test_organization_create(self):
        response = self.client.get(reverse("organization_create"))
        self.assertTemplateUsed(response, 'plateformeweb/organization_form.html')
        renderedView = response.render()
        self.assertEqual(renderedView.status_code, 200)

    def test_organization_detail(self):
        response = self.client.get(reverse("organization_detail", kwargs={'pk':self.org.pk,'slug':self.org.slug}))
        self.assertTemplateUsed(response, 'plateformeweb/organization.html')
        renderedView = response.render()
        self.assertEqual(renderedView.status_code, 200)

    def test_organization_edit(self):
        response = self.client.get(reverse("organization_edit", kwargs={'pk':self.org.pk}))
        self.assertTemplateUsed(response, 'plateformeweb/organization_form.html')
        renderedView = response.render()
        self.assertEqual(renderedView.status_code, 200)
