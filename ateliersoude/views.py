from datetime import date
from django.views.generic import (
    TemplateView,
    DetailView
)
from ateliersoude.user.mixins import PermissionOrgaContextMixin
from ateliersoude.user.models import (
    CustomUser,
    Organization
)
from ateliersoude.utils import get_future_published_events
from ateliersoude.user.forms import CustomUserEmailForm, MoreInfoCustomUserForm
EVENTS_PER_PAGE = 6


class HomeView(TemplateView):
    template_name = "home.html"


class OrganizationDetailView(PermissionOrgaContextMixin, DetailView):
    model = Organization
    template_name = "organization_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = [
            (f"{user.email} ({user.first_name} {user.last_name})", user.email)
            for user in CustomUser.objects.all()
        ]
        all_events = self.object.events.all()
        context["events"] = list(get_future_published_events(all_events))
        if context["is_volunteer"]:
            context["has_hidden_events"] = all_events.count() > 0
            past_events = all_events.filter(date__lt=date.today()).order_by(
                "date"
            )
            context["page"] = past_events.count() // EVENTS_PER_PAGE + 1
        context["register_form"] = CustomUserEmailForm
        context["add_admin_form"] = CustomUserEmailForm(auto_id="id_admin_%s")
        context["add_active_form"] = CustomUserEmailForm(
            auto_id="id_active_%s"
        )
        context["add_volunteer_form"] = CustomUserEmailForm(
            auto_id="id_volunteer_%s"
        )
        context["add_member_form"] = MoreInfoCustomUserForm
        return context
