"""
Tests pour les webhooks HelloAsso et TiBillet.
Vérifie la réception, la validation, l'idempotence et les filtres.

Tests for HelloAsso and TiBillet webhooks.
Checks reception, validation, idempotency and filters.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from openrepairplatform.user.models import (
    CustomUser,
    Fee,
    Membership,
    Organization,
    SourceChoice,
    WebHook,
)

pytestmark = pytest.mark.django_db


# --- Fixtures ---


@pytest.fixture
def organization():
    return Organization.objects.create(name="Atelier Test")


@pytest.fixture
def webhook_helloasso(organization):
    return WebHook.objects.create(
        organization=organization,
        source=SourceChoice.SOURCE_HELLOASSO,
    )


@pytest.fixture
def webhook_tibillet(organization):
    return WebHook.objects.create(
        organization=organization,
        source=SourceChoice.SOURCE_TIBILLET,
    )


@pytest.fixture
def api_client():
    return APIClient()


def webhook_url(webhook):
    """Construit l'URL du webhook / Builds the webhook URL"""
    return reverse("api_user:membership_webhook", kwargs={"webhook_pk": webhook.pk})


# --- Payloads de référence ---


def helloasso_payload(payment_id=15222, email="ha@test.com"):
    """Payload HelloAsso valide / Valid HelloAsso payload"""
    return {
        "eventType": "Payment",
        "data": {
            "id": payment_id,
            "amount": 2000,
            "date": "2026-04-08T12:00:00Z",
            "state": "Authorized",
            "order": {"formType": "Checkout"},
            "payer": {
                "email": email,
                "firstName": "Jean",
                "lastName": "Dupont",
            },
            "items": [
                {"amount": 2000, "type": "Payment", "name": "Adhésion"}
            ],
        },
        "metadata": {},
    }


