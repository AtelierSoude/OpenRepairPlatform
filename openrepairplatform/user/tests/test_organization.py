from os.path import join, dirname, abspath

import pytest
from django.contrib.auth import get_user

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from openrepairplatform.user.factories import USER_PASSWORD
from openrepairplatform.user.models import Organization, Fee

pytestmark = pytest.mark.django_db
FILES_DIR = join(dirname(abspath(__file__)), "files")


def test_organization_list(client, organization):
    response = client.get(reverse("user:organization_list"))
    assert response.status_code == 200
    assert response.context_data["object_list"].count() == 1


def test_organization_page(client, organization, user_log):
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(
        reverse("organization_page", kwargs={"orga_slug": organization.slug})
    )
    assert response.status_code == 200


def test_organization_members_view(client, organization, user_log, custom_user_factory):
    members = custom_user_factory.create_batch(10)
    organization.members.set(members)
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(
        reverse("organization_members", kwargs={"orga_slug": organization.slug})
    )
    assert response.status_code == 200
    assert set(list(members)) == set(list(organization.members.all()))


def test_organization_events_view(client, organization, user_log, event_factory):
    organization.admins.add(user_log)
    events = event_factory.create_batch(10, organization=organization)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(
        reverse("organization_events", kwargs={"orga_slug": organization.slug})
    )
    assert response.status_code == 200
    assert set(list(response.context_data["events"])) == set(list(events))
    assert response.context_data["search_form"]
    assert response.context_data["organization"]
    assert response.context_data["today"]


def test_organization_details_view(client, organization, user_log, place_factory):
    organization.actives.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(
        reverse("organization_details", kwargs={"orga_slug": organization.slug})
    )
    assert response.status_code == 200


def test_organization_create(client_log, custom_user):
    custom_user.is_staff = True
    custom_user.save()
    assert Organization.objects.count() == 0
    image_file = File(open(join(FILES_DIR, "test.png"), "rb"))
    upload_image = SimpleUploadedFile(
        "image.png", image_file.read(), content_type="multipart/form-data"
    )
    response = client_log.post(
        reverse("user:organization_create"),
        {
            "name": "Test",
            "description": """
                <h1> Test </h1>
                <strong> gras </strong>
                <u style="text-decoration-line: underline;"> sdfsdf </u>
            """,
            "picture": upload_image,
        },
    )
    assert response.status_code == 302
    assert "/admin/login/?next=" in response.url
    client_log.login(email=custom_user.email, password=USER_PASSWORD)
    image_file = File(open(join(FILES_DIR, "test.png"), "rb"))
    upload_image = SimpleUploadedFile(
        "image.png", image_file.read(), content_type="multipart/form-data"
    )
    response = client_log.post(
        reverse("user:organization_create"),
        {
            "name": "Test",
            "description": """
                <h1> Test </h1>
                <strong> gras </strong>
                <u style="text-decoration-line: underline;"> sdfsdf </u>
            """,
            "picture": upload_image,
        },
    )
    assert Organization.objects.count() == 1
    assert Organization.objects.first().slug in response.url


def test_organization_update(client_log, organization):
    response = client_log.post(
        reverse("user:organization_update", kwargs={"pk": organization.pk}),
        {"name": "Test Orga", "description": "Test"},
    )
    assert response.status_code == 403
    user = get_user(client_log)
    organization.admins.add(user)
    response = client_log.post(
        reverse("user:organization_update", kwargs={"pk": organization.pk}),
        {"name": "Test Orga", "description": "Test"},
    )
    assert response.status_code == 302
    organization.refresh_from_db()
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.name == "Test Orga"


def test_organization_delete(client_log, organization):
    assert Organization.objects.count() == 1
    response = client_log.post(
        reverse("user:organization_delete", kwargs={"pk": organization.pk})
    )
    assert response.status_code == 403
    user = get_user(client_log)
    organization.admins.add(user)
    response = client_log.post(
        reverse("user:organization_delete", kwargs={"pk": organization.pk})
    )
    assert response.status_code == 302
    assert response.url == reverse("user:organization_list")
    assert Organization.objects.count() == 0


