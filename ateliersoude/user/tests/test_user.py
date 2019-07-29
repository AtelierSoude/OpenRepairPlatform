import datetime
from urllib.parse import urlparse

import pytest
from django.contrib.auth import get_user
from django.core.management.base import CommandError
from django.core.management import call_command
from django.urls import reverse, resolve
from django.utils import timezone

from ateliersoude.event.views import _load_token
from ateliersoude.user.factories import USER_PASSWORD
from ateliersoude.user.models import CustomUser

pytestmark = pytest.mark.django_db


def test_command_superuser():
    assert CustomUser.objects.count() == 0
    call_command("createsuperuser", email="test@test.com", interactive=False)
    assert CustomUser.objects.count() == 1


def test_command_superuser_without_mail():
    assert CustomUser.objects.count() == 0
    with pytest.raises(CommandError):
        call_command("createsuperuser", email="", interactive=False)


def test_user_list_not_visible(client, custom_user):
    response = client.get(reverse("user:user_list"))
    assert response.status_code == 200
    assert response.context_data["object_list"].count() == 0


def test_user_list_visible(client, custom_user):
    custom_user.is_visible = True
    custom_user.save()
    response = client.get(reverse("user:user_list"))
    assert response.status_code == 200
    assert response.context_data["object_list"].count() == 1


def test_user_detail_not_visible(client, custom_user):
    response = client.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 404


def test_user_detail_visible(client, custom_user):
    custom_user.is_visible = True
    custom_user.save()
    response = client.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_detail_not_visible_but_staff(client_log, custom_user):
    user = get_user(client_log)
    user.is_staff = True
    user.save()
    response = client_log.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_detail_not_visible_but_same(client, custom_user):
    client.login(email=custom_user.email, password=USER_PASSWORD)
    response = client.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_detail_not_visible_but_active(
    client_log, custom_user, event_factory, organization
):
    user = get_user(client_log)
    organization.actives.add(user)
    event = event_factory(organization=organization)
    event.registered.add(custom_user)
    response = client_log.get(
        reverse("user:user_detail", kwargs={"pk": custom_user.pk})
    )
    assert response.status_code == 200


