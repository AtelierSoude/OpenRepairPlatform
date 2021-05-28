from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core import signing
from django.http import HttpResponseRedirect
from django.urls import Resolver404, resolve
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView, RedirectView, DeleteView

from openrepairplatform.event.models import Event
from openrepairplatform.user.models import CustomUser, Organization, Membership, Fee
from openrepairplatform.user.forms import MoreInfoCustomUserForm


def is_valid_path(path: str) -> bool:
    if not isinstance(path, str):
        return False
    try:
        # this call throws if the redirect is not registered in urls.py
        resolve(path)
        return True
    except Resolver404:
        return False


def _load_token(token, salt):
    ret = signing.loads(token, salt=salt)
    event_id = ret["event_id"]
    user_id = ret["user_id"]
    return Event.objects.get(pk=event_id), CustomUser.objects.get(pk=user_id)


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


class CreateMembershipMixin(HasActivePermissionMixin, RedirectView):
    model = Organization
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        user = CustomUser.objects.filter(email=request.POST["email"]).first()
        form = MoreInfoCustomUserForm(request.POST, instance=user)
        user = form.save()
        amount = form.cleaned_data["amount_paid"]
        membership, exist = Membership.objects.get_or_create(
            organization=self.organization,
            user=user,
        )
        event_pk = self.kwargs.get('event_pk', None)
        event = Event.objects.filter(pk=event_pk).first() if event_pk else None
        if amount > 0:
            Fee.objects.create(
                user=user,
                event=event,
                organization=self.organization,
                membership=membership,
                amount=amount,
                payment=form.cleaned_data["payment"],
                date=form.cleaned_data["date"],
            )
        messages.success(request, f"Vous avez ajouté {user} avec succes.")
        return res

    def get_redirect_url(self, *args, **kwargs):
        return self.request.META["HTTP_REFERER"]


class UpdateMembershipMixin(HasActivePermissionMixin, UpdateView):
    model = CustomUser
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def form_invalid(self, form):
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))

    def form_valid(self, form):
        user = form.save()
        date = form.cleaned_data["date"]
        amount = form.cleaned_data["amount_paid"]
        membership = Membership.objects.get(organization=self.organization, user=user)
        event_pk = self.kwargs.get('event_pk', None)
        event = Event.objects.filter(pk=event_pk).first() if event_pk else None
        if amount > 0:
            Fee.objects.create(
                amount=amount,
                user=user,
                event=event,
                organization=self.organization,
                date=date,
                payment=form.cleaned_data["payment"],
                membership=membership
            )
        messages.success(
            self.request, f"Vous avez mis à jour {self.object} avec succès."
        )
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return self.request.META["HTTP_REFERER"]


class DeleteMembershipMixin(HasActivePermissionMixin, DeleteView):
    model = Membership
    http_methods = ["post"]

    def delete(self, request, *args, **kwargs):
        res = super().delete(request, *args, **kwargs)
        messages.success(request, "La cotisation a bien été supprimée")
        return res

    def get_success_url(self, *args, **kwargs):
        return self.request.META["HTTP_REFERER"]
