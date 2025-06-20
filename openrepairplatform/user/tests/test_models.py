from datetime import date
import pytest

from django.urls import reverse
from openrepairplatform.user.factories import USER_PASSWORD

pytestmark = pytest.mark.django_db


def test_create_membership_without_fee(
    custom_user_factory, user_log, client, organization
):
    user = custom_user_factory()
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:organization_add_member", kwargs={"pk": organization.pk}),
        {
            "email": user.email,
            "amount_paid": 0,
            "payment": 1,
            "first_name": "Test",
            "last_name": "Test",
            "street_address": "11 rue du test",
            "date": date.today().strftime("%Y-%m-%d"),
        },
        HTTP_REFERER="/"
    )
    assert response.status_code == 302
    organization.refresh_from_db()
    assert organization.memberships.count() == 1


def test_create_membership_with_fee(
    custom_user_factory, user_log, client, organization
):
    user = custom_user_factory()
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse("user:organization_add_member", kwargs={"pk": organization.pk}),
        {
            "email": user.email,
            "amount_paid": 13,
            "payment": 1,
            "first_name": "Test",
            "last_name": "Test",
            "street_address": "11 rue du test",
            "date": date.today().strftime("%Y-%m-%d"),
        },
        HTTP_REFERER="/"
    )
    assert response.status_code == 302
    organization.refresh_from_db()
    assert organization.memberships.count() == 1
    assert organization.memberships.first().fees.count() == 1
    assert organization.memberships.first().amount == 13


def test_update_membership_with_fee(user_log, client, membership):
    membership.organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse(
            "user:organization_update_member",
            kwargs={"orga_pk": membership.organization.pk, "pk": membership.user.pk}),
        {
            "email": membership.user.email,
            "amount_paid": 13,
            "payment": 1,
            "first_name": "Test",
            "last_name": "Test",
            "street_address": "11 rue du test",
            "date": date.today().strftime("%Y-%m-%d"),
        },
        HTTP_REFERER="/"
    )
    assert response.status_code == 302
    membership.organization.refresh_from_db()
    assert membership.organization.memberships.count() == 1
    assert membership.organization.memberships.first().fees.count() == 1
    assert membership.organization.memberships.first().amount == 13


def test_delete_membership(user_log, client, membership):
    membership.organization.admins.add(user_log)
    organization = membership.organization
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(
        reverse(
            "user:delete_member",
            kwargs={"pk": membership.pk}),
        {}, HTTP_REFERER="/"
    )
    assert response.status_code == 302
    organization.refresh_from_db()
    assert organization.memberships.count() == 0


def test_delete_fee(user_log, client, membership, fee_factory):
    membership.organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    fee = fee_factory(
        membership=membership,
        organization=membership.organization,
        amount=12
    )
    assert membership.fees.count() == 1
    assert membership.amount == 12
    response = client.post(
        reverse(
            "user:fee_delete",
            kwargs={"pk": fee.pk}),
        {}, HTTP_REFERER="/"
    )
    assert response.status_code == 302
    membership.refresh_from_db()
    assert membership.fees.count() == 0
    assert membership.amount == 0
