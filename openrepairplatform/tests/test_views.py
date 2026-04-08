from http import HTTPStatus

import pytest
from django.test import TestCase, override_settings
from django.urls import reverse


class RobotsTxtTests(TestCase):
    def test_get(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")
        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], "User-Agent: *")

    def test_post_disallowed(self):
        response = self.client.post("/robots.txt")

        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)


# --- Tests des vues principales et des autocompletes ---
# --- Tests for root views and autocomplete views ---

pytestmark = pytest.mark.django_db


# ====================================================================
# HomeView — page d'accueil
# HomeView — homepage
# ====================================================================

def test_home_view(client):
    """La page d'accueil repond 200 et contient les compteurs dans le contexte.
    Homepage returns 200 and contains counters in context."""
    response = client.get(reverse("homepage"))
    assert response.status_code == 200
    assert "event_count" in response.context
    assert "user_count" in response.context
    assert "organization_count" in response.context


@override_settings(LOCATION=False)
def test_home_view_location_false(client):
    """Avec LOCATION=False, le template utilise est home.html.
    With LOCATION=False, the template used is home.html."""
    response = client.get(reverse("homepage"))
    assert response.status_code == 200
    assert "home.html" in [t.name for t in response.templates]


# ====================================================================
# AboutView — page a propos
# AboutView — about page
# ====================================================================

def test_about_view(client):
    """La page a propos repond 200 et le contexte contient about_menu='active'.
    About page returns 200 and context contains about_menu='active'."""
    response = client.get(reverse("a-propos"))
    assert response.status_code == 200
    assert response.context["about_menu"] == "active"


# ====================================================================
# OrganizationGroupsView — page groupes d'une organisation
# OrganizationGroupsView — organization groups page
# ====================================================================

def test_organization_groups_view_authenticated(client_log, organization_factory, user_log):
    """Un utilisateur authentifie peut voir la page groupes.
    An authenticated user can view the groups page."""
    organization = organization_factory()
    response = client_log.get(
        reverse("organization_groups", kwargs={"orga_slug": organization.slug})
    )
    assert response.status_code == 200
    assert response.context["groups_tab"] == "active"
    assert response.context["organization_menu"] == "active"
    # Verifie la presence des formulaires d'ajout
    # Check that add forms are present
    assert "add_admin_form" in response.context
    assert "add_active_form" in response.context
    assert "add_volunteer_form" in response.context
    assert "add_member_form" in response.context
    assert "emails" in response.context


def test_organization_groups_view_anonymous(client, organization_factory):
    """Un utilisateur anonyme peut aussi voir la page groupes
    (PermissionOrgaContextMixin ne bloque pas l'acces).
    Anonymous user can also view groups page
    (PermissionOrgaContextMixin does not block access)."""
    organization = organization_factory()
    response = client.get(
        reverse("organization_groups", kwargs={"orga_slug": organization.slug})
    )
    assert response.status_code == 200


# ====================================================================
# CustomUserAutocomplete — autocompletion utilisateurs
# CustomUserAutocomplete — user autocomplete
# ====================================================================

def test_user_autocomplete_authenticated(client_log, custom_user_factory):
    """Un utilisateur authentifie recoit des resultats d'autocompletion.
    An authenticated user gets autocomplete results."""
    custom_user_factory(first_name="Alice", last_name="Dupont", email="alice@test.com")
    response = client_log.get(reverse("user_autocomplete") + "?q=Alice")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    # Au moins un resultat correspondant a "Alice"
    # At least one result matching "Alice"
    assert len(data["results"]) >= 1


def test_user_autocomplete_anonymous(client):
    """Un utilisateur anonyme recoit une liste vide.
    An anonymous user gets an empty list."""
    response = client.get(reverse("user_autocomplete") + "?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


# ====================================================================
# PlaceAutocomplete — autocompletion lieux
# PlaceAutocomplete — place autocomplete
# ====================================================================

def test_place_autocomplete_authenticated(client_log, place_factory):
    """Un utilisateur authentifie recoit des lieux en autocompletion.
    An authenticated user gets places in autocomplete."""
    place = place_factory()
    response = client_log.get(
        reverse("place_autocomplete") + "?q=" + place.name[:3]
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) >= 1


def test_place_autocomplete_anonymous(client):
    """Un utilisateur anonyme recoit une liste vide.
    An anonymous user gets an empty list."""
    response = client.get(reverse("place_autocomplete") + "?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


# ====================================================================
# ActivityAutocomplete — autocompletion activites
# ActivityAutocomplete — activity autocomplete
# ====================================================================

def test_activity_autocomplete_authenticated(client_log, activity_factory):
    """Un utilisateur authentifie recoit des activites en autocompletion.
    An authenticated user gets activities in autocomplete."""
    activity = activity_factory()
    response = client_log.get(
        reverse("activity_autocomplete") + "?q=" + activity.name[:3]
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) >= 1


def test_activity_autocomplete_anonymous(client):
    """Un utilisateur anonyme recoit une liste vide.
    An anonymous user gets an empty list."""
    response = client.get(reverse("activity_autocomplete") + "?q=test")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


# ====================================================================
# ActiveOrgaAutocomplete — autocompletion membres actifs d'une orga
# ActiveOrgaAutocomplete — active members autocomplete for an org
# ====================================================================

def test_active_orga_autocomplete_as_active(
    client_log, organization_factory, user_log, custom_user_factory
):
    """Un membre actif de l'orga peut utiliser l'autocompletion.
    An active member can use autocomplete."""
    organization = organization_factory()
    organization.actives.add(user_log)
    other_user = custom_user_factory(
        first_name="Bernard", last_name="Martin", email="bernard@test.com"
    )
    organization.actives.add(other_user)
    # Sans parametre q= car union() + filter() n'est pas supporte par PostgreSQL
    # Without q= param because union() + filter() is not supported by PostgreSQL
    response = client_log.get(
        reverse(
            "user_orga_autocomplete",
            kwargs={"orga_slug": organization.slug},
        )
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) >= 1


def test_active_orga_autocomplete_anonymous(client, organization_factory):
    """Un utilisateur anonyme est redirige (pas d'acces).
    An anonymous user is redirected (no access)."""
    organization = organization_factory()
    response = client.get(
        reverse(
            "user_orga_autocomplete",
            kwargs={"orga_slug": organization.slug},
        )
        + "?q=test"
    )
    # HasActivePermissionMixin redirige vers login (302) ou interdit (403)
    # HasActivePermissionMixin redirects to login (302) or forbids (403)
    assert response.status_code in (302, 403)


def test_active_orga_autocomplete_non_active_user(
    client_log, organization_factory, user_log
):
    """Un utilisateur authentifie mais pas actif de l'orga est refuse.
    An authenticated user who is not active in the org is denied."""
    organization = organization_factory()
    response = client_log.get(
        reverse(
            "user_orga_autocomplete",
            kwargs={"orga_slug": organization.slug},
        )
        + "?q=test"
    )
    # L'utilisateur est connecte mais n'est pas membre actif → 403
    # User is logged in but not an active member → 403
    assert response.status_code == 403
