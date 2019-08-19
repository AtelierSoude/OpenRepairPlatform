from django.utils import timezone
from rest_framework.generics import ListAPIView

from ateliersoude.event.models import Event
from ateliersoude.location.models import Place
from ateliersoude.location.serializers import PlaceSerializer


class PlaceListAPIView(ListAPIView):
    serializer_class = PlaceSerializer
    queryset = Place.objects.filter()
    authentication_classes = []
