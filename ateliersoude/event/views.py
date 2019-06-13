import logging
from datetime import timedelta

from django.contrib import messages
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    RedirectView,
    FormView,
)

from ateliersoude import utils
from ateliersoude.event.forms import (
    EventForm,
    ActivityForm,
    ConditionForm,
    EventSearchForm,
    RecurrentEventForm,
)
from ateliersoude.event.models import Activity, Condition, Event, Participation
from ateliersoude.event.templatetags.app_filters import tokenize
from ateliersoude.mixins import (
    RedirectQueryParamView,
    HasAdminPermissionMixin,
    HasActivePermissionMixin,
)
from ateliersoude.user.mixins import PermissionOrgaContextMixin
from ateliersoude.user.forms import CustomUserEmailForm, MoreInfoCustomUserForm
from ateliersoude.user.models import CustomUser, Membership

logger = logging.getLogger(__name__)


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
        return reverse("user:organization_detail", args=[orga.pk, orga.slug])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["organization"] = self.organization
        return ctx


class ConditionCreateView(
    RedirectQueryParamView, ConditionFormView, CreateView
):
    success_message = "La Condition a bien été créée"


class ConditionEditView(RedirectQueryParamView, ConditionFormView, UpdateView):
    success_message = "La Condition a bien été mise à jour"


class ConditionDeleteView(HasAdminPermissionMixin, DeleteView):
    model = Condition
    template_name = "event/condition/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "La condition a bien été supprimée")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


class ActivityView(PermissionOrgaContextMixin, DetailView):
    model = Activity
    template_name = "event/activity/detail.html"


class ActivityListView(ListView):
    model = Activity
    template_name = "event/activity/list.html"


class ActivityFormView(HasAdminPermissionMixin):
    model = Activity
    form_class = ActivityForm
    template_name = "event/activity/form.html"

    def form_valid(self, form):
        form.instance.organization = self.organization
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ActivityCreateView(RedirectQueryParamView, ActivityFormView, CreateView):
    success_message = "L'activité a bien été créée"


class ActivityEditView(RedirectQueryParamView, ActivityFormView, UpdateView):
    success_message = "L'activité a bien été mise à jour"


class ActivityDeleteView(
    HasAdminPermissionMixin, RedirectQueryParamView, DeleteView
):
    model = Activity
    success_url = reverse_lazy("event:activity_list")
    template_name = "event/activity/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'activité a bien été supprimée")
        return super().delete(request, *args, **kwargs)


class EventView(PermissionOrgaContextMixin, DetailView):
    model = Event
    template_name = "event/event_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["users"] = [
            (f"{user.email} ({user.first_name} {user.last_name})",
             user.email)
            for user in CustomUser.objects.all()
        ]
        ctx["register_form"] = CustomUserEmailForm
        ctx["present_form"] = MoreInfoCustomUserForm
        ctx["total_fees"] = sum(
            [fee.amount for fee in self.get_object().participations.all()]
        )
        return ctx


class EventListView(ListView):
    model = Event
    template_name = "event/event_list.html"
    paginate_by = 18

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = EventSearchForm(self.request.GET)
        context["register_form"] = CustomUserEmailForm
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


class EventFormView(HasActivePermissionMixin):
    model = Event
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"orga": self.organization})
        return kwargs

    def form_valid(self, form):
        form.instance.organization = self.organization
        event = form.save()
        if not self.object:
            event.organizers.add(self.request.user)
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(event.get_absolute_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orga"] = self.organization
        return ctx


class EventEditView(RedirectQueryParamView, EventFormView, UpdateView):
    success_message = "L'évènement a bien été modifié"


class EventCreateView(RedirectQueryParamView, EventFormView, CreateView):
    success_message = "L'évènement a bien été créé"


class EventDeleteView(
    HasAdminPermissionMixin, RedirectQueryParamView, DeleteView
):
    model = Event
    success_url = reverse_lazy("event:list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'évènement a bien été supprimé")
        return super().delete(request, *args, **kwargs)


class RecurrentEventCreateView(HasActivePermissionMixin, FormView):
    form_class = RecurrentEventForm
    success_url = reverse_lazy("event:list")
    template_name = "event/recurrent_event_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"orga": self.organization})
        return kwargs

    def form_valid(self, form):
        res = super().form_valid(form)
        count = form.save()
        messages.success(
            self.request, f"Vous avez créé {count} événements récurrents"
        )
        return res

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orga"] = self.organization
        return ctx


def _load_token(token, salt):
    ret = signing.loads(token, salt=salt)
    event_id = ret["event_id"]
    user_id = ret["user_id"]
    return Event.objects.get(pk=event_id), CustomUser.objects.get(pk=user_id)


def add_present(event: Event, user: CustomUser, paid: int):
    event.registered.remove(user)
    Participation.objects.create(event=event, user=user, amount=paid)


class AbsentView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "absent")
        except Exception:
            logger.exception(f"Error loading token {token} during asbent")
            messages.error(
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        event.registered.add(user)
        participation = event.participations.filter(user=user).first()
        if participation and participation.saved:
            contribution = Membership.objects.filter(
                user=participation.user, organization=event.organization
            ).first()
            if contribution:
                contribution.amount -= participation.amount
                contribution.save()
        event.presents.remove(user)
        messages.success(self.request, f"{user} a été marqué comme absent !")

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug]) + "#manage"


