from rest_framework import serializers

from .models import Place


class PlaceSerializer(serializers.ModelSerializer):
    orga_url = serializers.SerializerMethodField()
    orga_name = serializers.SerializerMethodField()
    future_events = serializers.SerializerMethodField()

    def get_future_events(self, place):
        if place.future_published_events():
            return True

    def get_orga_url(self, place):
        if place.organization:
            return place.organization.get_absolute_url()

    def get_orga_name(self, place):
        if place.organization:
            return place.organization.name

    class Meta:
        model = Place
        fields = [
            "pk",
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
            "future_events",
        ]
