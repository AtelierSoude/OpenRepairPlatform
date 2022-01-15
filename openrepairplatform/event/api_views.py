from django.contrib import messages
from rest_framework.generics import UpdateAPIView, CreateAPIView

from .serializers import EventUpdateSerializer, EventCreateSerializer
from .models import Event


class EventUpdateAPIView(UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventUpdateSerializer

    def update(self, request, *args, **kwargs):
        res = super().update(request, *args, **kwargs)
        if res.status_code == 200:
            messages.success(request, "L'événement a bien été modifié.")
        return res


class EventCreateAPIView(CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventCreateSerializer
