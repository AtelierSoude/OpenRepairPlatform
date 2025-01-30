import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core import signing
from django.http import HttpResponseRedirect
from django.urls import Resolver404, resolve, reverse
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
        form = self.form_class(data=request.POST, instance=user)
        if form.is_valid():
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


class LocationRedirectMixin:
    def get(self, request, *args, **kwargs):
        postcode = request.GET.get("postcode", False)
        if postcode and settings.LOCATION:
            request.session["postcode"] = postcode
            request.session["location"] = None
            point = requests.get(
                "https://api-adresse.data.gouv.fr/search/"
                f"?q={postcode}&type=municipality"
            )
            if point.json()['features']:
                request.session["location"] = (
                    point.json()['features'][0]['geometry']['coordinates']
                )

        if not request.session.get("location", False) and settings.LOCATION:
            if request.session.get("postcode", False):
                messages.info(request, "Vous devez renseigner un code postal valide.")
            else:
                messages.info(request, "Vous devez renseigner un code postal.")
            return HttpResponseRedirect(reverse("homepage"))
        else:
            return super().get(request, *args, **kwargs)

    def get_distance(self):
        if self.request.GET.get("distance", False):
            self.request.session["distance"] = int(self.request.GET["distance"])
        distance = (
            self.request.session.get("distance")
            if self.request.session.get("distance", False)
            else settings.KM_DISTANCE
        )
        return distance

    def filter_queryset_location(self, queryset):
        if not settings.LOCATION:
            return queryset
        location = Point(self.request.session["location"])
        return queryset.filter(
            location__location__dwithin=(
               location, D(km=self.get_distance())
            )
        )


class LocationOrganization(LocationRedirectMixin):
    def filter_queryset_location(self, queryset):
        if not settings.LOCATION:
            return queryset
        location = Point(self.request.session["location"])
        return queryset.filter(
            places__location__dwithin=(
               location, D(km=self.get_distance())
            )
        ).distinct()


class LocationActivity(LocationRedirectMixin):
    def filter_queryset_location(self, queryset):
        if not settings.LOCATION:
            return queryset
        location = Point(self.request.session["location"])
        return queryset.filter(
            organization__places__location__dwithin=(
               location, D(km=self.get_distance())
            )
        ).distinct()
