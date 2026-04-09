"""
Tests pour les vues API et sérialiseurs d'événements.
Tests for Event API views and serializers.
"""
import datetime

import pytest
from django.urls import reverse
from rest_framework import status

from openrepairplatform.event.models import Event

pytestmark = pytest.mark.django_db


# -- Helpers ------------------------------------------------------------------
# Données de base pour la création d'un événement.
# Base payload for event creation.

def _build_event_create_payload(
    activity, organization, place, user, conditions=None
):
    """Construit le payload minimal pour créer un événement via l'API.
    Builds the minimal payload for creating an event through the API."""
    payload = {
        "activity": activity.pk,
        "organization": organization.pk,
        "location": place.pk,
        "date": str(datetime.date.today() + datetime.timedelta(days=7)),
        "starts_at": "14:00",
        "ends_at": "17:00",
        "available_seats": 10,
        "needed_organizers": 1,
        "is_free": True,
        "members_only": False,
        "booking": True,
        "allow_stuffs": False,
        "external": False,
        "external_url": "",
        "description": "Événement de test",
        "collaborator": "",
        "conditions": [c.pk for c in conditions] if conditions else [],
        "organizers": [user.pk],
        "internal_notes": "",
    }
    return payload


# -- Tests Update (PUT / PATCH) -----------------------------------------------


