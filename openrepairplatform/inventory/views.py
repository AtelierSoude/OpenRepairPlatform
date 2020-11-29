from dal import autocomplete
from django.urls import reverse, reverse_lazy
from django.db.models import Q

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    RedirectView,
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
from .forms import StuffForm
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
        context["add_organization_stuff"] = StuffForm
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



class StuffUserFormView(RedirectView):
    model = Stuff
    form_class = StuffForm
    http_methods = ["post"]

    def get(self, request, *args, **kwargs):
        self.object = kwargs["user_pk"]
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_redirect_url(self, *args, **kwargs):
        rq = self.request.POST
        user = CustomUser.objects.get(pk=self.object)
        if rq.get('create_device'):
            device = Device.objects.create(
                brand = Brand.objects.get(pk=rq.get('brand')),
                model = rq.get('model'),
                category = Category.objects.get(pk=rq.get('category')),
            )
        else:
            device = Device.objects.get(pk=rq.get('device'))
        stuff = Stuff.objects.create(
            member_owner = user,
            device = device,
            state = rq['state'],
            information = rq['information'],
        )
        if rq.get('create_folder'):
            if rq.get('ongoing'):
                ongoing_val = False
            else:
                ongoing_val = True
            folder = RepairFolder.objects.create(
                open_date = rq['repair_date'],
                stuff = stuff,
                ongoing = ongoing_val
            )
            intervention = Intervention.objects.create(      
                repair_date = rq['repair_date'],
                folder = folder,
                observation = Observation.objects.filter(pk=rq.get('observation')).first(),
                reasoning = Reasoning.objects.filter(pk=rq.get('reasoning')).first(),
                action = Action.objects.filter(pk=rq.get('action')).first(),
                status = Status.objects.filter(pk=rq.get('status')).first(),
            )
        return reverse("inventory:stuff_view", args=[stuff.pk])

class StuffUserCreateView(RedirectQueryParamView, StuffUserFormView, CreateView):
    success_message = "l'appareil a bien été créé"


class StuffOrganizationFormView(HasActivePermissionMixin, RedirectView):
    model = Stuff
    form_class = StuffForm
    http_methods = ["post"]

    def get(self, request, *args, **kwargs):
        self.object = self.organization
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_redirect_url(self, *args, **kwargs):
        rq = self.request.POST
        if rq.get('create_device'):
            device = Device.objects.create(
                brand = Brand.objects.get(pk=rq.get('brand')),
                model = rq.get('model'),
                category = Category.objects.get(pk=rq.get('category')),
            )
        else:
            device = Device.objects.get(pk=rq.get('device'))
        stuff = Stuff.objects.create(
            organization_owner = self.object,
            device = device,
            place = Place.objects.filter(pk=rq.get('place')).first(),
            state = rq['state'],
            information = rq['information'],
        )
        if rq.get('create_folder'):
            if rq.get('ongoing'):
                ongoing_val = False
            else:
                ongoing_val = True
            folder = RepairFolder.objects.create(
                open_date = rq['repair_date'],
                stuff = stuff,
                ongoing = ongoing_val
            )
            intervention = Intervention.objects.create(        
                folder = folder,
                repair_date = rq['repair_date'],
                observation = Observation.objects.filter(pk=rq.get('observation')).first(),
                reasoning = Reasoning.objects.filter(pk=rq.get('reasoning')).first(),
                action = Action.objects.filter(pk=rq.get('action')).first(),
                status = Status.objects.filter(pk=rq.get('status')).first(),
            )
        return reverse("organization_stock", args=[self.object.slug])

class StuffOrganizationCreateView(RedirectQueryParamView, StuffOrganizationFormView, CreateView):
    success_message = "l'appareil a bien été créé"


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