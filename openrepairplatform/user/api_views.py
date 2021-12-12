from openrepairplatform.user.models import CustomUser
from openrepairplatform.user.serializers import CustomUserSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import BasePermission


class OrganizationOwner(BasePermission):
    def has_permission(self, request, view):
        authenticated = request.user and request.user.is_authenticated
        manager_organizations = (
            request.user.active_organizations.all().union(
                request.user.volunteer_organizations.all(),
                request.user.admin_organizations.all()
            )
        )
        return bool(authenticated and manager_organizations)


class CustomUserAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [OrganizationOwner]
