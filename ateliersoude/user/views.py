from datetime import date
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    RedirectView,
)

from ateliersoude import utils
from ateliersoude.event.models import Event
from ateliersoude.event.templatetags.app_filters import tokenize
from ateliersoude.event.views import add_present
from ateliersoude.mixins import (
    HasAdminPermissionMixin,
    HasActivePermissionMixin,
    HasVolunteerPermissionMixin,
)
from ateliersoude.user.mixins import PermissionOrgaContextMixin
from ateliersoude.user.models import CustomUser, Organization, Membership
from ateliersoude.utils import get_future_published_events

from .forms import (
    UserUpdateForm,
    UserCreateForm,
    OrganizationForm,
    CustomUserEmailForm,
    MoreInfoCustomUserForm,
)

EVENTS_PER_PAGE = 6


class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = CustomUser
    template_name = "user/user_form.html"
    form_class = UserUpdateForm

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.success(self.request, "L'utilisateur a bien été mis à jour.")
        return res

    def test_func(self):
        return self.request.user == self.get_object()


class UserCreateView(CreateView):
    model = CustomUser
    template_name = "user/user_form.html"
    form_class = UserCreateForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.success(self.request, "L'utilisateur a bien été créé")
        return res


class UserCreateAndBookView(CreateView):
    model = CustomUser
    form_class = CustomUserEmailForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        self.object = CustomUser.objects.filter(
            email=self.request.POST.get("email", "invalid email")
        ).first()
        if self.object:
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        event_id = self.request.GET.get("event")
        redirect_url = self.request.GET.get("redirect")
        event = get_object_or_404(Event, pk=event_id)
        token = tokenize(self.object, event, "book")
        return (
            reverse("event:book", kwargs={"token": token})
            + f"?redirect={redirect_url}"
        )


class PresentMoreInfoView(UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def form_valid(self, form):
        user = form.save()
        add_present(self.event, user, form.cleaned_data["amount_paid"])
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return (
            reverse("event:detail", args=[self.event.id, self.event.slug])
            + "#manage"
        )

    def test_func(self):
        self.event = get_object_or_404(Event, pk=self.kwargs.get("event_pk"))
        return self.request.user in self.event.organization.actives_or_more


class PresentCreateUserView(HasActivePermissionMixin, RedirectView):
    model = Event
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def get_redirect_url(self, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs.get("pk"))
        user = CustomUser.objects.filter(
            email=self.request.POST["email"]
        ).first()
        if user:
            form = MoreInfoCustomUserForm(self.request.POST, instance=user)
        else:
            form = MoreInfoCustomUserForm(self.request.POST)
        user = form.save()
        add_present(event, user, form.cleaned_data["amount_paid"])
        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug]) + "#manage"


class AddMemberToOrganization(HasActivePermissionMixin, RedirectView):
    model = Organization
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def get_redirect_url(self, *args, **kwargs):
        user = CustomUser.objects.filter(
            email=self.request.POST["email"]
        ).first()
        url = reverse(
            "user:organization_detail",
            kwargs={
                "pk": self.organization.pk,
                "slug": self.organization.slug,
            },
        )
        if user in self.organization.members.all():
            messages.warning(self.request, "L'utilisateur est déjà membre.")
            return url
        if user:
            form = MoreInfoCustomUserForm(self.request.POST, instance=user)
        else:
            form = MoreInfoCustomUserForm(self.request.POST)
        user = form.save()
        paid = form.cleaned_data["amount_paid"]
        Membership.objects.create(
            organization=self.organization, user=user, amount=paid
        )
        messages.success(self.request, f"Vous avez ajouté {user} avec succes.")
        return url


class UpdateMemberView(HasActivePermissionMixin, UpdateView):
    model = CustomUser
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def form_valid(self, form):
        user = form.save()
        membership = Membership.objects.get(
            organization=self.organization, user=user
        )
        membership.amount += form.cleaned_data["amount_paid"]
        membership.save()
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        messages.success(
            self.request, f"Vous avez mis à jour {self.object} avec succes."
        )
        return reverse(
            "user:organization_detail",
            kwargs={
                "pk": self.organization.pk,
                "slug": self.organization.slug,
            },
        )


class UserDetailView(DetailView):
    model = CustomUser
    template_name = "user/user_detail.html"

    def get_object(self, queryset=None):
        custom_user = super().get_object(queryset=queryset)
        user = self.request.user

        if custom_user.is_visible:
            return custom_user

        if user.is_staff:
            return custom_user

        if user.is_authenticated:
            if user.pk == custom_user.pk:
                return custom_user

            organizations = user.active_organizations.all().union(
                user.volunteer_organizations.all(),
                user.admin_organizations.all(),
            )
            can_see_users = CustomUser.objects.filter(
                Q(registered_events__organization__in=list(organizations))
                | Q(presents_events__organization__in=list(organizations))
            )

            if custom_user in can_see_users:
                return custom_user

        raise Http404("Utilisateur introuvable")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context["object"]
        registered = list(user.registered_events.all())
        context["passed_rendezvous"] = (
            [(event, "present") for event in user.presents_events.all()]
            + [(event, "absent") for event in registered if event.has_ended]
            + [
                (event, "organizer")
                for event in user.organizers_events.all()
                if event.has_ended
            ]
        )
        context["future_rendezvous"] = [
            (event, "") for event in registered if not event.has_ended
        ] + [
            (event, "organizer")
            for event in user.organizers_events.all()
            if not event.has_ended
        ]
        context["passed_rendezvous"].sort(
            key=lambda evt: evt[0].date, reverse=True
        )
        context["future_rendezvous"].sort(key=lambda evt: evt[0].date)
        return context


