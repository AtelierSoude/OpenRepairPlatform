from django.contrib import messages
from django.urls import reverse, reverse_lazy

from django.views.generic import (
    DetailView,
    TemplateView,
    DeleteView,
    CreateView,
    UpdateView,
    ListView,
)

from openrepairplatform.location.forms import PlaceForm
from openrepairplatform.location.models import Place
from openrepairplatform.user.mixins import PermissionOrgaContextMixin
from openrepairplatform.mixins import (
    RedirectQueryParamView,
    HasAdminPermissionMixin,
)


class PlaceListView(ListView):
    model = Place


class PlaceView(PermissionOrgaContextMixin, DetailView):
    model = Place

    def get_queryset(self):
        # renvoie un 404 si le lieu n'existe pas
        return super().get_queryset().filter(organization__isnull=False)


class PlaceDeleteView(HasAdminPermissionMixin, RedirectQueryParamView, DeleteView):
    model = Place

    def form_valid(self, form):
        messages.success(self.request, "Le lieu a bien été supprimé")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "organization_controls",
            kwargs={"orga_slug": self.organization.slug},
        )

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
