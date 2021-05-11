from openrepairplatform.user.models import (
    CustomUser,
)
from openrepairplatform.user.serializers import CustomUserSerializer
from rest_framework import viewsets


class CustomUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
