from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    RedirectView,
)
from datetime import timedelta
from openrepairplatform import utils
from openrepairplatform.event.models import Event, Participation
from openrepairplatform.event.templatetags.app_filters import tokenize
from openrepairplatform.event.views import add_present
from openrepairplatform.mixins import (
    HasAdminPermissionMixin,
    HasActivePermissionMixin,
    HasVolunteerPermissionMixin,
    RedirectQueryParamView,
)
from openrepairplatform.inventory.mixins import PermissionCreateUserStuffMixin
from openrepairplatform.user.models import CustomUser, Organization, Membership, Fee
from openrepairplatform.inventory.models import Stuff
from openrepairplatform.inventory.forms import StuffForm

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
            event = Event.objects.get(id=self.request.GET.get("event"))
            organizers = event.organizers.all()
            if self.object in organizers:
                messages.error(
                    self.request, "Vous existez déjà comme animateur de cet événement"
                )
                return redirect(
                    reverse(
                        "event:detail",
                        kwargs={
                            "pk": request.GET["event"],
                            "slug": event.slug,
                        },
                    )
                )
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        event_id = self.request.GET.get("event")
        redirect_url = self.request.GET.get("redirect")
        event = get_object_or_404(Event, pk=event_id)
        token = tokenize(self.object, event, "book")
        return (
            reverse("event:book", kwargs={"token": token}) + f"?redirect={redirect_url}"
        )


class OrganizerBookView(HasVolunteerPermissionMixin, RedirectView):
    model = Event
    form_class = CustomUserEmailForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        new_organizer = CustomUser.objects.filter(
            email=self.request.POST.get("email", "invalid email")
        ).first()
        event = self.model.objects.get(id=kwargs["pk"])
        if new_organizer and new_organizer in (
            self.organization.actives_or_more.all()
            .union(self.organization.volunteers.all())
            .difference(event.registered.all())
        ):
            if new_organizer in event.organizers.all():
                messages.error(
                    request,
                    str(new_organizer) + " est déjà animateur.trice de cet événement",
                )
            else:
                messages.success(
                    request,
                    str(new_organizer)
                    + " rajouté.e comme animateur.trice de cet événement",
                )
            event.organizers.add(new_organizer)
            event.save()
            return redirect(event.get_absolute_url())
        messages.error(self.request, "Impossible de rajouter cette personne")
        return redirect(event.get_absolute_url())


class PresentMoreInfoView(UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def form_valid(self, form):
        user = form.save()
        add_present(
            self.event,
            user,
            form.cleaned_data["amount_paid"],
            form.cleaned_data["payment"],
        )
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return (
            reverse("event:detail", args=[self.event.id, self.event.slug]) + "#manage"
        )

    def test_func(self):
        self.event = get_object_or_404(Event, pk=self.kwargs.get("event_pk"))
        return self.request.user in self.event.organization.actives_or_more


class PresentCreateUserView(HasActivePermissionMixin, RedirectView):
    model = Event
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def get_object(self, **kwargs):
        self.event = get_object_or_404(self.model, pk=kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        self.get_object(**kwargs)
        user = CustomUser.objects.filter(email=self.request.POST.get("email")).first()
        if user:
            form = MoreInfoCustomUserForm(self.request.POST, instance=user)
        else:
            form = MoreInfoCustomUserForm(self.request.POST)
        user = form.save()
        add_present(
            self.event,
            user,
            form.cleaned_data["amount_paid"],
            form.cleaned_data["payment"]
        )
        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse(
            "event:detail", args=[self.event.id, self.event.slug]
        ) + "#manage"


# in future : change or mix AddMemberToOrganization and UpdateMembre Views
class AddMemberToOrganization(HasActivePermissionMixin, RedirectView):
    model = Organization
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def get_redirect_url(self, *args, **kwargs):
        user = CustomUser.objects.filter(email=self.request.POST["email"]).first()
        url = reverse(
            "organization_members",
            kwargs={"orga_slug": self.organization.slug},
        )
        if user:
            form = MoreInfoCustomUserForm(self.request.POST, instance=user)
        else:
            form = MoreInfoCustomUserForm(self.request.POST)
        user = form.save()
        amount = form.cleaned_data["amount_paid"]
        date = form.cleaned_data["date"]
        if user in self.organization.members.all():
            fees = Fee.objects.filter(organization=self.organization, user=user)
            up_date_fees = fees.filter(date__gte=date)
            membership = Membership.objects.get(
                organization=self.organization, user=user
            )
            if amount != 0 or form.cleaned_data["first_fee"]:
                fee = Fee.objects.create(
                    amount=amount,
                    user=user,
                    organization=self.organization,
                    date=date,
                    payment=form.cleaned_data["payment"],
                )
                if (
                    form.cleaned_data["first_fee"]
                    or membership.first_payment < timezone.now() - timedelta(days=365)
                    or not fees
                ):
                    membership.first_payment = date
                    membership.amount = 0
                    membership.fee = fee
                    for fee in up_date_fees:
                        membership.amount += fee.amount
                elif date < membership.first_payment.date():
                    pass
                elif date > membership.first_payment.date():
                    membership.amount += amount
                membership.save()
            messages.success(self.request, f"Vous avez modifié {user} avec succes.")
        else:
            fee = Fee.objects.create(
                amount=amount,
                user=user,
                organization=self.organization,
                date=date,
                payment=form.cleaned_data["payment"],
            )
            Membership.objects.create(
                organization=self.organization,
                user=user,
                amount=amount,
                first_payment=date,
                fee=fee,
            )
            messages.success(self.request, f"Vous avez ajouté ou {user} avec succes.")
        return url


class UpdateMemberView(HasActivePermissionMixin, UpdateView):
    model = CustomUser
    form_class = MoreInfoCustomUserForm
    http_methods = ["post"]

    def form_invalid(self, form):
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))

    def form_valid(self, form):
        user = form.save()
        date = form.cleaned_data["date"]
        amount = form.cleaned_data["amount_paid"]
        fees = Fee.objects.filter(organization=self.organization, user=user)
        up_date_fees = fees.filter(date__gte=date)
        membership = Membership.objects.get(organization=self.organization, user=user)
        if amount != 0 or form.cleaned_data["first_fee"]:
            fee = Fee.objects.create(
                amount=amount,
                user=user,
                organization=self.organization,
                date=date,
                payment=form.cleaned_data["payment"],
            )
            if (
                form.cleaned_data["first_fee"]
                or membership.first_payment < timezone.now() - timedelta(days=365)
                or not fees
            ):
                membership.first_payment = date
                membership.amount = 0
                membership.fee = fee
                for fee in up_date_fees:
                    membership.amount += fee.amount
            else:
                membership.amount += amount
        membership.save()
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        messages.success(
            self.request, f"Vous avez mis à jour {self.object} avec succès."
        )
        return reverse(
            "organization_members",
            kwargs={"orga_slug": self.organization.slug},
        )