def tibillet_payload(uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", email="tb@test.com"):
    """Payload TiBillet valide / Valid TiBillet payload"""
    return {
        "object": "membership",
        "pk": "42",
        "uuid": uuid,
        "state": "A",
        "state_display": "Payé en ligne",
        "email": email,
        "first_name": "Marie",
        "last_name": "Martin",
        "pseudo": "mmartin",
        "contribution_value": 20.0,
        "last_contribution": "2026-04-08T12:00:00Z",
        "deadline": "2027-04-08T23:59:59Z",
        "date_added": "2026-04-08T13:20:00Z",
        "payment_method": "SN",
        "payment_method_name": "Online: Stripe CC",
        "price_name": "Adhésion annuelle",
        "price_uuid": "11111111-2222-3333-4444-555555555555",
        "product_name": "Adhésion",
        "product_uuid": "66666666-7777-8888-9999-000000000000",
        "organisation": "Association Test",
        "organisation_id": "aabbccdd-eeff-0011-2233-445566778899",
        "is_valid": True,
        "newsletter": True,
        "postal_code": 75001,
        "birth_date": "1990-01-15",
        "phone": "0612345678",
        "custom_form": {},
        "option_generale": [],
        "option_names": [],
        "user": 1,
        "card_number": None,
        "last_action": "2026-04-08T13:20:00Z",
        "comment": "",
        "asset_fedow": None,
        "stripe_id_subscription": None,
        "last_stripe_invoice": None,
        "member_name": "Marie Martin",
        "product_img": None,
        "datetime": "2026-04-08T13:20:00Z",
    }


# ============================================================
# Tests HelloAsso
# ============================================================


class TestHelloAssoWebhook:
    """Tests pour le flux HelloAsso / Tests for the HelloAsso flow"""

    def test_helloasso_webhook_creates_membership_and_fee(
        self, api_client, webhook_helloasso, organization
    ):
        """Un payload HelloAsso valide crée un user, une adhésion et une cotisation.
        A valid HelloAsso payload creates a user, membership and fee."""
        # On simule l'IP HelloAsso autorisée
        # Simulating the allowed HelloAsso IP
        response = api_client.post(
            webhook_url(webhook_helloasso),
            data=helloasso_payload(),
            format="json",
            REMOTE_ADDR="51.138.206.200",
        )

        assert response.status_code == 201
        assert CustomUser.objects.filter(email="ha@test.com").exists()
        assert Membership.objects.filter(
            user__email="ha@test.com", organization=organization
        ).exists()
        assert Fee.objects.filter(id_payment="15222").exists()

        fee = Fee.objects.get(id_payment="15222")
        # HelloAsso envoie en centimes → 2000 ÷ 100 = 20€
        # HelloAsso sends in cents → 2000 ÷ 100 = 20€
        assert fee.amount == 20

    def test_helloasso_idempotence(self, api_client, webhook_helloasso):
        """Le même paiement HelloAsso ne crée pas de doublon.
        The same HelloAsso payment doesn't create a duplicate."""
        url = webhook_url(webhook_helloasso)

        # Premier appel → 201
        # First call → 201
        response_1 = api_client.post(
            url, data=helloasso_payload(), format="json", REMOTE_ADDR="51.138.206.200",
        )
        assert response_1.status_code == 201

        # Deuxième appel avec le même ID → 200 ignored
        # Second call with the same ID → 200 ignored
        response_2 = api_client.post(
            url, data=helloasso_payload(), format="json", REMOTE_ADDR="51.138.206.200",
        )
        assert response_2.status_code == 200
        assert response_2.data["status"] == "ignored"
        assert Fee.objects.filter(id_payment="15222").count() == 1

    def test_helloasso_wrong_ip_returns_403(self, api_client, webhook_helloasso):
        """Une IP non autorisée est rejetée.
        An unauthorized IP is rejected."""
        response = api_client.post(
            webhook_url(webhook_helloasso),
            data=helloasso_payload(),
            format="json",
            REMOTE_ADDR="1.2.3.4",
        )
        assert response.status_code == 403

    def test_helloasso_wrong_event_type_is_ignored(self, api_client, webhook_helloasso):
        """Un eventType non-Payment est ignoré.
        A non-Payment eventType is ignored."""
        payload = helloasso_payload()
        payload["eventType"] = "Order"

        response = api_client.post(
            webhook_url(webhook_helloasso),
            data=payload,
            format="json",
            REMOTE_ADDR="51.138.206.200",
        )
        assert response.status_code == 200
        assert response.data["status"] == "ignored"

    def test_helloasso_wrong_form_type_is_ignored(self, api_client, webhook_helloasso):
        """Un formType non accepté (ex: Event) est ignoré.
        An unaccepted formType (e.g. Event) is ignored."""
        payload = helloasso_payload()
        payload["data"]["order"]["formType"] = "Event"

        response = api_client.post(
            webhook_url(webhook_helloasso),
            data=payload,
            format="json",
            REMOTE_ADDR="51.138.206.200",
        )
        assert response.status_code == 200
        assert response.data["status"] == "ignored"
        assert not Fee.objects.exists()

    def test_helloasso_non_authorized_state_is_ignored(self, api_client, webhook_helloasso):
        """Un paiement avec un state != Authorized est ignoré.
        A payment with state != Authorized is ignored."""
        payload = helloasso_payload()
        payload["data"]["state"] = "Pending"

        response = api_client.post(
            webhook_url(webhook_helloasso),
            data=payload,
            format="json",
            REMOTE_ADDR="51.138.206.200",
        )
        assert response.status_code == 200
        assert response.data["status"] == "ignored"
        assert not Fee.objects.exists()

    def test_helloasso_donation_items_are_ignored(self, api_client, webhook_helloasso):
        """Un paiement dont tous les items sont des donations est ignoré.
        A payment where all items are donations is ignored."""
        payload = helloasso_payload()
        payload["data"]["items"] = [
            {"amount": 1000, "type": "Donation", "name": "Don libre"}
        ]

        response = api_client.post(
            webhook_url(webhook_helloasso),
            data=payload,
            format="json",
            REMOTE_ADDR="51.138.206.200",
        )
        assert response.status_code == 200
        assert response.data["status"] == "ignored"
        assert not Fee.objects.exists()

    def test_helloasso_invalid_payload_returns_400(self, api_client, webhook_helloasso):
        """Un payload mal formé retourne 400.
        A malformed payload returns 400."""
        response = api_client.post(
            webhook_url(webhook_helloasso),
            data={"eventType": "Payment", "data": {"id": "not_a_number"}},
            format="json",
            REMOTE_ADDR="51.138.206.200",
        )
        assert response.status_code == 400

    def test_helloasso_existing_user_gets_new_fee(
        self, api_client, webhook_helloasso, organization
    ):
        """Si l'utilisateur existe déjà, on crée une nouvelle cotisation sans doublon user.
        If the user already exists, a new fee is created without duplicating the user."""
        # Créer l'utilisateur avant le webhook
        # Create the user before the webhook
        CustomUser.objects.create(
            email="ha@test.com", first_name="Existing", last_name="User"
        )

        response = api_client.post(
            webhook_url(webhook_helloasso),
            data=helloasso_payload(),
            format="json",
            REMOTE_ADDR="51.138.206.200",
        )

        assert response.status_code == 201
        assert CustomUser.objects.filter(email="ha@test.com").count() == 1
        assert Fee.objects.filter(id_payment="15222").exists()

    def test_helloasso_checkout_and_membership_form_types_both_work(
        self, api_client, webhook_helloasso
    ):
        """Les deux formTypes acceptés (Checkout et Membership) créent une adhésion.
        Both accepted formTypes (Checkout and Membership) create a membership."""
        url = webhook_url(webhook_helloasso)

        for i, form_type in enumerate(["Checkout", "Membership"]):
            payload = helloasso_payload(payment_id=30000 + i, email=f"ft-{i}@test.com")
            payload["data"]["order"]["formType"] = form_type

            response = api_client.post(
                url, data=payload, format="json", REMOTE_ADDR="51.138.206.200",
            )
            assert response.status_code == 201, (
                f"formType '{form_type}' devrait être accepté / should be accepted"
            )


# ============================================================
# Tests TiBillet
# ============================================================


class TestTiBilletWebhook:
    """Tests pour le flux TiBillet / Tests for the TiBillet flow"""

    def test_tibillet_webhook_creates_membership_and_fee(
        self, api_client, webhook_tibillet, organization
    ):
        """Un payload TiBillet valide crée un user, une adhésion et une cotisation.
        A valid TiBillet payload creates a user, membership and fee."""
        response = api_client.post(
            webhook_url(webhook_tibillet),
            data=tibillet_payload(),
            format="json",
            REMOTE_ADDR="51.77.151.34",
        )

        assert response.status_code == 201
        assert CustomUser.objects.filter(email="tb@test.com").exists()
        assert Membership.objects.filter(
            user__email="tb@test.com",
            organization=organization,
            source=SourceChoice.SOURCE_TIBILLET,
        ).exists()
        assert Fee.objects.filter(
            id_payment="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        ).exists()

        fee = Fee.objects.get(id_payment="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        # TiBillet envoie déjà en euros → 20.0 → 20
        # TiBillet already sends in euros → 20.0 → 20
        assert fee.amount == 20

    def test_tibillet_idempotence(self, api_client, webhook_tibillet):
        """Le même UUID TiBillet ne crée pas de doublon.
        The same TiBillet UUID doesn't create a duplicate."""
        url = webhook_url(webhook_tibillet)

        response_1 = api_client.post(
            url, data=tibillet_payload(), format="json", REMOTE_ADDR="51.77.151.34",
        )
        assert response_1.status_code == 201

        response_2 = api_client.post(
            url, data=tibillet_payload(), format="json", REMOTE_ADDR="51.77.151.34",
        )
        assert response_2.status_code == 200
        assert response_2.data["status"] == "ignored"
        assert Fee.objects.filter(
            id_payment="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        ).count() == 1

    def test_tibillet_wrong_ip_returns_403(self, api_client, webhook_tibillet):
        """Une IP non autorisée est rejetée.
        An unauthorized IP is rejected."""
        response = api_client.post(
            webhook_url(webhook_tibillet),
            data=tibillet_payload(),
            format="json",
            REMOTE_ADDR="1.2.3.4",
        )
        assert response.status_code == 403

    def test_tibillet_invalid_state_is_ignored(self, api_client, webhook_tibillet):
        """Un state non accepté (ex: WP = waiting payment) est ignoré.
        An unaccepted state (e.g. WP = waiting payment) is ignored."""
        payload = tibillet_payload()
        payload["state"] = "WP"

        response = api_client.post(
            webhook_url(webhook_tibillet),
            data=payload,
            format="json",
            REMOTE_ADDR="51.77.151.34",
        )
        assert response.status_code == 200
        assert response.data["status"] == "ignored"
        assert not Fee.objects.exists()

    def test_tibillet_null_deadline_is_ignored(self, api_client, webhook_tibillet):
        """Un deadline null (adhésion pas encore validée) est ignoré.
        A null deadline (membership not yet validated) is ignored."""
        payload = tibillet_payload()
        payload["deadline"] = None

        response = api_client.post(
            webhook_url(webhook_tibillet),
            data=payload,
            format="json",
            REMOTE_ADDR="51.77.151.34",
        )
        assert response.status_code == 200
        assert response.data["status"] == "ignored"
        assert not Fee.objects.exists()

    def test_tibillet_wrong_object_is_ignored(self, api_client, webhook_tibillet):
        """Un object != 'membership' (ex: reservation) est ignoré.
        An object != 'membership' (e.g. reservation) is ignored."""
        payload = tibillet_payload()
        payload["object"] = "reservation"

        response = api_client.post(
            webhook_url(webhook_tibillet),
            data=payload,
            format="json",
            REMOTE_ADDR="51.77.151.34",
        )
        assert response.status_code == 200
        assert response.data["status"] == "ignored"

    def test_tibillet_all_accepted_states_work(self, api_client, webhook_tibillet):
        """Tous les states acceptés (A, O, AV, D) créent une adhésion.
        All accepted states (A, O, AV, D) create a membership."""
        for i, state_code in enumerate(["A", "O", "AV", "D"]):
            unique_uuid = f"state-test-{state_code}-{i}"
            unique_email = f"state-{state_code}@test.com"
            payload = tibillet_payload(uuid=unique_uuid, email=unique_email)
            payload["state"] = state_code

            response = api_client.post(
                webhook_url(webhook_tibillet),
                data=payload,
                format="json",
                REMOTE_ADDR="51.77.151.34",
            )
            assert response.status_code == 201, (
                f"state '{state_code}' devrait être accepté / should be accepted"
            )
