from django.contrib import messages
from django.db.models import Count
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


class ActivityView(PermissionOrgaContextMixin, DetailView):
    model = Activity
    template_name = "event/activity/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["activity_menu"] = "active"
        return context


class ActivityListView(ListView):
    model = Activity
    template_name = "event/activity/list.html"

    def get_queryset(self):
        queryset = (
            Activity.objects.all()
            .annotate(category_count=Count("category"))
            .order_by("-category_count")
        )
        queryset = queryset.order_by("category__name")
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
    success_url = reverse_lazy("event:activity_list")
    template_name = "event/activity/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'activité a bien été supprimée")
        return super().delete(request, *args, **kwargs)