def test_add_admin_to_organization_forbidden(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:organization_add_admin", kwargs={"pk": organization.pk}),
        {"email": user_log.email},
    )
    assert response.status_code == 403


def test_add_admin_to_organization(custom_user_factory, client, organization):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.admins.count() == 1
    response = client.post(
        reverse("user:organization_add_admin", kwargs={"pk": organization.pk}),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.admins.count() == 2


def test_add_admin_to_organization_wrong_user(custom_user, client, organization):
    organization.admins.add(custom_user)
    assert client.login(email=custom_user.email, password=USER_PASSWORD)
    assert organization.admins.count() == 1
    response = client.post(
        reverse("user:organization_add_admin", kwargs={"pk": organization.pk}),
        {"email": "unknown@something.org"},
    )
    assert response.status_code == 302
    assert organization.admins.count() == 1


def test_add_active_to_organization_forbidden(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:organization_add_active", kwargs={"pk": organization.pk}),
        {"email": user_log.email},
    )
    assert response.status_code == 403


def test_add_active_to_organization(custom_user_factory, client, organization):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.actives.count() == 0
    response = client.post(
        reverse("user:organization_add_active", kwargs={"pk": organization.pk}),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    actives = organization.actives.all()
    assert len(actives) == 1
    assert actives[0].pk == user.pk


def test_add_admin_to_actives_of_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    organization.admins.add(user)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.actives.count() == 0
    response = client.post(
        reverse("user:organization_add_active", kwargs={"pk": organization.pk}),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.actives.count() == 0


def test_add_active_to_admins_of_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    organization.actives.add(user)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.actives.count() == 1
    assert organization.admins.count() == 1
    response = client.post(
        reverse("user:organization_add_admin", kwargs={"pk": organization.pk}),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.actives.count() == 0
    assert organization.admins.count() == 2


def test_remove_active_from_organization_forbidden(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse(
            "user:remove_from_actives",
            kwargs={
                "pk": organization.pk,
                "user_pk": 123,  # we don't care, we'll get a 403 anyway
            },
        )
    )
    assert response.status_code == 403


def test_remove_active_from_organization(custom_user_factory, client, organization):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.actives.add(user)
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.actives.count() == 1
    response = client.post(
        reverse(
            "user:remove_from_actives",
            kwargs={"pk": organization.pk, "user_pk": user.pk},
        )
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.actives.count() == 0


def test_remove_admin_from_organization(custom_user_factory, client, organization):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    organization.admins.add(user)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.admins.count() == 2
    response = client.post(
        reverse(
            "user:remove_from_admins",
            kwargs={"pk": organization.pk, "user_pk": user.pk},
        )
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.admins.count() == 1


def test_add_volunteer_to_organization_forbidden(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:organization_add_volunteer", kwargs={"pk": organization.pk}),
        {"email": user_log.email},
    )
    assert response.status_code == 403


def test_add_volunteer_to_organization(custom_user_factory, client, organization):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.actives.count() == 0
    response = client.post(
        reverse("user:organization_add_volunteer", kwargs={"pk": organization.pk}),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    volunteers = organization.volunteers.all()
    assert len(volunteers) == 1
    assert volunteers[0].pk == user.pk


def test_add_admin_to_volunteers_of_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    organization.admins.add(user)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.actives.count() == 0
    response = client.post(
        reverse("user:organization_add_volunteer", kwargs={"pk": organization.pk}),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.volunteers.count() == 0


def test_add_volunteer_to_admins_of_organization(
    custom_user_factory, client, organization
):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    organization.volunteers.add(user)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.volunteers.count() == 1
    assert organization.admins.count() == 1
    response = client.post(
        reverse("user:organization_add_admin", kwargs={"pk": organization.pk}),
        {"email": user.email},
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.volunteers.count() == 0
    assert organization.admins.count() == 2


def test_remove_volunteer_from_organization_forbidden(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse(
            "user:remove_from_volunteers",
            kwargs={
                "pk": organization.pk,
                "user_pk": 123,  # we don't care, we'll get a 403 anyway
            },
        )
    )
    assert response.status_code == 403


def test_remove_volunteer_from_organization(custom_user_factory, client, organization):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.volunteers.add(user)
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.volunteers.count() == 1
    response = client.post(
        reverse(
            "user:remove_from_volunteers",
            kwargs={"pk": organization.pk, "user_pk": user.pk},
        )
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_page",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.volunteers.count() == 0


def test_extended_event_list(client, custom_user, event_factory, organization):
    for _ in range(13):
        event_factory(organization=organization)
    path = reverse(
        "user:organization_all_events",
        kwargs={
            "orga_pk": organization.pk,
            "slug": organization.slug,
            "page": 1,
        },
    )
    resp = client.get(path)
    assert resp.status_code == 302
    assert "/accounts/login" in resp.url
    organization.volunteers.add(custom_user)
    assert client.login(email=custom_user.email, password=USER_PASSWORD)
    resp = client.get(path)
    assert resp.status_code == 200
    assert len(resp.context["event_list"]) == 6
    assert resp.context["paginator"].num_pages == 3


def test_add_member_to_organization(custom_user_factory, client, organization):
    user = custom_user_factory()
    admin = custom_user_factory()
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.admins.count() == 1
    assert Fee.objects.count() == 0
    response = client.post(
        reverse("user:organization_add_member", kwargs={"pk": organization.pk}),
        {
            "email": user.email,
            "first_name": "Michel",
            "last_name": "Miche",
            "street_address": "11 rue du test",
            "amount_paid": 5,
            "payment": 1,
            "date": timezone.now().date().strftime("%Y-%m-%d"),
        },
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_members",
        kwargs={"orga_slug": organization.slug},
    )
    assert organization.members.count() == 1
    assert Fee.objects.count() == 1


def test_re_add_member_to_organization(
    custom_user_factory, client, organization, membership_factory
):
    user = custom_user_factory()
    admin = custom_user_factory()
    membership_factory(user=user, organization=organization)
    organization.admins.add(admin)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.admins.count() == 1
    response = client.post(
        reverse("user:organization_add_member", kwargs={"pk": organization.pk}),
        {
            "email": user.email,
            "first_name": "Michel",
            "last_name": "Miche",
            "street_address": "11 rue du test",
            "amount_paid": 5,
            "payment": 1,
            "date": timezone.now().date().strftime("%Y-%m-%d"),
        },
    )
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_members",
        kwargs={"orga_slug": organization.slug},
    )
    assert user.first_name != "Michel"
    assert organization.members.count() == 1


def test_update_member_to_organization(
    custom_user_factory, client, organization, membership_factory
):
    admin = custom_user_factory()
    organization.admins.add(admin)
    user = custom_user_factory()
    membership = membership_factory(user=user, organization=organization, amount=1)
    assert client.login(email=admin.email, password=USER_PASSWORD)
    assert organization.admins.count() == 1
    assert Fee.objects.count() == 0
    response = client.post(
        reverse(
            "user:organization_update_member",
            kwargs={"orga_pk": organization.pk, "pk": user.pk},
        ),
        {
            "email": user.email,
            "first_name": "Michel",
            "last_name": "Miche",
            "street_address": "11 rue du test",
            "amount_paid": 5,
            "payment": 1,
            "date": timezone.now().date().strftime("%Y-%m-%d"),
        },
    )
    membership.refresh_from_db()
    assert response.status_code == 302
    assert response.url == reverse(
        "organization_members",
        kwargs={"orga_slug": organization.slug},
    )
    user.refresh_from_db()
    assert user.first_name == "Michel"
    assert membership.amount == 6
    assert organization.members.count() == 1
    assert Fee.objects.count() == 1

    # Test first_payment update
    membership.first_payment = timezone.now() - timedelta(days=400)
    membership.save()
    response = client.post(
        reverse(
            "user:organization_update_member",
            kwargs={"orga_pk": organization.pk, "pk": user.pk},
        ),
        {
            "email": user.email,
            "first_name": "Michel",
            "last_name": "Miche",
            "street_address": "11 rue du test",
            "amount_paid": 5,
            "payment": 1,
            "date": timezone.now().date().strftime("%Y-%m-%d"),
        },
    )
    membership.refresh_from_db()
    assert response.status_code == 302
    assert membership.current_contribution == 10
    assert membership.amount == 10
