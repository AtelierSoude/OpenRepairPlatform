from dal import autocomplete
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.safestring import mark_safe

from django.views.generic import (
    TemplateView,
    DetailView,
    ListView,
    FormView,
)
import django_tables2 as tables
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin

from openrepairplatform.tables import FeeTable, MemberTable, EventTable
from openrepairplatform.filters import FeeFilter, MemberFilter, EventFilter

from openrepairplatform.user.mixins import PermissionOrgaContextMixin
from openrepairplatform.mixins import HasActivePermissionMixin
from openrepairplatform.user.models import (
    CustomUser,
    Organization,
    Fee
)
from openrepairplatform.event.models import Event, Activity, Place
from openrepairplatform.user.forms import (
    CustomUserEmailForm,
    CustomUserSearchForm,
    MoreInfoCustomUserForm,
)
from openrepairplatform.event.forms import (
    EventSearchForm
)
from django.db.models import Count
from datetime import datetime
EVENTS_PER_PAGE = 6

class HomeView(TemplateView, FormView):
    form_class = EventSearchForm
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = EventSearchForm(self.request.GET)
        context["event_count"] = Event.objects.all().count()
        context["user_count"] = CustomUser.objects.all().count()
        context["organization_count"] = Organization.objects.all().count()
        context["results_number"] = self.get_queryset().count()
        return context

    def get_queryset(self):
        queryset = Event.future_published_events()
        form = EventSearchForm(self.request.GET)
        if not form.is_valid():
            return queryset
        if form.cleaned_data["place"]:
            queryset = queryset.filter(location=form.cleaned_data["place"])
        if form.cleaned_data["organization"]:
            queryset = queryset.filter(
                organization=form.cleaned_data["organization"]
            )
        if form.cleaned_data["activity"]:
            queryset = queryset.filter(activity=form.cleaned_data["activity"])
        if form.cleaned_data["starts_before"]:
            queryset = queryset.filter(
                date__lte=form.cleaned_data["starts_before"]
            )
        if form.cleaned_data["starts_after"]:
            queryset = queryset.filter(
                date__gte=form.cleaned_data["starts_after"]
            )
        return queryset

class OrganizationPageView(PermissionOrgaContextMixin, DetailView):
    model = Organization
    template_name = "organization_page.html"

    def get_object(self, *args, **kwargs):
        self.organization = Organization.objects.get(
            slug=self.kwargs["orga_slug"]
        )
        return self.organization

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        activities = Activity.objects.filter(organization=self.organization).annotate(category_count=Count('category')
            ).order_by('-category_count')
        context ["activities_list"] = activities.order_by('category__name')
        context["future_event"] = Event.future_published_events().filter(
            organization=self.organization).order_by('date')
        context["page_tab"] = 'active'
        context["organization_menu"] = 'active'
        return context

class OrganizationEventsView(
    PermissionOrgaContextMixin,
    ExportMixin, 
    tables.SingleTableMixin, 
    FilterView,
        ):
    model = Organization
    template_name = "organization_events.html"
    context_object_name = "events"
    table_class = EventTable
    filterset_class = EventFilter
    paginate_by = 20
    dataset_kwargs = {"title": "Event"}
    form_class = EventSearchForm

    def get_queryset(self):
        orga_slug = self.kwargs.get("orga_slug")
        organization = get_object_or_404(Organization, slug=orga_slug)
        self.object = organization
        return organization.events.order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = Organization.objects.get(slug=self.kwargs.get("orga_slug"))
        context["events_tab"] = 'active'
        context["organization_menu"] = 'active'
        context["organization"] = organization
        context["search_form"] = self.form_class
        filtered_data = EventFilter(self.request.GET, queryset=self.get_queryset().all())
        context["total_events"] = filtered_data.qs.count()
        context["today"] = datetime.date(datetime.now())
        context["future_event"] = Event.future_published_events().filter(
            organization=organization).order_by('date')
        return context

