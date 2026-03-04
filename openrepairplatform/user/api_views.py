import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from rest_framework.response import Response

from openrepairplatform.user.models import CustomUser, Organization, Membership, Fee, WebHook, SourceChoice
from openrepairplatform.user.serializers import CustomUserSerializer, HelloAssoWebhookSerializer, WebHookSerializer

logger = logging.getLogger(__name__)


class OrganizationOwner(BasePermission):
    def has_permission(self, request, view):
        authenticated = request.user and request.user.is_authenticated
        manager_organizations = (
            request.user.active_organizations.all().union(
                request.user.volunteer_organizations.all(),
                request.user.admin_organizations.all()
            )
        )
        return bool(authenticated and manager_organizations)


class CustomUserAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [OrganizationOwner]

class MembershipWebhookView(viewsets.ViewSet):
    """
    ViewSet pour traiter les webhooks entrants de HelloAsso ou TiBillet.
    Cette vue est volontairement verbeuse et explicite pour faciliter la maintenance.
    Elle n'utilise pas les classes génériques de DRF (sucres syntaxiques).

    ViewSet to process incoming webhooks from HelloAsso or TiBillet.
    This view is intentionally verbose and explicit for easier maintenance.
    It does not use DRF generic classes (syntactic sugar).
    """
    permission_classes = [AllowAny]

    # formTypes HelloAsso acceptés pour créer une adhésion
    # HelloAsso formTypes accepted to create a membership
    ACCEPTED_FORM_TYPES = {"Checkout", "Membership"}

    def create(self, request, webhook_pk=None):
        """
        Action pour traiter le payload du webhook et créer une adhésion.

        Action to process the webhook payload and create a membership.

        Exemple de test avec curl / Example test with curl:
        (Note: l'IP source doit correspondre à celle autorisée pour la source du webhook)
        (Note: the source IP must match the one allowed for this webhook's source)

        curl -X POST http://localhost:8005/api/user/webhook/<uuid>/ \
             -H "Content-Type: application/json" \
             -d '{"eventType": "Payment", "data": {"id": 15222, "amount": 1000, "date": "2026-02-10T11:50:48Z", "state": "Authorized", "order": {"formType": "Checkout"}, "payer": {"email": "test@example.com", "firstName": "John", "lastName": "Doe"}, "items": [{"amount": 1000, "type": "Membership", "name": "Adhésion"}]}, "metadata": {"id": 75698555}}'
        """
        logger.info(f"webhook membership {webhook_pk} : {request.data}")
        print(f"webhook membership {webhook_pk} : {request.data}")

        # 1. Récupération du WebHook par son UUID (hex) passé dans l'URL
        # 1. Retrieve the WebHook by its UUID (hex) passed in the URL
        webhook = get_object_or_404(WebHook, pk=webhook_pk)
        organization = webhook.organization

        # Log systématique de chaque appel webhook pour diagnostic
        # Systematic log of each webhook call for diagnostics
        logger.info(
            "Webhook %s reçu: body=%s",
            webhook_pk,
            request.data,
        )

        # 2. Vérification de l'IP source (Authenticité)
        # 2. Source IP verification (Authenticity)
        # On récupère l'IP du client, en tenant compte du proxy (nginx/uWSGI)
        # We retrieve the client IP, taking the proxy into account (nginx/uWSGI)
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            # Le premier élément est l'IP réelle du client
            # The first element is the real client IP
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.META.get("REMOTE_ADDR")

        # Comparaison de l'IP avec celle autorisée pour la source du webhook
        # Comparing IP with the one allowed for this webhook's source
        allowed_ip = WebHook.ALLOWED_IPS.get(webhook.source)
        if client_ip != allowed_ip:
            logger.warning(
                "Webhook %s: IP non autorisée - reçue=%s, attendue=%s (source=%s)",
                webhook_pk, client_ip, allowed_ip, webhook.source,
            )
            return Response(
                {"status": "error", "message": "Unauthorized IP address."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 3. Validation manuelle des données via le Serializer
        # 3. Manual data validation via the Serializer
        serializer = HelloAssoWebhookSerializer(data=request.data)

        # On vérifie si les données sont valides (lève une exception 400 en cas d'erreur)
        # Check if data is valid (raises a 400 exception on error)
        serializer.is_valid(raise_exception=True)

        # Extraction des données validées
        # Extraction of validated data
        event_type = serializer.validated_data["eventType"]
        validated_data = serializer.validated_data["data"]
        form_type = validated_data.get("order", {}).get("formType", "")

        # 4. Filtre sur eventType — seuls les paiements nous intéressent
        # 4. Filter on eventType — only payments are relevant
        if event_type != "Payment":
            logger.info("Webhook %s: eventType '%s' ignoré", webhook_pk, event_type)
            return Response(
                {"status": "ignored", "message": f"eventType '{event_type}' ignored."},
                status=status.HTTP_200_OK,
            )

        # 5. Filtre sur formType — seuls Checkout et Membership créent une adhésion
        # 5. Filter on formType — only Checkout and Membership create a membership
        if form_type and form_type not in self.ACCEPTED_FORM_TYPES:
            logger.info("Webhook %s: formType '%s' ignoré", webhook_pk, form_type)
            return Response(
                {"status": "ignored", "message": f"formType '{form_type}' ignored."},
                status=status.HTTP_200_OK,
            )

        # 6. Idempotence via l'ID de paiement HelloAsso (data.id)
        # 6. Idempotency via the HelloAsso payment ID (data.id)
        # On le fait avant de créer quoi que ce soit pour rester idempotent.
        # We do it before creating anything to remain idempotent.
        payment_id = str(validated_data["id"])
        if Fee.objects.filter(id_payment=payment_id).exists():
            logger.info("Webhook %s: paiement %s déjà traité", webhook_pk, payment_id)
            return Response(
                {"status": "ignored", "message": f"Payment {payment_id} already processed."},
                status=status.HTTP_200_OK,
            )

        # 7. Vérification de l'état du paiement (doit être "Authorized")
        # 7. Check payment state (must be "Authorized")
        if validated_data["state"] != "Authorized":
            logger.info("Webhook %s: état '%s' ignoré", webhook_pk, validated_data["state"])
            return Response(
                {"status": "ignored", "message": f"State '{validated_data['state']}' ignored."},
                status=status.HTTP_200_OK,
            )

        # 8. Vérification du type du paiement (doit être "Membership")
        # 8. Check payment's type (must be "Membership")
        items = validated_data["items"]

        # On vérifie si au moins un item est de type "Membership"
        # Check if any of the items is of type "Membership"
        if not any(item.get("type") == "Membership" for item in items):
            logger.info("Webhook %s: item type '%s' ignoré", webhook_pk, items[0].get("type"))
            return Response(
                {
                    "status": "ignored",
                    "message": f"Payment type '{items[0].get('type')}' ignored. Only 'Membership' is processed."
                },
                status=status.HTTP_200_OK
            )

        payer_data = validated_data["payer"]
        payment_date = validated_data["date"].date()
        # HelloAsso fournit les montants en centimes
        # HelloAsso provides amounts in cents
        amount = validated_data["amount"] // 100

        # 9. Récupération ou création de l'utilisateur (CustomUser)
        # 9. Retrieve or create the user (CustomUser)
        # On utilise l'email comme identifiant unique
        # We use email as a unique identifier
        user, user_created = CustomUser.objects.get_or_create(
            email=payer_data["email"],
            defaults={
                "first_name": payer_data.get("firstName", ""),
                "last_name": payer_data.get("lastName", ""),
            }
        )

        # 10. Récupération ou création de l'adhésion (Membership) pour cet utilisateur et cette organisation
        # 10. Retrieve or create the membership (Membership) for this user and organization
        membership, membership_created = Membership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={
                "first_payment": payment_date,
                "source": SourceChoice.SOURCE_HELLOASSO,
            }
        )

        # 11. Création de la cotisation (Fee) associée
        # 11. Creation of the associated fee (Fee)
        Fee.objects.create(
            organization=organization,
            membership=membership,
            amount=amount,
            date=payment_date,
            payment=Fee.PAYMENT_BANK,  # Paiement en ligne / Online payment
            id_payment=payment_id,
        )

        # 12. Retour d'une réponse explicite de succès (201 Created)
        # 12. Return an explicit success response (201 Created)
        logger.info(
            "Webhook %s: adhésion créée pour %s (%s) - formType=%s, montant=%s€",
            webhook_pk, user.email, organization.name, form_type, amount,
        )
        return Response(
            {
                "status": "success",
                "message": "Membership and fee processed successfully",
                "user_email": user.email,
                "organization": organization.name
            },
            status=status.HTTP_201_CREATED,
        )


class WebHookViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer les WebHooks d'une organisation.
    Permet de lister (list), créer (create) et supprimer (destroy) des webhooks de manière explicite.
    L'organisation est identifiée par son slug passé dans l'URL.
    Seuls les administrateurs de l'organisation peuvent effectuer ces actions.

    ViewSet to manage Organization WebHooks.
    Allows listing, creating, and deleting webhooks in an explicit manner.
    The organization is identified by its slug passed in the URL.
    Only organization administrators can perform these actions.
    """
    permission_classes = [IsAuthenticated]

    def get_organization(self, orga_slug):
        """
        Méthode utilitaire explicite pour récupérer l'organisation à partir du slug.
        Elle vérifie également si l'utilisateur actuel fait partie des administrateurs.

        Explicit utility method to retrieve the organization from the slug.
        It also checks if the current user is among the administrators.
        """
        # Récupération de l'objet Organization ou erreur 404
        # Retrieving the Organization object or 404 error
        organization = get_object_or_404(Organization, slug=orga_slug)

        # Vérification des droits : l'utilisateur doit être dans la liste des admins
        # Rights check: the user must be in the admins list
        if not organization.admins.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied(
                _("Accès refusé : Vous n'êtes pas administrateur de cette organisation.")
            )

        return organization

    def list(self, request, orga_slug=None):
        """
        Action pour lister les webhooks d'une organisation.
        Tout est explicite : récupération de l'orga, filtrage des webhooks, et sérialisation.

        Action to list webhooks of an organization.
        Everything is explicit: organization retrieval, webhook filtering, and serialization.
        """
        # On récupère l'organisation via le slug passé dans l'URL
        # Retrieving the organization via the slug passed in the URL
        organization = self.get_organization(orga_slug)

        # Récupération manuelle et explicite des webhooks
        # Manual and explicit retrieval of webhooks
        webhooks = WebHook.objects.filter(organization=organization)

        # Sérialisation manuelle
        # Manual serialization
        serializer = WebHookSerializer(webhooks, many=True)

        # Retour d'une réponse DRF avec les données sérialisées
        # Returning a DRF response with the serialized data
        return Response(serializer.data)

    def create(self, request, orga_slug=None):
        """
        Action pour créer un nouveau webhook pour une organisation.
        Gère explicitement la validation, la sauvegarde et le support HTMX.

        Action to create a new webhook for an organization.
        Explicitly handles validation, saving, and HTMX support.
        """
        # On récupère l'organisation via le slug
        # Retrieving the organization via the slug
        organization = self.get_organization(orga_slug)

        # Initialisation du serializer avec les données de la requête
        # Initializing the serializer with the request data
        serializer = WebHookSerializer(data=request.data)

        # Validation explicite (si invalide, une exception est levée ou on renvoie 400)
        # Explicit validation (if invalid, an exception is raised or we return 400)
        if serializer.is_valid():
            # Sauvegarde manuelle en injectant l'organisation récupérée
            # Manual save by injecting the retrieved organization
            webhook = serializer.save(organization=organization)

            # Détection explicite d'une requête HTMX
            # Explicit detection of an HTMX request
            if request.headers.get("HX-Request"):
                # Si c'est du HTMX, on renvoie un fragment HTML via 'render'
                # If it's HTMX, we return an HTML fragment via 'render'
                return render(
                    request,
                    "user/webhooks/item.html",
                    {"webhook": webhook, "organization": organization}
                )

            # Sinon on renvoie une réponse JSON standard avec un code 201
            # Otherwise return a standard JSON response with a 201 code
            return Response(
                WebHookSerializer(webhook).data,
                status=status.HTTP_201_CREATED
            )

        # Si le serializer n'est pas valide, on renvoie les erreurs
        # If the serializer is not valid, we return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, orga_slug=None, pk=None):
        """
        Action pour supprimer un webhook spécifique.
        Recherche explicite de l'objet et gestion de la réponse HTMX.

        Action to delete a specific webhook.
        Explicit object lookup and HTMX response management.
        """
        # On récupère d'abord l'organisation (pour vérification des droits)
        # First retrieve the organization (for rights check)
        organization = self.get_organization(orga_slug)

        # Récupération explicite du webhook appartenant à cette organisation
        # Explicit retrieval of the webhook belonging to this organization
        webhook = get_object_or_404(WebHook, pk=pk, organization=organization)

        # Suppression manuelle de l'objet
        # Manual deletion of the object
        webhook.delete()

        # Détection explicite d'une requête HTMX
        # Explicit detection of an HTMX request
        if request.headers.get("HX-Request"):
            # Pour HTMX, une réponse vide avec succès (200) suffit pour que
            # hx-swap="outerHTML" supprime l'élément.
            # For HTMX, a successful empty response (200) is enough for
            # hx-swap="outerHTML" to remove the element.
            return HttpResponse("", status=status.HTTP_200_OK)

        # Réponse DRF standard (204 No Content) pour les clients non-HTMX
        # Standard DRF response (204 No Content) for non-HTMX clients
        return Response(status=status.HTTP_204_NO_CONTENT)

