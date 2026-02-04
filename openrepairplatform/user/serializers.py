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
    Affiche l'UUID en hexadécimal et permet de renseigner la clé de signature.
    """
    class Meta:
        model = WebHook
        fields = ["uuid", "hex", "signature_public_key"]
        read_only_fields = ["uuid", "hex"]


class HelloAssoPayerSerializer(serializers.Serializer):
    email = serializers.EmailField()
    firstName = serializers.CharField(required=False, allow_blank=True)
    lastName = serializers.CharField(required=False, allow_blank=True)

class HelloAssoItemSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    name = serializers.CharField()

class HelloAssoDataSerializer(serializers.Serializer):
    payer = HelloAssoPayerSerializer()
    items = HelloAssoItemSerializer(many=True)
    date = serializers.DateTimeField()
    state = serializers.CharField()

class HelloAssoWebhookSerializer(serializers.Serializer):
    data = HelloAssoDataSerializer()
    eventType = serializers.CharField()
    metadata = serializers.DictField(required=True)

    def validate_metadata(self, value):
        if "id" not in value:
            raise serializers.ValidationError("The 'id' field is required in metadata.")
        return value
