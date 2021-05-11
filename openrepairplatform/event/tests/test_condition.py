import pytest
from django.contrib.auth import get_user
from django.urls import reverse

from openrepairplatform.event.models import Condition
from openrepairplatform.user.factories import USER_PASSWORD

pytestmark = pytest.mark.django_db


@pytest.fixture
def condition_data(organization_factory):
    orga = organization_factory()
    return {
        "name": "cond_name",
        "organization": orga.pk,
        "price": 12.13,
        "description": "Lorem ipsum",
    }


def test_get_condition_delete(client, user_log, condition_factory):
    condition = condition_factory()
    response = client.get(reverse("event:condition_delete", args=[condition.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:condition_delete", args=[condition.pk]))
    assert response.status_code == 403
    current_user = get_user(client)
    condition.organization.admins.add(current_user)
    assert current_user in condition.organization.admins.all()
    response = client.get(reverse("event:condition_delete", args=[condition.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert condition.name in html
    assert condition.organization.name in html


def test_condition_delete(client, user_log, condition_factory):
    condition = condition_factory()
    assert Condition.objects.count() == 1
    response = client.post(reverse("event:condition_delete", args=[condition.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(reverse("event:condition_delete", args=[condition.pk]))
    assert response.status_code == 403
    current_user = get_user(client)
    condition.organization.admins.add(current_user)
    assert current_user in condition.organization.admins.all()
    response = client.post(reverse("event:condition_delete", args=[condition.pk]))
    assert Condition.objects.count() == 0
    assert response.status_code == 302
    assert response["Location"] == reverse(
        "organization_page",
        args=[condition.organization.slug],
    )


def test_get_condition_create_403(client, user_log, organization):
    response = client.get(reverse("event:condition_create", args=[organization.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:condition_create", args=[organization.pk]))
    assert response.status_code == 403
    html = response.content.decode()
    assert "pas administrateur" in html


def test_get_condition_create_403_not_in_orga(client_log, organization):
    response = client_log.get(reverse("event:condition_create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "pas administrateur" in html


def test_get_condition_create(client, user_log, organization):
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:condition_create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'une nouvelle Condition" in html


def test_condition_create(client, user_log, condition_data, organization):
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    assert Condition.objects.count() == 0
    response = client.post(
        reverse("event:condition_create", args=[organization.pk]),
        condition_data,
    )
    conditions = Condition.objects.all()
    assert response.status_code == 302
    assert len(conditions) == 1
    orga = conditions[0].organization
    assert response["Location"] == reverse("organization_page", args=[orga.slug])


def test_condition_create_invalid(client, user_log, condition_data, organization):
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    assert Condition.objects.count() == 0
    data = condition_data
    data["name"] = ""
    response = client.post(
        reverse("event:condition_create", args=[organization.pk]), data
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert Condition.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_condition_update_403(client, user_log, organization, condition):
    response = client.get(reverse("event:condition_edit", args=[condition.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:condition_edit", args=[condition.pk]))
    assert response.status_code == 403
    html = response.content.decode()
    assert "pas administrateur" in html


def test_get_condition_update_403_not_in_orga(client_log, organization, condition):
    response = client_log.get(reverse("event:condition_edit", args=[condition.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "pas administrateur" in html


def test_get_condition_update(client, user_log, condition, organization):
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:condition_edit", args=[condition.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert f"Mise à jour de '{condition.name}'" in html


def test_condition_update(client, user_log, condition, condition_data, organization):
    organization.admins.add(user_log)
    client.login(email=user_log.email, password=USER_PASSWORD)
    condition_data["name"] = "cond_name2"
    response = client.post(
        reverse("event:condition_edit", args=[condition.pk]), condition_data
    )
    conditions = Condition.objects.all()
    assert response.status_code == 302
    assert len(conditions) == 1
    orga = conditions[0].organization
    assert conditions[0].name == "cond_name2"
    assert response["Location"] == reverse("organization_page", args=[orga.slug])


def test_condition_no_price(condition_factory):
    condition = condition_factory(price=0)
    assert str(condition) == condition.name
