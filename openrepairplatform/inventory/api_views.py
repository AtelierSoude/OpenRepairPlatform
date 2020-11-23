from django.shortcuts import render
from openrepairplatform.inventory.models import (
    Stuff, RepairFolder, Intervention, Device
)
from openrepairplatform.inventory.serializers import StuffSerializer, DeviceSerializer, InterventionSerializer, RepairFolderSerializer
from rest_framework import viewsets

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class StuffViewSet(viewsets.ModelViewSet):
    queryset = Stuff.objects.all()
    serializer_class = StuffSerializer

class RepairFolderViewSet(viewsets.ModelViewSet):
    serializer_class = RepairFolderSerializer
    queryset = RepairFolder.objects.all()

    def get_queryset(self):
        stuff_pk = self.kwargs['stuff_pk']
        get_stuff = Stuff.objects.get(pk=stuff_pk)
        self.queryset = RepairFolder.objects.filter(stuff=get_stuff)
        return self.queryset

class InterventionViewSet(viewsets.ModelViewSet):
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer