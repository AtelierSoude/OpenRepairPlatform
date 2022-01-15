from django.contrib import messages
from rest_framework import status
from rest_framework.generics import UpdateAPIView, CreateAPIView
from rest_framework.response import Response

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        headers = self.get_success_headers(serializer.data)
        res = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        if res.status_code == 201:
            breakpoint()
            if request.data.get("recurrent_type", False):
                message = f"{obj} événements ont été créé."
            else:
                message = "L'événement a bien été créé."
            messages.success(request, message)
        return res
