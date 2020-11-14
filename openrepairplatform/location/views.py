from django.contrib import messages
from django.urls import reverse_lazy

from django.views.generic import (
    DetailView,
    TemplateView,
    DeleteView,
    CreateView,
    UpdateView,
)

from openrepairplatform.location.forms import PlaceForm
from openrepairplatform.location.models import Place
from openrepairplatform.user.mixins import PermissionOrgaContextMixin
from openrepairplatform.mixins import RedirectQueryParamView, HasAdminPermissionMixin, HasActivePermissionMixin


class PlaceView(PermissionOrgaContextMixin, DetailView):
    model = Place


class PlaceDeleteView(
    HasAdminPermissionMixin, RedirectQueryParamView, DeleteView
):
    model = Place
    success_url = reverse_lazy("location:list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Le lieu a bien été supprimé")
        return super().delete(request, *args, **kwargs)


class PlaceMapView(TemplateView):
    template_name = "location/place_list.html"


class PlaceFormView(HasAdminPermissionMixin):
    def form_valid(self, form):
        form.instance.organization = self.organization
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class PlaceCreateView(RedirectQueryParamView, PlaceFormView, CreateView):
    form_class = PlaceForm
    model = Place
    success_message = "Le lieu a bien été créé"


class PlaceEditView(RedirectQueryParamView, PlaceFormView, UpdateView):
    form_class = PlaceForm
    model = Place
    success_message = "Le lieu a bien été modifié"
