from rest_framework.generics import ListAPIView

from openrepairplatform.location.models import Place
from openrepairplatform.location.serializers import PlaceSerializer


class PlaceListAPIView(ListAPIView):
    serializer_class = PlaceSerializer
    queryset = Place.objects.filter()
    authentication_classes = []
