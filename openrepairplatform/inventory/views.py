from dal import autocomplete
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from bootstrap_modal_forms.generic import (
  BSModalCreateView,
  BSModalUpdateView,
  BSModalReadView,
  BSModalDeleteView
)


from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    RedirectView,
    FormView,
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
from .models import Stuff, Device, Category, Observation, Status, Reasoning, Action, Brand, Intervention, RepairFolder
from openrepairplatform.location.models import Place
from .filters import StockFilter
from .forms import StuffForm, StuffEditForm, FolderForm
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
    paginate_by = 30
    table_class = StockTable
    filterset_class = StockFilter
    dataset_kwargs = {"title": "Stock"}

    def get_queryset(self):
        self.object = self.organization
        return Stuff.objects.filter(organization_owner=self.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        context["stuff_count"] = self.get_queryset().count()
        context["stock_tab"] = 'active'
        context["organization_menu"] = 'active'
        return context


class StuffDetailView(DetailView):
    model = Stuff
    template_name = "inventory/stuff_detail.html"
    pk_url_kwarg = "stuff_pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class FolderCreateView(BSModalCreateView):
    model = RepairFolder
    template_name = 'inventory/folder_create_form.html'
    form_class = FolderForm
    success_message = "Le dossier a bien été créé"

    def form_valid(self, form, *args, **kwargs): 
        stuff = Stuff.objects.get(pk=self.kwargs["pk"])
        form.instance.stuff = stuff
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        stuff = Stuff.objects.get(pk=self.kwargs["pk"])
        return stuff.get_absolute_url()

class StuffUpdateView(BSModalUpdateView):
    model = Stuff
    form_class = StuffEditForm
    success_message = "L'appareil a bien été modifié"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()

class StuffFormMixin(BSModalCreateView):
    model = Stuff
    form_class = StuffForm
    template_name = 'inventory/stuff_form.html'
    success_message = "L'appareil a bien été ajouté à l'inventaire"

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    #def post(self, request, *args, **kwargs):
    ### import pdb; pdb.set_trace()

class StuffUserFormView(StuffFormMixin, BSModalCreateView):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = CustomUser.objects.get(pk=self.kwargs["user_pk"])
        return kwargs

class StuffOrganizationFormView(StuffFormMixin, CreateView):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = Organization.objects.get(slug=self.kwargs["orga_slug"])
        return kwargs

    def get_success_url(self, *args, **kwargs):
        return reverse(
            "organization_stock",
            kwargs={"orga_slug": self.kwargs["orga_slug"]},
        )
        
#### views for autocompletion 


class DeviceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Device.objects.all()
        category_pk = self.forwarded.get('category', None)

        if category_pk:
            category = Category.objects.get(pk=category_pk)
            qs = Device.objects.filter(category=category) 
            childrens = category.get_children()
            descendants = category.get_descendants()
            if childrens:
                for children in childrens:
                    qsadd = Device.objects.filter(category=children)
                qs = qs.union(qsadd)    
                if descendants:
                    for descendant in descendants:
                        qsadd = Device.objects.filter(category=descendant)
                    qs = qs.union(qsadd)    

        if self.q:
            qs = qs.filter(slug__icontains=self.q)
        return qs

class CategoryAutocomplete(autocomplete.Select2QuerySetView):

    def get_result_label(self, item):
        if item.get_parent():
            return f"{item.get_parent()} > {item}"
        else: 
           return f"{item}"

    def get_queryset(self):
        qs = Category.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class BrandAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Brand.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def has_add_permission(self, request):
        return True

class ObservationAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Observation.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def has_add_permission(self, request):
        return True

class ActionAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Observation.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def has_add_permission(self, request):
        return True

class ReasoningAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Reasoning.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def has_add_permission(self, request):
        return True

class ActionAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Action.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def has_add_permission(self, request):
        return True

class StatusAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Status.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def has_add_permission(self, request):
        return True