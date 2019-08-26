from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView
)
from django.contrib import messages
from ateliersoude.mixins import HasActivePermissionMixin
from ateliersoude.user.mixins import PermissionOrgaContextMixin

from .models import Stuff
from .forms import StuffForm


class OrganizationStockView(
    HasActivePermissionMixin, PermissionOrgaContextMixin, ListView
        ):
    model = Stuff
    template_name = "organization_stock.html"
    context_object_name = "stock"
    paginate_by = 50

    def get_queryset(self):
        self.object = self.organization
        return Stuff.objects.filter(organization_owner=self.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        context["form"] = StuffForm
        return context


class StuffDetailView(DetailView):
    model = Stuff
    template_name = "inventory/stuff_detail.html"
    pk_url_kwarg = "stuff_pk"


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