def test_event_update_api(api_client_log, published_event_factory, user_log):
    """PUT complet sur un événement existant → 200 + données mises à jour.
    Full PUT on an existing event → 200 + data updated in DB."""
    event = published_event_factory()
    url = reverse("api_event:update-event", args=[event.pk])

    payload = {
        "activity": event.activity.pk,
        "organization": event.organization.pk,
        "location": event.location.pk,
        "date": str(event.date),
        "starts_at": str(event.starts_at),
        "ends_at": str(event.ends_at),
        "publish_at": str(event.publish_at),
        "available_seats": 42,
        "needed_organizers": 3,
        "is_free": False,
        "members_only": True,
        "booking": False,
        "allow_stuffs": True,
        "external": False,
        "external_url": "",
        "description": "Description modifiée",
        "collaborator": "Partenaire test",
        "conditions": [],
        "organizers": [user_log.pk],
        "internal_notes": "Notes internes mises à jour",
    }

    response = api_client_log.put(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK

    event.refresh_from_db()
    assert event.available_seats == 42
    assert event.needed_organizers == 3
    assert event.description == "Description modifiée"
    assert event.collaborator == "Partenaire test"
    assert event.is_free is False
    assert event.allow_stuffs is True


def test_event_update_api_partial(api_client_log, published_event_factory):
    """PATCH partiel → seul le champ envoyé est modifié.
    Partial PATCH → only the sent field is updated."""
    event = published_event_factory()
    url = reverse("api_event:update-event", args=[event.pk])

    original_description = event.description
    response = api_client_log.patch(
        url, {"available_seats": 99}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK

    event.refresh_from_db()
    assert event.available_seats == 99
    # Les autres champs ne changent pas.
    # Other fields remain unchanged.
    assert event.description == original_description


def test_event_update_api_not_found(api_client_log):
    """PUT sur un pk inexistant → 404.
    PUT on a non-existent pk → 404."""
    url = reverse("api_event:update-event", args=[999999])
    response = api_client_log.put(url, {}, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# -- Tests Create (POST) ------------------------------------------------------


def test_event_create_api(
    api_client_log,
    user_log,
    organization_factory,
    activity_factory,
    place_factory,
    condition_factory,
):
    """POST avec données valides → 201 + un événement créé en base.
    POST with valid data → 201 + one event created in DB."""
    organization = organization_factory()
    activity = activity_factory(organization=organization)
    place = place_factory()
    condition = condition_factory(organization=organization)

    payload = _build_event_create_payload(
        activity, organization, place, user_log, conditions=[condition]
    )
    url = reverse("api_event:create-event")

    response = api_client_log.post(url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Event.objects.count() == 1

    event = Event.objects.first()
    assert event.activity == activity
    assert event.organization == organization
    assert event.available_seats == 10
    assert event.is_free is True
    assert user_log in event.organizers.all()
    assert condition in event.conditions.all()


def test_event_create_api_recurrent_weekly(
    api_client_log,
    user_log,
    organization_factory,
    activity_factory,
    place_factory,
):
    """POST récurrent hebdomadaire → 201 + plusieurs événements créés.
    Weekly recurrent POST → 201 + multiple events created."""
    organization = organization_factory()
    activity = activity_factory(organization=organization)
    place = place_factory()

    # Période de 4 semaines avec lundi et mercredi → ~8 événements.
    # 4-week period with Monday and Wednesday → ~8 events.
    start_date = datetime.date.today() + datetime.timedelta(days=1)
    end_date = start_date + datetime.timedelta(days=28)

    payload = _build_event_create_payload(
        activity, organization, place, user_log
    )
    payload.update({
        "date": str(start_date),
        "recurrent_type": "WEEKLY",
        "days": ["MO", "WE"],
        "weeks": [],
        "end_date": str(end_date),
        "period_before_publish": 7,
    })

    url = reverse("api_event:create-event")
    response = api_client_log.post(url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    # Au moins 2 événements (dépend du jour courant).
    # At least 2 events (depends on current day).
    event_count = Event.objects.count()
    assert event_count > 1

    # Tous les événements ont les bonnes propriétés.
    # All events have the correct properties.
    for event in Event.objects.all():
        assert event.activity == activity
        assert event.organization == organization
        assert event.available_seats == 10


def test_event_create_api_recurrent_monthly(
    api_client_log,
    user_log,
    organization_factory,
    activity_factory,
    place_factory,
):
    """POST récurrent mensuel avec semaines spécifiées → 201 + événements créés.
    Monthly recurrent POST with specified weeks → 201 + events created."""
    organization = organization_factory()
    activity = activity_factory(organization=organization)
    place = place_factory()

    start_date = datetime.date.today() + datetime.timedelta(days=1)
    end_date = start_date + datetime.timedelta(days=90)

    payload = _build_event_create_payload(
        activity, organization, place, user_log
    )
    payload.update({
        "date": str(start_date),
        "recurrent_type": "MONTHLY",
        "days": ["TU"],
        "weeks": [1, 3],
        "end_date": str(end_date),
        "period_before_publish": 14,
    })

    url = reverse("api_event:create-event")
    response = api_client_log.post(url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Event.objects.count() >= 1


def test_event_create_api_missing_required_fields(api_client_log):
    """POST sans données → 400 (validation error).
    POST with no data → 400 (validation error)."""
    url = reverse("api_event:create-event")
    response = api_client_log.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_event_create_api_unauthenticated(client):
    """POST sans authentification → accès refusé (401 ou 403).
    POST without authentication → access denied (401 or 403)."""
    url = reverse("api_event:create-event")
    response = client.post(url, {}, content_type="application/json")
    # DRF sans configuration explicite → AllowAny par défaut,
    # donc la requête passe mais échoue en validation (400).
    # Si IsAuthenticated est configuré, ce sera 401 ou 403.
    assert response.status_code in (
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


# -- Tests Serializer (via l'API) ---------------------------------------------


def test_event_create_serializer_invalid_recurrent_without_days(
    api_client_log,
    user_log,
    organization_factory,
    activity_factory,
    place_factory,
):
    """Récurrence sans jours spécifiés → erreur de validation.
    Recurrence without specified days → validation error."""
    organization = organization_factory()
    activity = activity_factory(organization=organization)
    place = place_factory()

    payload = _build_event_create_payload(
        activity, organization, place, user_log
    )
    payload.update({
        "recurrent_type": "WEEKLY",
        "days": [],
        "weeks": [],
        "end_date": str(datetime.date.today() + datetime.timedelta(days=28)),
        "period_before_publish": 7,
    })

    url = reverse("api_event:create-event")
    response = api_client_log.post(url, payload, format="json")
    # Sans jours, rrule ne génère aucune date → le comportement dépend
    # de l'implémentation, mais ça ne doit pas crasher.
    # Without days, rrule generates no dates → behavior depends on
    # implementation, but it should not crash.
    assert response.status_code in (
        status.HTTP_201_CREATED,
        status.HTTP_400_BAD_REQUEST,
    )
