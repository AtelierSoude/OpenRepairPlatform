from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
)
from django.contrib import messages
from openrepairplatform.mixins import HasActivePermissionMixin, RedirectQueryParamView
from openrepairplatform.user.mixins import PermissionOrgaContextMixin
from django.urls import reverse, reverse_lazy

import django_tables2 as tables
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin

from .tables import StockTable
from .models import Stuff, Device
from .filters import StockFilter
from .forms import StuffForm, StuffUserForm, StuffOrganizationForm, StuffDeviceForm, StuffOwnerForm, StuffPlaceForm, StuffStateForm
from openrepairplatform.user.models import CustomUser, Organization

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions


class DeviceDetailView(DetailView):
    model = Device
    template_name = "inventory/device_detail.html"

class OrganizationStockView(
    HasActivePermissionMixin, 
    PermissionOrgaContextMixin, 
    ExportMixin, 
    tables.SingleTableMixin, 
    FilterView,
        ):
    model = Stuff
    template_name = "organization_stock.html"
    context_object_name = "stock"
    paginate_by = 50
    table_class = StockTable
    filterset_class = StockFilter
    dataset_kwargs = {"title": "Stock"}

    def get_queryset(self):
        self.object = self.organization
        return Stuff.objects.filter(organization_owner=self.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        context["stock_tab"] = 'active'
        context["add_organization_stuff"] = StuffOrganizationForm
        return context


class StuffDetailView(DetailView):
    model = Stuff
    template_name = "inventory/stuff_detail.html"
    pk_url_kwarg = "stuff_pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stuff_form"] = StuffForm
        return context


class StuffFormView(PermissionOrgaContextMixin):
    model = Stuff
    form_class = StuffForm
    http_methods = ["post"]

    def get(self, request, *args, **kwargs):
        self.object = self.organization
        return super().get(request, *args, **kwargs)

    def get_success_url(self, message):
        messages.success(self.request, message)
        return self.object.get_absolute_url()


class StuffCreateView(StuffFormView, CreateView):

    def get_success_url(self, *args, **kwargs):
        message = f"Vous avez créé {self.object} avec succès."
        return super().get_success_url(message)


class StuffUpdateView(StuffFormView, UpdateView):
    pk_url_kwarg = "stuff_pk"

    def get_success_url(self, *args, **kwargs):
        message = f"Vous avez modifié {self.object} avec succès."
        return super().get_success_url(message)


class StuffUserFormView(PermissionOrgaContextMixin):
    model = Stuff
    form_class = StuffUserForm
    http_methods = ["post"]

    def form_valid(self, form):
        form.instance.member_owner = CustomUser.objects.get(pk=self.kwargs["user_pk"])
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        stuff = self.object
        return reverse("inventory:stuff_view", args=[stuff.pk])


class StuffOrganizationFormView(PermissionOrgaContextMixin):
    model = Stuff
    form_class = StuffOrganizationForm
    http_methods = ["post"]

    def form_valid(self, form):
        form.instance.organization_owner = Organization.objects.get(slug=self.kwargs["orga_slug"])
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        orga_slug = self.kwargs["orga_slug"]
        return reverse("organization_stock", args=[orga_slug])


class StuffOrganizationCreateView(RedirectQueryParamView, StuffOrganizationFormView, CreateView):
    success_message = "l'appareil a bien été créé"
