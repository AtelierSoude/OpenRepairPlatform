"""
Tests pour l'application inventory.
Couvre les modeles, vues, autocompletes et mixins.
---
Tests for the inventory app.
Covers models, views, autocompletes and mixins.
"""
import pytest
from datetime import date

from django.urls import reverse
from django.utils.text import slugify

from openrepairplatform.inventory.models import (
    Stuff,
    Device,
    Category,
    Observation,
    RepairFolder,
    Intervention,
)
from openrepairplatform.user.models import Organization

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────
#  Tests modeles / Model tests
# ──────────────────────────────────────────────


class TestStuffOwner:
    """Verifie la propriete owner et la methode set_owner de Stuff."""

    def test_stuff_owner_member(self, stuff_factory, custom_user_factory):
        """owner renvoie le member_owner quand il est defini."""
        user = custom_user_factory()
        stuff = stuff_factory(member_owner=user, organization_owner=None)
        assert stuff.owner == user

    def test_stuff_owner_organization(self, stuff_factory, organization_factory):
        """owner renvoie l'organization_owner quand member_owner est vide."""
        orga = organization_factory()
        stuff = stuff_factory(member_owner=None, organization_owner=orga)
        assert stuff.owner == orga

    def test_stuff_owner_none(self, stuff_factory):
        """owner renvoie None quand aucun proprietaire."""
        stuff = stuff_factory(member_owner=None, organization_owner=None)
        assert stuff.owner is None

    def test_stuff_set_owner_user(self, stuff_factory, custom_user_factory):
        """set_owner avec un CustomUser met member_owner et vide organization_owner."""
        user = custom_user_factory()
        stuff = stuff_factory(member_owner=None, organization_owner=None)
        stuff.set_owner(user)
        stuff.refresh_from_db()
        assert stuff.member_owner == user
        assert stuff.organization_owner is None

    def test_stuff_set_owner_organization(self, stuff_factory, organization_factory):
        """set_owner avec une Organization met organization_owner et vide member_owner."""
        orga = organization_factory()
        stuff = stuff_factory(member_owner=None, organization_owner=None)
        stuff.set_owner(orga)
        stuff.refresh_from_db()
        assert stuff.organization_owner == orga
        assert stuff.member_owner is None


class TestDeviceSlug:
    """Verifie la generation automatique du slug dans Device.save()."""

    def test_device_slug_generation(self, device_factory):
        """Le slug est genere a partir de category, brand et model."""
        device = device_factory()
        expected_slug = "-".join(
            (slugify(device.category), slugify(device.brand), slugify(device.model))
        )
        assert device.slug == expected_slug

    def test_device_slug_unique_on_save(self, category_factory, brand_factory):
        """Chaque device a un slug unique compose de ses 3 champs."""
        cat = category_factory(name="Electromenager")
        brand = brand_factory(name="Bosch")
        device = Device(category=cat, brand=brand, model="Serie 4")
        device.save()
        assert "electromenager" in device.slug
        assert "bosch" in device.slug
        assert "serie-4" in device.slug


class TestInterventionDate:
    """Verifie la propriete date de Intervention."""

    def test_intervention_date_uses_repair_date(self, intervention_factory):
        """Sans event, date renvoie repair_date."""
        intervention = intervention_factory(event=None)
        assert intervention.date == intervention.repair_date

    def test_intervention_date_uses_event_date(
        self, intervention_factory, published_event_factory
    ):
        """Avec un event, date renvoie event.date."""
        event = published_event_factory()
        intervention = intervention_factory(event=event)
        assert intervention.date == event.date


# ──────────────────────────────────────────────
#  Tests vues publiques / Public view tests
# ──────────────────────────────────────────────


class TestStockListView:
    """La page publique d'inventaire n'affiche que les objets visibles."""

    def test_stock_list_returns_200(self, client):
        url = reverse("inventory:stock_list")
        response = client.get(url)
        assert response.status_code == 200

    def test_stock_list_shows_only_visible(self, client, stuff_factory):
        """Seuls les Stuff avec is_visible=True apparaissent."""
        visible_stuff = stuff_factory(is_visible=True)
        hidden_stuff = stuff_factory(is_visible=False)
        url = reverse("inventory:stock_list")
        response = client.get(url)
        # Le queryset filtre sur is_visible=True
        # on verifie via le contexte du FilterView
        qs = response.context["object_list"]
        stuff_ids = [s.pk for s in qs]
        assert visible_stuff.pk in stuff_ids
        assert hidden_stuff.pk not in stuff_ids


class TestDeviceDetailView:
    def test_device_detail_returns_200(self, client, device_factory):
        device = device_factory()
        url = reverse("inventory:device_view", args=[device.pk, device.slug])
        response = client.get(url)
        assert response.status_code == 200


class TestStuffDetailView:
    def test_stuff_detail_returns_200(self, client_log, stuff_factory):
        stuff = stuff_factory()
        url = reverse("inventory:stuff_view", kwargs={"stuff_pk": stuff.pk})
        response = client_log.get(url)
        assert response.status_code == 200


# ──────────────────────────────────────────────
#  Tests vue OrganizationStockView
# ──────────────────────────────────────────────


