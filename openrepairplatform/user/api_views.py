from openrepairplatform.user.models import CustomUser
from openrepairplatform.user.serializers import CustomUserSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import BasePermission


class OrganizationOwner(BasePermission):
    def has_permission(self, request, view):
        authenticated = request.user and request.user.is_authenticated
        memberships = CustomUser.objects.get(pk=view.kwargs["pk"]).memberships.all()
        if authenticated:
            for membership in memberships:
                is_manager = (
                    request.user in membership.organization.admins.all() or
                    request.user in membership.organization.volunteers.all()
                )
                if is_manager:
                    return True
        return False


class CustomUserAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [OrganizationOwner]
