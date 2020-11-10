from django.shortcuts import render
from ateliersoude.user.models import (
    CustomUser,
)
from ateliersoude.user.serializers import CustomUserSerializer
from rest_framework import viewsets


class CustomUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer