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
from ateliersoude.user.forms import (
    CustomUserEmailForm,
    MoreInfoCustomUserForm,
    CustomUserForm
)
from ateliersoude.event.forms import EventSearchForm
from datetime import datetime
EVENTS_PER_PAGE = 6


class HomeView(TemplateView):
    template_name = "home.html"


class OrganizationPageView(
    PermissionOrgaContextMixin, DetailView
        ):
    model = Organization
    template_name = "organization_page.html"

    def get_object(self, *args, **kwargs):
        self.organization = Organization.objects.get(
            slug=self.kwargs["orga_slug"]
        )
        return self.organization

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["event_list"] = Event.future_published_events().filter(
            organization=self.organization).order_by('date')[0:10]
        context["emails"] = [
            (f"{user.email} ({user.first_name} {user.last_name})", user.email)
            for user in CustomUser.objects.all()
        ]
        context["add_admin_form"] = CustomUserEmailForm(auto_id="id_admin_%s")
        context["add_active_form"] = CustomUserEmailForm(
            auto_id="id_active_%s"
        )
        context["add_volunteer_form"] = CustomUserEmailForm(
            auto_id="id_volunteer_%s"
        )
        context["add_member_form"] = MoreInfoCustomUserForm
        context["page_tab"] = 'active'
        return context


class OrganizationMembersView(
    HasActivePermissionMixin, PermissionOrgaContextMixin, ListView
        ):
    model = CustomUser
    template_name = "organization_members.html"
    context_object_name = "members"
    paginate_by = 20

    def get_queryset(self):
        self.object = self.organization
        queryset = self.organization.members.all().order_by("last_name")
        form = CustomUserForm(self.request.GET)
        if form.is_valid() and form.cleaned_data["main_field"]:
            queryset = queryset.filter(
                first_name=form.cleaned_data["main_field"].split()[0],
                last_name=form.cleaned_data["main_field"].split()[1]
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members_tab"] = 'active'
        context["organization"] = self.organization
        context["search_form"] = CustomUserForm
        context["users"] = [
            (f"{user.first_name} {user.last_name}")
            for user in self.get_queryset()
        ]
        context["add_member_form"] = MoreInfoCustomUserForm
        return context


class OrganizationEventsView(
    HasActivePermissionMixin, PermissionOrgaContextMixin, ListView
        ):
    model = Event
    template_name = "organization_events.html"
    context_object_name = "events"
    paginate_by = 10
    form_class = EventSearchForm

    def get_queryset(self):
        self.object = self.organization
        return self.model.objects.filter(
            organization=self.organization
        ).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events_tab"] = 'active'
        context["organization"] = self.organization
        context["search_form"] = self.form_class
        context["today"] = datetime.date(datetime.now())
        return context


class OrganizationControlsView(
    HasActivePermissionMixin, PermissionOrgaContextMixin, DetailView
        ):
    model = Organization
    template_name = "organization_controls.html"

    def get_object(self, *args, **kwargs):
        return self.model.objects.get(slug=self.organization.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["controls_tab"] = 'active'
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
