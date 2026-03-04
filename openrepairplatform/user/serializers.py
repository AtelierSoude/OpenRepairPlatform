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
