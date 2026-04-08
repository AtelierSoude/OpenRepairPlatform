from django.contrib import messages
from django.db.models import Count
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from openrepairplatform.event.forms import ActivityForm
from openrepairplatform.event.models import Activity
from openrepairplatform.mixins import (
    RedirectQueryParamView,
    HasAdminPermissionMixin,
)
from openrepairplatform.user.mixins import PermissionOrgaContextMixin
from openrepairplatform.mixins import LocationActivity


class ActivityView(PermissionOrgaContextMixin, DetailView):
    model = Activity
    template_name = "event/activity/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["activity_menu"] = "active"
        return context


class ActivityListView(LocationActivity, ListView):
    model = Activity
    template_name = "event/activity/page_list.html"

    def get_queryset(self):
        queryset = (
            Activity.objects.all()
            .annotate(category_count=Count("category"))
            .order_by("-category_count")
        )
        queryset = queryset.order_by("category__name")
        queryset = self.filter_queryset_location(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["activity_menu"] = "active"
        return context


class ActivityFormView(HasAdminPermissionMixin):
    model = Activity
    form_class = ActivityForm
    template_name = "event/activity/form.html"

    def form_valid(self, form):
        form.instance.organization = self.organization
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["activity_menu"] = "active"
        return context


class ActivityCreateView(RedirectQueryParamView, ActivityFormView, CreateView):
    success_message = "L'activité a bien été créée"


class ActivityEditView(RedirectQueryParamView, ActivityFormView, UpdateView):
    success_message = "L'activité a bien été mise à jour"


class ActivityDeleteView(HasAdminPermissionMixin, RedirectQueryParamView, DeleteView):
    model = Activity
    template_name = "event/activity/confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "L'activité a bien été supprimée")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse(
            "organization_controls",
            kwargs={"orga_slug": self.organization.slug},
        )