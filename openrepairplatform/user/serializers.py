from rest_framework import serializers

from openrepairplatform.user.models import (
    CustomUser,
    WebHook,
)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "street_address", "email"]


class WebHookSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle WebHook.
    Affiche l'UUID en hexadécimal et la source (HelloAsso ou TiBillet).

    Serializer for the WebHook model.
    Displays the UUID as hex and the source (HelloAsso or TiBillet).
    """
    class Meta:
        model = WebHook
        fields = ["uuid", "hex", "source"]
        read_only_fields = ["uuid", "hex"]


class HelloAssoPayerSerializer(serializers.Serializer):
    email = serializers.EmailField()
    firstName = serializers.CharField(required=False, allow_blank=True)
    lastName = serializers.CharField(required=False, allow_blank=True)

class HelloAssoItemSerializer(serializers.Serializer):
    # Le montant au niveau item n'est pas utilisé (seul le montant top-level compte)
    # Item-level amount is not used (only the top-level amount matters)
    amount = serializers.IntegerField(required=False, default=0)
    # Le nom de l'item n'est pas utilisé dans le traitement, on autorise le vide
    # Item name is not used in processing, we allow blank
    name = serializers.CharField(required=False, allow_blank=True, default="")
    # Le type peut être absent sur certains payloads (donations, etc.)
    # Type may be missing on some payloads (donations, etc.)
    type = serializers.CharField(required=False, default="")

class HelloAssoOrderSerializer(serializers.Serializer):
    formType = serializers.CharField(required=False, default="")

class HelloAssoDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order = HelloAssoOrderSerializer(required=False, default=dict)
    payer = HelloAssoPayerSerializer()
    # Les donations HelloAsso peuvent ne pas avoir d'items
    # HelloAsso donations may not have items
    items = HelloAssoItemSerializer(many=True, required=False, default=list)
    amount = serializers.IntegerField()
    date = serializers.DateTimeField()
    # Si l'état est absent, on utilise une valeur par défaut qui sera rejetée
    # proprement par le filtre "Authorized" dans la vue (pas d'erreur 400)
    # If state is missing, we use a default value that will be cleanly rejected
    # by the "Authorized" filter in the view (no 400 error)
    state = serializers.CharField(required=False, default="")

class HelloAssoWebhookSerializer(serializers.Serializer):
    data = HelloAssoDataSerializer()
    eventType = serializers.CharField()
    metadata = serializers.DictField(required=False, default=dict)


class TiBilletMembershipSerializer(serializers.Serializer):
    """
    Valide le payload webhook envoyé par TiBillet lors d'une adhésion.
    Le payload est plat (pas d'enveloppe eventType/data comme HelloAsso).

    Validates the webhook payload sent by TiBillet for a membership.
    The payload is flat (no eventType/data envelope like HelloAsso).
    """
    # Champs obligatoires pour le traitement / Required fields for processing
    object = serializers.CharField()
    uuid = serializers.CharField()
    email = serializers.EmailField()
    contribution_value = serializers.FloatField()
    last_contribution = serializers.DateTimeField()
    state = serializers.CharField()
    deadline = serializers.CharField(allow_null=True)

    # Champs optionnels utilisés si présents / Optional fields used if present
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")

    # Tous les autres champs du payload TiBillet — non utilisés par ORP
    # mais déclarés pour ne pas bloquer la validation DRF
    # All other TiBillet payload fields — not used by ORP
    # but declared so DRF validation doesn't reject them
    pk = serializers.CharField(required=False, allow_null=True)
    state_display = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    datetime = serializers.CharField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    pseudo = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    price_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    price_uuid = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    product_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    product_uuid = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    organisation = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    organisation_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user = serializers.IntegerField(required=False, allow_null=True)
    card_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_added = serializers.CharField(required=False, allow_null=True)
    last_action = serializers.CharField(required=False, allow_null=True)
    payment_method = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    payment_method_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    newsletter = serializers.BooleanField(required=False, default=False)
    postal_code = serializers.IntegerField(required=False, allow_null=True)
    birth_date = serializers.CharField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_valid = serializers.BooleanField(required=False, default=False)
    asset_fedow = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    stripe_id_subscription = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    last_stripe_invoice = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    member_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    product_img = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    option_generale = serializers.ListField(required=False, default=list)
    option_names = serializers.ListField(required=False, default=list)
    custom_form = serializers.JSONField(required=False, allow_null=True)