class UserListView(ListView):
    model = CustomUser
    template_name = "user/user_list.html"
    queryset = CustomUser.objects.filter(is_superuser=False, is_visible=True)


class OrganizationDetailView(PermissionOrgaContextMixin, DetailView):
    model = Organization
    template_name = "user/organization/organization_detail.html"

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


class OrganizationEventsListView(HasVolunteerPermissionMixin, ListView):
    model = Event
    paginate_by = EVENTS_PER_PAGE
    template_name = "user/organization/organization_event_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = Organization.objects.get(pk=self.kwargs.get("orga_pk"))
        context["organization"] = organization
        return context

    def get_queryset(self):
        orga_pk = self.kwargs.get("orga_pk")
        organization = get_object_or_404(Organization, pk=orga_pk)
        return organization.events.order_by("date")


class OrganizationListView(ListView):
    model = Organization
    template_name = "user/organization/organization_list.html"


@method_decorator(staff_member_required, name="dispatch")
class OrganizationCreateView(CreateView):
    template_name = "user/organization/organization_form.html"
    model = Organization
    form_class = OrganizationForm

    def form_valid(self, form):
        res = super().form_valid(form)
        form.instance.admins.add(self.request.user)
        messages.success(self.request, "L'organisation a bien été créée")
        return res


class OrganizationUpdateView(HasAdminPermissionMixin, UpdateView):
    template_name = "user/organization/organization_form.html"
    model = Organization
    form_class = OrganizationForm

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.success(
            self.request, "L'organisation a bien été mise à jour."
        )
        return res


class OrganizationDeleteView(HasAdminPermissionMixin, DeleteView):
    template_name = "user/organization/confirmation_delete.html"
    model = Organization
    success_url = reverse_lazy("user:organization_list")

    def delete(self, request, *args, **kwargs):
        delete = super().delete(request, *args, **kwargs)
        messages.success(request, "L'organisation a bien été supprimé")
        return delete


class AddUserToOrganization(HasAdminPermissionMixin, RedirectView):
    model = Organization

    def get_redirect_url(self, *args, **kwargs):
        email = self.request.POST.get("email", "")
        user = (
            CustomUser.objects.filter(email=email)
            .exclude(first_name="")
            .first()
        )
        redirect_url = reverse(
            "user:organization_detail",
            kwargs={
                "pk": self.organization.pk,
                "slug": self.organization.slug,
            },
        )

        if not user:
            messages.error(
                self.request,
                "L'utilisateur avec l'email " f"'{email}' n'existe pas",
            )
            return redirect_url

        if user in self.organization.admins.all():
            messages.warning(
                self.request,
                "Action impossible: l'utilisateur fait déjà partie des admins "
                "de l'association",
            )
            return redirect_url

        self.add_user_to_orga(self.organization, user)
        messages.success(self.request, f"Bienvenue {user.first_name}!")
        return redirect_url


class AddAdminToOrganization(AddUserToOrganization):
    @staticmethod
    def add_user_to_orga(orga, user):
        orga.actives.remove(user)
        orga.volunteers.remove(user)
        orga.admins.add(user)


class AddActiveToOrganization(HasActivePermissionMixin, AddUserToOrganization):
    @staticmethod
    def add_user_to_orga(orga, user):
        orga.volunteers.remove(user)
        orga.actives.add(user)


class AddVolunteerToOrganization(
    HasActivePermissionMixin, AddUserToOrganization
):
    @staticmethod
    def add_user_to_orga(orga, user):
        orga.actives.remove(user)
        orga.volunteers.add(user)


class RemoveUserFromOrganization(HasAdminPermissionMixin, RedirectView):
    model = Organization

    def get_redirect_url(self, *args, **kwargs):
        user_pk = kwargs["user_pk"]
        user = get_object_or_404(CustomUser, pk=user_pk)
        self.remove_user_from_orga(self.organization, user)
        messages.success(
            self.request,
            f"L'utilisateur {user.first_name} " "a bien été retiré !",
        )

        return reverse(
            "user:organization_detail",
            kwargs={
                "pk": self.organization.pk,
                "slug": self.organization.slug,
            },
        )


class RemoveAdminFromOrganization(RemoveUserFromOrganization):
    @staticmethod
    def remove_user_from_orga(orga, user):
        orga.admins.remove(user)


class RemoveActiveFromOrganization(RemoveUserFromOrganization):
    @staticmethod
    def remove_user_from_orga(orga, user):
        orga.actives.remove(user)


class RemoveVolunteerFromOrganization(RemoveUserFromOrganization):
    @staticmethod
    def remove_user_from_orga(orga, user):
        orga.volunteers.remove(user)
