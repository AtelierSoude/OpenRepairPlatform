from rest_framework import serializers

from .models import Place


class PlaceSerializer(serializers.ModelSerializer):
    orga_url = serializers.SerializerMethodField()
    orga_name = serializers.SerializerMethodField()

    def get_orga_url(self, place):
        return place.organization.get_absolute_url()

    def get_orga_name(self, place):
        return place.organization.name

    class Meta:
        model = Place
        fields = [
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
        ]