class UserDetailView(PermissionCreateUserStuffMixin, DetailView):
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

            for organization in organizations.all():
                if organization in custom_user.member_organizations.all():
                    return custom_user

            if custom_user in can_see_users:
                return custom_user

        raise Http404("Utilisateur introuvable")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context["object"]
        registered = list(user.registered_events.all())
        participations = list(Participation.objects.filter(user=user))
        context["fees"] = list(Fee.objects.filter(user=user))
        context["passed_participations"] = [
            (participation.event, participation.amount)
            for participation in participations
        ]
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
        context["passed_rendezvous"].sort(key=lambda evt: evt[0].date, reverse=True)
        context["future_rendezvous"].sort(key=lambda evt: evt[0].date)
        context["stock"] = Stuff.objects.filter(member_owner=self.get_object())
        context["add_member_stuff"] = StuffForm
        return context


class UserListView(ListView):
    model = CustomUser
    context_object_name = "users"
    template_name = "user/user_list.html"
    paginate_by = 9
    queryset = CustomUser.objects.filter(is_superuser=False, is_visible=True).order_by(
        "last_name"
    )


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization_menu"] = "active"
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization_menu"] = "active"
        return context


class OrganizationUpdateView(HasAdminPermissionMixin, UpdateView):
    template_name = "user/organization/organization_form.html"
    model = Organization
    form_class = OrganizationForm

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.success(self.request, "L'organisation a bien été mise à jour.")
        return res

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization_menu"] = "active"
        return context


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
        user = CustomUser.objects.filter(email=email).exclude(first_name="").first()
        redirect_url = reverse(
            "organization_page",
            kwargs={"orga_slug": self.organization.slug},
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


class AddVolunteerToOrganization(HasActivePermissionMixin, AddUserToOrganization):
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
            "organization_page",
            kwargs={"orga_slug": self.organization.slug},
        )


class FeeDeleteView(HasActivePermissionMixin, RedirectQueryParamView, DeleteView):
    model = Fee

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        fee = self.object
        membership = Membership.objects.get(
            user=fee.user, organization=fee.organization
        )
        fees = Fee.objects.filter(
            user=membership.user, organization=membership.organization
        )
        try:
            fee.participation.amount = 0
            fee.participation.save()
        except ObjectDoesNotExist:
            pass
        if fee.date >= membership.first_payment.date():
            membership.amount -= fee.amount
        try:
            has_membership = fee.membership is not None
            if has_membership:
                next_fee = fees.filter(date__gt=fee.date).last()
                if not next_fee:
                    prev_fee = fees.filter(date__lt=fee.date).first()
                    if prev_fee:
                        membership.amount = prev_fee.amount
                        membership.fee = prev_fee
                        membership.first_payment = prev_fee.date
                if next_fee:
                    membership.fee = next_fee
                    membership.first_payment = next_fee.date
        except ObjectDoesNotExist:
            pass
        fee.delete()
        if not fees:
            membership.delete()
        else:
            membership.save()
        messages.success(request, "La cotisation a bien été supprimée")
        return HttpResponseRedirect(
            reverse("user:user_detail", kwargs={"pk": membership.user.pk})
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
