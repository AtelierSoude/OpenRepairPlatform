import hmac
import hashlib
import logging

from django.db import transaction
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
    """Réception des webhooks HelloAsso/TiBillet pour créer des adhésions."""
    permission_classes = [AllowAny]

    # formTypes HelloAsso acceptés pour créer une adhésion
    ACCEPTED_FORM_TYPES = {"Checkout", "Membership"}

    def create(self, request, webhook_pk=None):
        # 1. Récupération du WebHook par son UUID
        webhook = get_object_or_404(WebHook, pk=webhook_pk)
        organization = webhook.organization

        # 2. Vérification de la signature HMAC-SHA256
        received_signature = request.headers.get("x-ha-signature")
        secret_key = webhook.signature_public_key

        computed_signature = hmac.new(
            secret_key.encode("utf-8"),
            msg=request.body,
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not received_signature or not hmac.compare_digest(computed_signature, received_signature):
            logger.warning("Webhook %s: signature invalide depuis %s", webhook_pk, request.META.get("REMOTE_ADDR"))
            return Response(
                {"status": "error", "message": "Invalid signature."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 3. Log du payload brut pour monitoring
        logger.info("Webhook %s: payload reçu: %s", webhook_pk, request.data)

        # 4. Validation du payload HelloAsso
        serializer = HelloAssoWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_type = serializer.validated_data["eventType"]
        validated_data = serializer.validated_data["data"]
        form_type = validated_data.get("order", {}).get("formType", "")

        # 5. Filtre sur eventType — seuls les paiements nous intéressent
        if event_type != "Payment":
            logger.info("Webhook %s: eventType '%s' ignoré", webhook_pk, event_type)
            return Response(
                {"status": "ignored", "message": f"eventType '{event_type}' ignored."},
                status=status.HTTP_200_OK,
            )

        # 6. Filtre sur formType — seuls Checkout et Membership créent une adhésion
        if form_type and form_type not in self.ACCEPTED_FORM_TYPES:
            logger.info("Webhook %s: formType '%s' ignoré", webhook_pk, form_type)
            return Response(
                {"status": "ignored", "message": f"formType '{form_type}' ignored."},
                status=status.HTTP_200_OK,
            )

        # 7. Idempotence via l'ID de paiement HelloAsso (data.id)
        payment_id = str(validated_data["id"])
        if Fee.objects.filter(id_payment=payment_id).exists():
            logger.info("Webhook %s: paiement %s déjà traité", webhook_pk, payment_id)
            return Response(
                {"status": "ignored", "message": f"Payment {payment_id} already processed."},
                status=status.HTTP_200_OK,
            )

        # 8. Seuls les paiements "Authorized" sont traités
        if validated_data["state"] != "Authorized":
            logger.info("Webhook %s: état '%s' ignoré", webhook_pk, validated_data["state"])
            return Response(
                {"status": "ignored", "message": f"State '{validated_data['state']}' ignored."},
                status=status.HTTP_200_OK,
            )

        payer_data = validated_data["payer"]
        payment_date = validated_data["date"].date()
        # HelloAsso fournit les montants en centimes
        amount = validated_data["amount"] // 100

        # 9. Création atomique : utilisateur + adhésion + cotisation
        with transaction.atomic():
            user, _ = CustomUser.objects.get_or_create(
                email=payer_data["email"],
                defaults={
                    "first_name": payer_data.get("firstName", ""),
                    "last_name": payer_data.get("lastName", ""),
                },
            )

            membership, _ = Membership.objects.get_or_create(
                user=user,
                organization=organization,
                defaults={
                    "first_payment": payment_date,
                    "source": SourceChoice.SOURCE_HELLOASSO,
                },
            )

            Fee.objects.create(
                organization=organization,
                membership=membership,
                amount=amount,
                date=payment_date,
                payment=Fee.PAYMENT_BANK,
                id_payment=payment_id,
            )

        logger.info(
            "Webhook %s: adhésion créée pour %s (%s) - formType=%s, montant=%s€",
            webhook_pk, user.email, organization.name, form_type, amount,
        )
        return Response(
            {"status": "success", "user_email": user.email, "organization": organization.name},
            status=status.HTTP_201_CREATED,
        )


class WebHookViewSet(viewsets.ViewSet):
    """Gestion CRUD des WebHooks d'une organisation (admin uniquement)."""
    permission_classes = [IsAuthenticated]

    def get_organization(self, orga_slug):
        organization = get_object_or_404(Organization, slug=orga_slug)
        if not organization.admins.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied(
                _("Accès refusé : Vous n'êtes pas administrateur de cette organisation.")
            )
        return organization

    def list(self, request, orga_slug=None):
        organization = self.get_organization(orga_slug)
        webhooks = WebHook.objects.filter(organization=organization)
        serializer = WebHookSerializer(webhooks, many=True)
        return Response(serializer.data)

    def create(self, request, orga_slug=None):
        organization = self.get_organization(orga_slug)
        serializer = WebHookSerializer(data=request.data)
        if serializer.is_valid():
            webhook = serializer.save(organization=organization)
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "user/webhooks/item.html",
                    {"webhook": webhook, "organization": organization},
                )
            return Response(WebHookSerializer(webhook).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, orga_slug=None, pk=None):
        organization = self.get_organization(orga_slug)
        webhook = get_object_or_404(WebHook, pk=pk, organization=organization)
        webhook.delete()
        if request.headers.get("HX-Request"):
            return HttpResponse("", status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