class OrganizationGroupsView(PermissionOrgaContextMixin, DetailView):
    model = Organization
    template_name = "organization_groups.html"

    def get_object(self, *args, **kwargs):
        self.organization = Organization.objects.get(
            slug=self.kwargs["orga_slug"]
        )
        return self.organization

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
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
        context["groups_tab"] = 'active'
        context["organization_menu"] = 'active'
        context["future_event"] = Event.future_published_events().filter(
            organization=self.organization).order_by('date')
        return context

class OrganizationMembersView(
    HasActivePermissionMixin, 
    PermissionOrgaContextMixin, 
    ExportMixin, 
    tables.SingleTableMixin, 
    FilterView
        ):
    model = CustomUser
    template_name = "organization_members.html"
    context_object_name = "members"
    paginate_by = 20
    table_class = MemberTable
    filterset_class = MemberFilter
    paginate_by = 40
    dataset_kwargs = {"title": "Members"}

    def get_queryset(self):
        self.object = self.organization
        queryset = self.organization.members.all().order_by("last_name")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members_tab"] = 'active'
        context["organization_menu"] = 'active'
        context["organization"] = self.organization
        context["search_form"] = CustomUserSearchForm
        context["emails"] = [
            (f"{user.email} ({user.first_name} {user.last_name})", user.email)
            for user in CustomUser.objects.all()
        ]
        context["add_member_form"] = MoreInfoCustomUserForm
        context["future_event"] = Event.future_published_events().filter(
            organization=self.organization).order_by('date')
        return context

class OrganizationFeesView(
    HasActivePermissionMixin, 
    PermissionOrgaContextMixin, 
    ExportMixin, 
    tables.SingleTableMixin, 
    FilterView
        ):
    model = Fee
    template_name = "organization_fees.html"
    context_object_name = "fees"
    table_class = FeeTable
    filterset_class = FeeFilter
    paginate_by = 40
    dataset_kwargs = {"title": "Fees"}

    def get_queryset(self):
        self.object = self.organization
        return self.model.objects.filter(
            organization=self.organization
        ).order_by("-date").exclude(amount=0)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["accounting_tab"] = 'active'
        context["organization_menu"] = 'active'
        context["organization"] = self.organization
        filtered_data = FeeFilter(self.request.GET, queryset=self.get_queryset().all())
        context["total_fees"] = sum(
            [fee.amount for fee in filtered_data.qs]
        )
        context["future_event"] = Event.future_published_events().filter(
            organization=self.organization).order_by('date')
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
        context["organization_menu"] = 'active'
        context["future_event"] = Event.future_published_events().filter(
            organization=self.organization).order_by('date')
        return context


class OrganizationDetailsView(PermissionOrgaContextMixin, DetailView):
    model = Organization
    template_name = "organization_details.html"

    def get_object(self, *args, **kwargs):
        return Organization.objects.get(slug=self.kwargs["orga_slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.object
        context["organization_menu"] = 'active'
        return context

#### autocomplete ####

class ActiveOrgaAutocomplete(HasActivePermissionMixin, autocomplete.Select2QuerySetView):

    def get_queryset(self, *args, **kwargs):
        orga_slug = self.kwargs.get("orga_slug")
        organization = get_object_or_404(Organization, slug=orga_slug)

        if not self.request.user.is_authenticated:
            return CustomUser.objects.none()

        qs = organization.actives.all().union(
            organization.admins.all(), organization.volunteers.all()
            )

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        return qs

class CustomUserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CustomUser.objects.none()

        qs = CustomUser.objects.all()

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q) | Q(email__icontains=self.q))
        return qs

    def get_selected_result_label(self, item):
        return f"<span class='selected-user' id={item.pk}/>{item}</span>"

class PlaceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Place.objects.none()

        qs = Place.objects.all().order_by("name")

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(address__icontains=self.q))
        return qs

class ActivityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Activity.objects.none()

        future_events = Event.future_published_events()
        qs = Activity.objects.all().order_by("name")

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