def test_user_create(client):
    assert CustomUser.objects.count() == 0
    response = client.post(
        reverse("user:user_create"),
        {
            "email": "test@test.fr",
            "first_name": "Test",
            "last_name": "Test",
            "street_address": "221 b Tester Street",
            "password1": USER_PASSWORD,
            "password2": USER_PASSWORD,
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("login")
    assert CustomUser.objects.count() == 1


def test_anonymous_user_create(client, event):
    assert CustomUser.objects.count() == 0
    response = client.post(
        reverse("user:create_and_book") + f"?event={event.pk}",
        {"email": "test@test.fr"},
    )
    anonymous_user = CustomUser.objects.first()
    assert response.status_code == 302
    url_parsed = urlparse(response.url)
    resolved = resolve(url_parsed.path)
    event_from_token, user = _load_token(resolved.kwargs["token"], "book")
    assert anonymous_user.first_name == ""
    assert anonymous_user.password == ""
    assert event.pk == event_from_token.pk


def test_anonymous_user_create_already_exists(client, event, custom_user):
    response = client.post(
        reverse("user:create_and_book") + f"?event={event.pk}",
        {"email": custom_user.email},
    )
    user = CustomUser.objects.first()
    assert response.status_code == 302
    assert user.pk == custom_user.pk
    url_parsed = urlparse(response.url)
    resolved = resolve(url_parsed.path)
    event_from_token, user = _load_token(resolved.kwargs["token"], "book")
    assert custom_user.first_name == user.first_name
    assert custom_user.password == user.password
    assert event.pk == event_from_token.pk


def test_anonymous_user_create_is_organizer(client, event, custom_user):
    event.organizers.add(custom_user)
    event.save()
    response = client.post(
        reverse("user:create_and_book") + f"?event={event.pk}",
        {"email": custom_user.email},
    )
    user = CustomUser.objects.first()
    assert response.status_code == 302
    assert user.pk == custom_user.pk
    assert user not in event.registered.all()


def test_anonymous_get_user_create(
    client, event_factory, organization, custom_user_factory
        ):
    user = custom_user_factory()
    organization.admins.add(user)
    in_two_hours = timezone.now() + datetime.timedelta(hours=2)
    two_hours_ago = timezone.now() - datetime.timedelta(hours=2)
    client.login(email=user.email, password=USER_PASSWORD)
    event_factory(
        organization=organization,
        starts_at=in_two_hours,
        publish_at=two_hours_ago,
    )
    response = client.get(
        reverse(
            "organization_page", kwargs={"orga_slug": organization.slug},
        )
    )
    assert response.status_code == 200


def test_user_update(client, custom_user_factory):
    user1 = custom_user_factory()
    user2 = custom_user_factory()
    data = {
        "first_name": "Test",
        "last_name": "Test",
        "email": "test@test.fr",
        "street_address": "221 b Tester Street",
    }
    response = client.post(
        reverse("user:user_update", kwargs={"pk": user1.pk}), data
    )
    assert response.status_code == 302
    client.login(email=user2.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:user_update", kwargs={"pk": user1.pk}), data
    )
    assert response.status_code == 403
    client.login(email=user1.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:user_update", kwargs={"pk": user1.pk}), data
    )
    assert response.url == reverse("user:user_detail", kwargs={"pk": user1.pk})
    user1.refresh_from_db()
    assert user1.first_name == "Test"


def test_present_with_more_info(client, event, custom_user_factory):
    assert event.presents.count() == 0
    user = custom_user_factory(last_name="", first_name="", street_address="")
    active = custom_user_factory()
    response = client.post(
        reverse("user:present_with_more_info", args=[event.pk, user.pk]),
        {
            "email": user.email,
            "last_name": "azerty",
            "first_name": "gfdsq",
            "street_address": "2, rue part-dieu",
            "amount_paid": 0,
        },
    )

    assert response.status_code == 302
    client.login(email=active.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:present_with_more_info", args=[event.pk, user.pk]),
        {
            "email": user.email,
            "last_name": "azerty",
            "first_name": "gfdsq",
            "street_address": "2, rue part-dieu",
            "amount_paid": 0,
        },
    )
    assert response.status_code == 403
    event.organization.actives.add(active)
    response = client.post(
        reverse("user:present_with_more_info", args=[event.pk, user.pk]),
        {
            "email": user.email,
            "last_name": "azerty",
            "first_name": "gfdsq",
            "street_address": "2, rue part-dieu",
            "amount_paid": 0,
        },
    )
    assert reverse("event:detail", args=[event.id, event.slug]) in response.url
    assert event.presents.count() == 1


def test_present_with_more_info_unknown_user(client, event, custom_user):
    assert CustomUser.objects.count() == 1
    assert event.presents.count() == 0
    response = client.post(
        reverse("user:present_create_user", args=[event.pk]),
        {
            "email": "testitest@example.com",
            "last_name": "azerty",
            "first_name": "gfdsq",
            "street_address": "2, rue part-dieu",
            "amount_paid": 0,
        },
    )
    assert response.status_code == 302
    assert "/accounts/login/" in response.url
    event.organization.actives.add(custom_user)
    client.login(email=custom_user.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:present_create_user", args=[event.pk]),
        {
            "email": "testitest@example.com",
            "last_name": "azerty",
            "first_name": "gfdsq",
            "street_address": "2, rue part-dieu",
            "amount_paid": 0,
        },
    )
    assert response.status_code == 302
    assert reverse("event:detail", args=[event.id, event.slug]) in response.url
    assert CustomUser.objects.count() == 2
    new_user = CustomUser.objects.exclude(pk=custom_user.pk).first()
    assert new_user.first_name == "gfdsq"
    assert new_user.last_name == "azerty"
    assert new_user.street_address == "2, rue part-dieu"
    assert new_user.email == "testitest@example.com"
    assert event.presents.count() == 1


def test_present_with_more_info_existing_user(client, event, custom_user):
    event.organization.actives.add(custom_user)
    event.registered.add(custom_user)
    assert event.presents.count() == 0
    assert event.registered.count() == 1
    client.login(email=custom_user.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:present_create_user", args=[event.pk]),
        {
            "email": custom_user.email,
            "last_name": "azerty",
            "first_name": "gfdsq",
            "street_address": "2, rue part-dieu",
            "amount_paid": 0,
        },
    )
    assert response.status_code == 302
    assert reverse("event:detail", args=[event.id, event.slug]) in response.url
    assert CustomUser.objects.count() == 1
    new_user = CustomUser.objects.first()
    assert new_user.first_name == "gfdsq"
    assert new_user.last_name == "azerty"
    assert new_user.street_address == "2, rue part-dieu"
    assert new_user.email == custom_user.email
    assert event.presents.count() == 1
    assert event.registered.count() == 0


def test_current_contribution(membership):
    membership.amount = 10
    assert membership.current_contribution == 10
    membership.first_payment = timezone.now() - datetime.timedelta(days=400)
    membership.save()
    assert membership.amount == 10
    assert membership.current_contribution == 0
    assert membership.amount == 0
