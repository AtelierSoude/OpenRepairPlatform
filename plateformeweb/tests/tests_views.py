from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from plateformeweb.models import *

class TestAllViews(TestCase):
    def setUp(self):
        admin_page = '/admin/'
        self.admin = CustomUser.objects.create_superuser('sankara', 'password')
        self.client.login(username='sankara', password='password')
        # Random User
        self.user = CustomUser.objects.create_user('lumumba', 'password')

        self.organization = Organization.objects.create(
            name = 'Atelier Soudé',
            slug = 'ateliersoude',
            owner = self.admin,
            active = True)
        self.placetype = PlaceType.objects.create(
            name = 'repaircafe',
            slug = 'repaircafe')
        self.activity = Activity.objects.create(
            name = 'cafe',
            owner = self.admin,
            picture = 'static/img/event-card.jpg')
        self.place = Place.objects.create(
            name = 'croixluizet',
            # type = self.placetype,
            slug = 'croixluizet',
            organization = self.organization,
            address = '',
            picture = 'foo.jpg')
        self.event = Event.objects.create(
            title = 'repairtoday',
            organization = self.organization,
            owner = self.admin,
            type = self.activity,
            location = self.place)
        self.client.logout()

    def test_anonym_visitor(self):
        authorized_views = [
            reverse('organization_list'),
            reverse('place_list'),
            reverse('activity_list'),
            reverse('event_list')
        ]

        for page in authorized_views:
            resp = self.client.get(page)
            assert resp.status_code == 200

    def test_organization_person_user_views(self):
        self.org_person = OrganizationPerson.objects.create(user=self.user, organization=self.organization)
        self.client.login(username='lumumba', password='password')

        authorized_views = [
            reverse('organization_list'),
            reverse('organization_detail', kwargs={'pk': self.organization.pk, 'slug': self.organization.slug }),
            reverse('place_list'),
            reverse('place_detail', kwargs={'pk': self.place.pk, 'slug': self.place.slug }),
            reverse('activity_list'),
            reverse('activity_detail', kwargs={'pk': self.activity.pk, 'slug': self.activity.slug }),
            reverse('event_list'),
            reverse('event_detail', kwargs={'pk': self.event.pk, 'slug': self.event.slug }),
            reverse('booking_form', kwargs={'pk': self.event.pk })
        ]

        for page in authorized_views:
            resp = self.client.get(page)
            assert resp.status_code == 200


    def test_organization_person_with_volunteer_role_user_views(self):
        self.volunteer = CustomUser.objects.create_user('bourguiba', 'password')
        self.org_person = OrganizationPerson.objects.create(user=self.volunteer, organization=self.organization, role=20)
        self.client.login(username='bourguiba', password='password')

        authorized_views = [
            reverse('organization_list'),
            reverse('organization_detail', kwargs={'pk': self.organization.pk, 'slug': self.organization.slug }),
            reverse('place_list'),
            reverse('place_detail', kwargs={'pk': self.place.pk, 'slug': self.place.slug }),
            reverse('activity_list'),
            reverse('activity_detail', kwargs={'pk': self.activity.pk, 'slug': self.activity.slug }),
            reverse('event_list'),
            reverse('event_detail', kwargs={'pk': self.event.pk, 'slug': self.event.slug }),
            reverse('booking_form', kwargs={'pk': self.event.pk })
        ]

        for page in authorized_views:
            resp = self.client.get(page)
            assert resp.status_code == 200

    def test_admin(self):
        self.client.login(username='sankara', password='password')

        authorized_views = [
            reverse('organization_list'),
            reverse('organization_create'),
            reverse('organization_edit', kwargs={'pk': self.organization.pk }),
            reverse('organization_detail', kwargs={'pk': self.organization.pk, 'slug': self.organization.slug }),
            reverse('place_list'),
            reverse('place_create'),
            reverse('place_edit', kwargs={'pk': self.place.pk }),
            reverse('place_detail', kwargs={'pk': self.place.pk, 'slug': self.place.slug }),
            reverse('activity_list'),
            reverse('activity_create'),
            reverse('activity_edit', kwargs={'pk': self.activity.pk }),
            reverse('activity_detail', kwargs={'pk': self.activity.pk, 'slug': self.activity.slug }),
            reverse('event_list'),
            reverse('event_create'),
            reverse('booking_form', kwargs={'pk': self.event.pk }),
            reverse('event_edit', kwargs={'pk': self.event.pk }),
            reverse('event_detail', kwargs={'pk': self.event.pk, 'slug': self.event.slug }),
            reverse('mass_event_create'),
            '/admin/auth/group/',
            '/admin/users/customuser/',
            '/admin/plateformeweb/event/',
            '/admin/plateformeweb/condition/',
            '/admin/plateformeweb/activity/',
            # '/admin/plateformeweb/placetype/',
            '/admin/plateformeweb/place/',
            '/admin/plateformeweb/organization/',
            '/admin/plateformeweb/organizationperson/',
            '/admin/address/country/',
            '/admin/address/state/',
            '/admin/address/locality/',
            '/admin/address/address/',
            '/admin/avatar/avatar/',
            '/admin/post_office/email/',
            '/admin/post_office/log/',
            '/admin/post_office/emailtemplate/'
        ]
        for page in authorized_views:
            resp = self.client.get(page)
            assert resp.status_code == 200
