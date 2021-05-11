from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import Resolver404, resolve
from django.shortcuts import get_object_or_404
from openrepairplatform.user.models import Organization


def is_valid_path(path: str) -> bool:
    if not isinstance(path, str):
        return False
    try:
        # this call throws if the redirect is not registered in urls.py
        resolve(path)
        return True
    except Resolver404:
        return False


class RedirectQueryParamView:
    def get_success_url(self):
        redirect = self.request.GET.get("redirect")
        default_redirect = super().get_success_url()
        if is_valid_path(redirect):
            return redirect
        else:
            return default_redirect


class HasOrganizationPermission(UserPassesTestMixin):
    organization = None

    def set_organization(self):
        orga_pk = self.kwargs.get("orga_pk")
        orga_slug = self.kwargs.get("orga_slug")
        if orga_slug:
            orga = get_object_or_404(Organization, slug=orga_slug)
        elif orga_pk:
            orga = get_object_or_404(Organization, pk=orga_pk)
        elif self.model == Organization:
            orga = get_object_or_404(Organization, pk=self.kwargs.get("pk"))
        else:
            orga = get_object_or_404(self.model, pk=self.kwargs.get("pk")).organization
        self.organization = orga

    def test_func(self):
        self.set_organization()
        return self.request.user in self.get_authorized_users()


class HasAdminPermissionMixin(HasOrganizationPermission):
    permission_denied_message = "Vous n'êtes pas administrateur de l'organisation."

    def get_authorized_users(self):
        return self.organization.admins.all()


class HasActivePermissionMixin(HasOrganizationPermission):
    permission_denied_message = "Vous n'êtes pas actif de l'organisation."

    def get_authorized_users(self):
        return self.organization.actives_or_more


class HasVolunteerPermissionMixin(HasOrganizationPermission):
    permission_denied_message = "Vous n'êtes pas volontaire de l'organisation."

    def get_authorized_users(self):
        return self.organization.actives_or_more.union(
            self.organization.volunteers.all()
        )