class CancelReservationView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "cancel")
        except Exception:
            logger.exception(f"Error loading token {token} during unbook")
            messages.error(
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        event.registered.remove(user)

        event_url = reverse("event:detail", args=[event.id, event.slug])
        event_url = self.request.build_absolute_uri(event_url)

        if user.first_name == "":
            # This is a temporary user created only for this event, we can
            # delete it
            user.delete()
        else:
            book_token = tokenize(user, event, "book")
            book_url = reverse("event:book", args=[book_token])
            book_url = self.request.build_absolute_uri(book_url)

        msg_plain = render_to_string("event/mail/unbook.txt", context=locals())
        msg_html = render_to_string("event/mail/unbook.html", context=locals())

        date = event.date.strftime("%d %B")
        subject = (
            f"Confirmation d'annulation pour le "
            f"{date} à {event.location.name}"
        )

        send_mail(
            subject,
            msg_plain,
            "no-reply@atelier-soude.fr",
            [user.email],
            html_message=msg_html,
        )

        messages.success(
            self.request, "Vous n'êtes plus inscrit à cet évènement"
        )

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


class BookView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "book")
        except Exception:
            logger.exception(f"Error loading token {token} during book")
            messages.error(
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        next_url = self.request.GET.get("redirect")
        if not utils.is_valid_path(next_url):
            next_url = reverse("event:detail", args=[event.id, event.slug])

        if event.remaining_seats <= 0:
            messages.error(
                self.request,
                "Désolé, il n'y a plus de place "
                "disponibles pour cet évènement",
            )
            return next_url

        if user in event.presents.all().union(event.registered.all()):
            messages.success(
                self.request,
                "Vous êtes déjà inscrit à cet évènement, à bientôt !",
            )
            return next_url

        event.registered.add(user)

        unbook_token = tokenize(user, event, "cancel")
        cancel_url = reverse("event:cancel_reservation", args=[unbook_token])
        cancel_url = self.request.build_absolute_uri(cancel_url)
        register_url = reverse("password_reset")
        register_url = self.request.build_absolute_uri(register_url)

        event_url = reverse("event:detail", args=[event.id, event.slug])
        event_url = self.request.build_absolute_uri(event_url)

        msg_plain = render_to_string("event/mail/book.txt", context=locals())
        msg_html = render_to_string("event/mail/book.html", context=locals())

        date = event.date.strftime("%d %B")
        subject = f"Votre réservation du {date} à {event.location.name}"

        send_mail(
            subject,
            msg_plain,
            "no-reply@atelier-soude.fr",
            [user.email],
            html_message=msg_html,
        )

        messages.success(
            self.request, f"'{user}' bien inscrit à l'évènement !"
        )

        return next_url


class CloseEventView(HasActivePermissionMixin, RedirectView):
    http_method_names = ["post"]
    model = Event

    def get_redirect_url(self, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        nb_deleted, nb_new_members = 0, 0
        for temp_user in event.registered.filter(first_name=""):
            temp_user.delete()
            nb_deleted += 1
        for participation in event.participations.all():
            contribution, created = Membership.objects.get_or_create(
                user=participation.user, organization=event.organization
            )
            if participation.saved:
                amount = 0
            else:
                amount = participation.amount

            if contribution.first_payment < timezone.now() - timedelta(
                days=365
            ):
                contribution.first_payment = timezone.now()
                contribution.amount = amount
            else:
                contribution.amount += amount
            participation.saved = True
            participation.save()
            contribution.save()
            if created:
                nb_new_members += 1

        messages.success(
            self.request,
            f"{nb_deleted} visiteurs temporaires "
            f"supprimés, {nb_new_members} nouveaux membres !",
        )

        return reverse("event:detail", args=[event.id, event.slug])


class AddActiveEventView(HasActivePermissionMixin, RedirectView):
    http_method_names = ["post"]
    model = Event

    def get_redirect_url(self, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        event.organizers.add(self.request.user)
        messages.success(self.request, "Ajouté aux organisateurs !")

        return reverse("event:detail", args=[event.id, event.slug])


class RemoveActiveEventView(HasActivePermissionMixin, RedirectView):
    http_method_names = ["post"]
    model = Event

    def get_redirect_url(self, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        event.organizers.remove(self.request.user)
        messages.success(self.request, "Retiré des organisateurs !")

        return reverse("event:detail", args=[event.id, event.slug])
