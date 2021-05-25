from django.contrib import messages
from django.urls import reverse
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
)

from openrepairplatform.event.forms import ConditionForm
from openrepairplatform.event.models import Condition, Participation
from openrepairplatform.mixins import (
    RedirectQueryParamView,
    HasAdminPermissionMixin,
)


class ConditionFormView(HasAdminPermissionMixin):
    model = Condition
    form_class = ConditionForm
    template_name = "event/condition/form.html"

    def form_valid(self, form):
        form.instance.organization = self.organization
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        orga = self.object.organization
        return reverse("organization_page", args=[orga.slug])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["organization"] = self.organization
        return ctx


class ConditionCreateView(RedirectQueryParamView, ConditionFormView, CreateView):
    success_message = "La condition a bien été créée"


class ConditionEditView(RedirectQueryParamView, ConditionFormView, UpdateView):
    success_message = "La condition a bien été mise à jour"


class ConditionDeleteView(HasAdminPermissionMixin, DeleteView):
    model = Condition
    template_name = "event/condition/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "La condition a bien été supprimée")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


class ParticipationCreateView(CreateView):
    model = Participation
    http_method_names = ["post"]
    fields = ["amount", "payment", "event", "user"]

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        request.POST["user"] = kwargs["user_pk"]
        request.POST["event"] = kwargs["event_pk"]
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "La participation a bien été créée.")
        return self.request.META["HTTP_REFERER"]


class ParticipationUpdateView(UpdateView):
    model = Participation
    http_method_names = ["post"]
    fields = ["amount", "payment"]

    def get_success_url(self):
        messages.success(self.request, "La participation a bien été modifiée.")
        return self.request.META["HTTP_REFERER"]


class ParticipationDeleteView(DeleteView):
    model = Participation
    http_method_names = ["post"]

    def get_success_url(self):
        messages.success(self.request, "La participation a bien été supprimée")
        return self.request.META["HTTP_REFERER"]
