from datetime import date
from django.views.generic import (
    TemplateView,
    DetailView,
    ListView
)
from ateliersoude.user.mixins import PermissionOrgaContextMixin
from ateliersoude.mixins import HasActivePermissionMixin
from ateliersoude.user.models import (
    CustomUser,
    Organization
)
from ateliersoude.event.models import Event
from ateliersoude.utils import get_future_published_events
from ateliersoude.user.forms import CustomUserEmailForm, MoreInfoCustomUserForm
from ateliersoude.event.forms import EventSearchForm
from datetime import datetime
EVENTS_PER_PAGE = 6


class HomeView(TemplateView):
    template_name = "home.html"


class OrganizationPageView(
    HasActivePermissionMixin, PermissionOrgaContextMixin, DetailView
        ):
    model = Organization
    template_name = "organization_page.html"

    def get_object(self, *args, **kwargs):
        return Organization.objects.get(slug=self.kwargs["orga_slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = [
            (f"{user.email} ({user.first_name} {user.last_name})", user.email)
            for user in CustomUser.objects.all()
        ]
        all_events = self.object.events.all()
        context["events"] = list(
            get_future_published_events(all_events, self.object)
        )
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


class OrganizationMembersView(
    HasActivePermissionMixin, PermissionOrgaContextMixin, ListView
        ):
    model = CustomUser
    template_name = "organization_members.html"
    context_object_name = "members"
    object = Organization.objects.first()
    paginate_by = 20

    def get_queryset(self):
        return self.organization.members.all().order_by("last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        context["search_form"] = CustomUserEmailForm
        return context


class OrganizationControlsView(
    HasActivePermissionMixin, PermissionOrgaContextMixin, DetailView
        ):
    model = Organization
    template_name = "organization_controls.html"

    def get_object(self, *args, **kwargs):
        return self.model.objects.get(slug=self.organization.slug)


class OrganizationEventsView(HasActivePermissionMixin, ListView):
    model = Event
    template_name = "organization_events.html"
    context_object_name = "events"
    paginate_by = 10
    form_class = EventSearchForm

    def get_queryset(self):
        return self.model.objects.filter(
            organization=self.organization
        ).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        context["search_form"] = self.form_class
        context["today"] = datetime.date(datetime.now())
        return context


class OrganizationDetailsView(PermissionOrgaContextMixin, DetailView):
    model = Organization
    template_name = "organization_details.html"

    def get_object(self, *args, **kwargs):
        return Organization.objects.get(slug=self.kwargs["orga_slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.object
        return context
