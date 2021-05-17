import pytest

from django.contrib.auth import get_user
from django.urls import reverse

from openrepairplatform.location.models import Place

pytestmark = pytest.mark.django_db


@pytest.fixture
def location_data(organization_factory):
    return {
        "name": "myname",
        "category": "test",
        "address": "1, rue Sylvestre",
        "longitude": 12,
        "latitude": 21,
        "description": "Lorem ipsum",
    }


def test_location_list(client):
    response = client.get(reverse("location:list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous


def test_location_api_list(client_log, place_factory):
    response = client_log.get(reverse("api_location:places"))
    places = response.json()
    assert response.status_code == 200
    assert len(places) == 0
    place = place_factory()
    response = client_log.get(reverse("api_location:places"))
    places = response.json()
    assert len(places) == 1
    assert places[0]["name"] == place.name
    assert set(places[0].keys()) == {
        "picture",
        "get_absolute_url",
        "orga_url",
        "orga_name",
        "name",
        "description",
        "address",
        "latitude",
        "longitude",
        "category",
        "future_events",
        "pk",
    }


def test_location_detail_context(client_log, place_factory):
    place = place_factory()
    response = client_log.get(reverse("location:detail", args=[place.pk, place.slug]))
    assert response.status_code == 200
    assert isinstance(response.context_data["place"], Place)
    assert place.pk == response.context_data["place"].pk
    assert (
        f"{place.name}, {place.address}" == f"{response.context_data['place']}"
    )


def test_get_location_delete(client_log, place_factory):
    current_user = get_user(client_log)
    place = place_factory()
    response = client_log.get(reverse("location:delete", args=[place.pk]))
    assert response.status_code == 403
    place.organization.admins.add(current_user)
    assert current_user in place.organization.admins.all()
    response_ok = client_log.get(reverse("location:delete", args=[place.pk]))
    html = response_ok.content.decode()
    assert response_ok.status_code == 200
    assert place.name in html
    assert place.address in html


def test_location_delete(client_log, place_factory):
    current_user = get_user(client_log)
    place = place_factory()
    assert Place.objects.count() == 1
    response = client_log.post(reverse("location:delete", args=[place.pk]))
    assert response.status_code == 403
    place.organization.admins.add(current_user)
    assert current_user in place.organization.admins.all()
    response_ok = client_log.post(reverse("location:delete", args=[place.pk]))
    assert Place.objects.count() == 0
    assert response_ok.status_code == 302
    assert response_ok["Location"] == reverse("location:list")


def test_get_location_create(client_log, organization):
    current_user = get_user(client_log)
    response = client_log.get(
        reverse("location:create", kwargs={"orga_pk": organization.pk})
    )
    assert response.status_code == 403
    organization.admins.add(current_user)
    assert current_user in organization.admins.all()
    response_ok = client_log.get(
        reverse("location:create", kwargs={"orga_pk": organization.pk})
    )
    assert response_ok.status_code == 200
    html = response_ok.content.decode()
    assert "Création d'un nouveau lieu" in html


def test_location_create(client_log, location_data, organization):
    current_user = get_user(client_log)
    assert Place.objects.count() == 0
    response = client_log.post(
        reverse("location:create", kwargs={"orga_pk": organization.pk}),
        location_data,
    )
    places = Place.objects.all()
    assert response.status_code == 403
    organization.admins.add(current_user)
    assert current_user in organization.admins.all()
    response_ok = client_log.post(
        reverse("location:create", kwargs={"orga_pk": organization.pk}),
        location_data,
    )
    assert response_ok.status_code == 302
    assert len(places) == 1
    assert response_ok["Location"] == reverse(
        "location:detail", args=[places[0].pk, places[0].slug]
    )


def test_location_create_invalid(client_log, location_data, organization):
    current_user = get_user(client_log)
    organization.admins.add(current_user)
    assert current_user in organization.admins.all()
    assert Place.objects.count() == 0
    data = location_data
    data["name"] = ""
    response = client_log.post(
        reverse("location:create", kwargs={"orga_pk": organization.pk}), data
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert Place.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_location_update(client_log, place_factory):
    current_user = get_user(client_log)
    place = place_factory()
    response = client_log.get(reverse("location:edit", args=[place.pk]))
    assert response.status_code == 403
    place.organization.admins.add(current_user)
    assert current_user in place.organization.admins.all()
    response_ok = client_log.get(reverse("location:edit", args=[place.pk]))
    html = response_ok.content.decode()
    assert response_ok.status_code == 200
    assert f"Mise à jour de '{place.name}" in html


def test_location_update(client_log, place_factory, location_data):
    current_user = get_user(client_log)
    place = place_factory()
    response = client_log.post(reverse("location:edit", args=[place.pk]), location_data)
    assert response.status_code == 403
    place.organization.admins.add(current_user)
    assert current_user in place.organization.admins.all()
    response_ok = client_log.post(
        reverse("location:edit", args=[place.pk]), location_data
    )
    places = Place.objects.all()
    assert response_ok.status_code == 302
    assert len(places) == 1
    assert places[0].name == "myname"
    assert response_ok["Location"] == reverse(
        "location:detail", args=[places[0].pk, places[0].slug]
    )