class TestOrganizationStockView:
    """
    Necessite HasActivePermissionMixin : l'utilisateur doit etre actif dans l'orga.
    ---
    Requires HasActivePermissionMixin: user must be active in the organization.
    """

    def test_organization_stock_403_for_non_active(
        self, client_log, organization_factory
    ):
        """Un utilisateur non-actif dans l'orga recoit 403."""
        orga = organization_factory()
        url = reverse("organization_stock", kwargs={"orga_slug": orga.slug})
        response = client_log.get(url)
        assert response.status_code == 403

    def test_organization_stock_ok_for_active(
        self, client_log, user_log, organization_factory, stuff_factory
    ):
        """Un utilisateur actif dans l'orga peut voir le stock."""
        orga = organization_factory()
        # Ajouter l'utilisateur comme actif dans l'organisation
        # actives est un ManyToManyField sur Organization
        orga.actives.add(user_log)
        stuff = stuff_factory(organization_owner=orga, member_owner=None)
        url = reverse("organization_stock", kwargs={"orga_slug": orga.slug})
        response = client_log.get(url)
        assert response.status_code == 200


# ──────────────────────────────────────────────
#  Tests autocompletes
# ──────────────────────────────────────────────


class TestAutocompleteViews:
    """
    Les vues autocomplete (dal) renvoient 200 pour un utilisateur connecte.
    ---
    Autocomplete views (dal) return 200 for an authenticated user.
    """

    def test_device_autocomplete(self, client_log):
        url = reverse("inventory:device_autocomplete")
        response = client_log.get(url)
        assert response.status_code == 200

    def test_category_autocomplete(self, client_log):
        url = reverse("inventory:category_autocomplete")
        response = client_log.get(url)
        assert response.status_code == 200

    def test_brand_autocomplete(self, client_log):
        url = reverse("inventory:brand_autocomplete")
        response = client_log.get(url)
        assert response.status_code == 200

    def test_observation_autocomplete(self, client_log):
        url = reverse("inventory:observation_autocomplete")
        response = client_log.get(url)
        assert response.status_code == 200

    def test_observation_autocomplete_with_category(
        self, client_log, category_factory, observation_factory
    ):
        """
        Avec ?category=X, l'autocomplete calcule les scores de probabilite.
        ---
        With ?category=X, the autocomplete computes probability scores.
        """
        cat = category_factory()
        obs = observation_factory()
        url = reverse("inventory:observation_autocomplete")
        response = client_log.get(url, {"category": cat.pk})
        assert response.status_code == 200

    def test_reasoning_autocomplete(self, client_log):
        url = reverse("inventory:reasoning_autocomplete")
        response = client_log.get(url)
        assert response.status_code == 200

    def test_action_autocomplete(self, client_log):
        url = reverse("inventory:action_autocomplete")
        response = client_log.get(url)
        assert response.status_code == 200

    def test_status_autocomplete(self, client_log):
        url = reverse("inventory:status_autocomplete")
        response = client_log.get(url)
        assert response.status_code == 200


# ──────────────────────────────────────────────
#  Tests creation dossier / intervention
# ──────────────────────────────────────────────


class TestFolderAndInterventionCreate:

    def test_folder_create_get(self, client_log, stuff_factory):
        """GET sur la page de creation de dossier renvoie 200."""
        stuff = stuff_factory()
        url = reverse("inventory:create_folder", args=[stuff.pk])
        response = client_log.get(url)
        assert response.status_code == 200

    def test_intervention_create_get(self, client_log, repair_folder_factory):
        """GET sur la page de creation d'intervention renvoie 200."""
        folder = repair_folder_factory()
        url = reverse("inventory:create_intervention", args=[folder.pk])
        response = client_log.get(url)
        assert response.status_code == 200


# ──────────────────────────────────────────────
#  Tests mixin PermissionEditUserStuffMixin
# ──────────────────────────────────────────────


class TestPermissionEditUserStuffMixin:
    """
    Verifie que can_edit est dans le contexte quand l'utilisateur possede le stuff.
    ---
    Checks that can_edit is in context when the user owns the stuff.
    """

    def test_stuff_detail_can_edit_owner(self, client_log, user_log, stuff_factory):
        """Le proprietaire du stuff voit can_edit=True."""
        stuff = stuff_factory(member_owner=user_log, organization_owner=None)
        url = reverse("inventory:stuff_view", kwargs={"stuff_pk": stuff.pk})
        response = client_log.get(url)
        assert response.status_code == 200
        assert response.context.get("can_edit") is True

    def test_stuff_detail_cannot_edit_other(
        self, client_log, stuff_factory, custom_user_factory
    ):
        """Un utilisateur qui ne possede pas le stuff n'a pas can_edit."""
        other_user = custom_user_factory()
        stuff = stuff_factory(member_owner=other_user, organization_owner=None)
        url = reverse("inventory:stuff_view", kwargs={"stuff_pk": stuff.pk})
        response = client_log.get(url)
        assert response.status_code == 200
        # can_edit ne doit pas etre True (absent ou False)
        assert response.context.get("can_edit") is not True

    def test_stuff_detail_can_edit_orga_active(
        self, client_log, user_log, stuff_factory, organization_factory
    ):
        """
        Un utilisateur actif dans l'orga proprietaire peut editer le stuff.
        ---
        A user who is active in the owning org can edit the stuff.
        """
        orga = organization_factory()
        orga.actives.add(user_log)
        stuff = stuff_factory(member_owner=None, organization_owner=orga)
        url = reverse("inventory:stuff_view", kwargs={"stuff_pk": stuff.pk})
        response = client_log.get(url)
        assert response.status_code == 200
        assert response.context.get("can_edit") is True
