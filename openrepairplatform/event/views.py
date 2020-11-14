import logging
from datetime import timedelta
from dal import autocomplete

from django.contrib import messages
from django.db.models import Count
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    RedirectView,
    FormView,
)

from openrepairplatform import utils
from openrepairplatform.event.forms import (
    EventForm,
    ActivityForm,
    ConditionForm,
    EventSearchForm,
    RecurrentEventForm,
)
from openrepairplatform.event.models import Activity, Condition, Event, Participation
from openrepairplatform.location.models import Place
from ateliersoude.inventory.forms import StuffForm
from openrepairplatform.user.models import CustomUser
from openrepairplatform.event.templatetags.app_filters import tokenize
from openrepairplatform.mixins import (
    RedirectQueryParamView,
    HasAdminPermissionMixin,
    HasActivePermissionMixin,
    HasVolunteerPermissionMixin,
)
from openrepairplatform.user.mixins import PermissionOrgaContextMixin
from openrepairplatform.user.forms import CustomUserEmailForm, MoreInfoCustomUserForm
from openrepairplatform.user.models import CustomUser, Membership, Fee, Organization

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
        return reverse("organization_page", args=[orga.slug])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["organization"] = self.organization
        return ctx


class ConditionCreateView(
    RedirectQueryParamView, ConditionFormView, CreateView
):
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


class ActivityView(PermissionOrgaContextMixin, DetailView):
    model = Activity
    template_name = "event/activity/detail.html"


class ActivityListView(ListView):
    model = Activity
    template_name = "event/activity/list.html"

    def get_queryset(self):
        queryset = Activity.objects.all().annotate(category_count=Count('category')).order_by('-category_count')
        queryset = queryset.order_by('category__name')
        return queryset


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
            (f"{user.email} ({user.first_name} {user.last_name})", user.email)
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
    form_class = EventSearchForm
    context_object_name = "event_list"
    template_name = "event/event_list.html"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = EventSearchForm(self.request.GET)
        context["register_form"] = CustomUserEmailForm
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
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        users = event.organizers.all().union(
                event.presents.all(),
                event.registered.all()
            )
        if users:
            for user in users: 
                msg_plain = render_to_string("event/mail/event_delete.txt", context=locals())
                msg_html = render_to_string("event/mail/event_delete.html", context=locals())
                date = event.date.strftime("%d %B")
                subject = f"IMPORTANT : Annulation événement du {date} : {event.activity.name} à {event.location.name}"
                send_mail(
                    subject,
                    msg_plain,
                    f"{event.organization}" '<no-reply@atelier-soude.fr>',
                    [user.email],
                    html_message=msg_html,
                )
        messages.success(request, "L'évènement a bien été supprimé et les participants avertis")
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


def add_present(event: Event, user: CustomUser, paid: int, payment: int):
    event.registered.remove(user)
    Participation.objects.create(event=event, user=user, amount=paid, payment=payment)


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
        fees = Fee.objects.filter(user=user, organization=event.organization)
        related_fee = participation.fee
        if participation and participation.saved and participation.amount !=0:
            contribution = Membership.objects.filter(
                user=participation.user, organization=event.organization
            ).first()
            if contribution:
                if related_fee == contribution.fee:
                    contribution.amount -= related_fee.amount
                    next_fee = fees.filter(date__gt=related_fee.date).last()
                    if not next_fee:
                        prev_fee = fees.filter(date__lt=related_fee.date).first()
                        if prev_fee:
                            contribution.amount = prev_fee.amount
                            contribution.fee = prev_fee
                            contribution.first_payment = prev_fee.date
                    if next_fee:
                        contribution.fee = next_fee
                        contribution.first_payment = next_fee.date
                elif event.date > contribution.first_payment.date():
                    contribution.amount -= related_fee.amount
                else: 
                    pass
                if related_fee:
                    related_fee.delete()
                if not fees:
                    contribution.delete()
                else:
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
            f"{event.organization}" '<no-reply@atelier-soude.fr>',
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
        is_authorized = False
        try:
            event, user = _load_token(token, "book")
        except Exception:
            logger.exception(f"Error loading token {token} during book")
            messages.error(
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        try:
            id_current_user = self.request.user.id
            current_user = CustomUser.objects.get(id=id_current_user)
            if current_user in (event.organization.actives.all().union(
                event.organization.volunteers.all(),
                event.organization.admins.all()
            )):
                is_authorized = True
        except Exception:
            pass

        next_url = self.request.GET.get("redirect")
        if not utils.is_valid_path(next_url):
            next_url = reverse("event:detail", args=[event.id, event.slug])

        if event.remaining_seats <= 0 and not is_authorized:
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

        conditions = event.conditions.all()
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
        subject = f"Votre réservation du {date} pour {event.activity.name} à {event.location.name}"

        send_mail(
            subject,
            msg_plain,
            f"{event.organization}" '<no-reply@atelier-soude.fr>',
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
        event_date = event.date
        nb_deleted, nb_new_members = 0, 0
        for temp_user in event.registered.filter(first_name=""):
            temp_user.delete()
            nb_deleted += 1
        for participation in event.participations.all():
            contribution, created = Membership.objects.get_or_create(
                user=participation.user, organization=event.organization
            )
            if not participation.saved and participation.amount != 0 or contribution.first_payment.date() < event_date - timedelta(days=365) :
                related_fee = Fee.objects.create(
                    amount=participation.amount,
                    user=participation.user,
                    organization=event.organization,
                    date=event_date,
                    payment=participation.payment
                )
                participation.fee = related_fee
                if contribution.fee is None or contribution.first_payment.date() < event_date - timedelta(days=365):
                    contribution.fee = related_fee
                    contribution.first_payment = related_fee.date
                    contribution.amount = related_fee.amount
                elif event_date < contribution.first_payment.date():
                    pass
                elif event_date > contribution.first_payment.date():
                    contribution.amount += related_fee.amount
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


class AddActiveEventView(HasVolunteerPermissionMixin, RedirectView):
    http_method_names = ["post"]
    model = Event

    def get_redirect_url(self, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        event.organizers.add(self.request.user)
        messages.success(self.request, "Ajouté aux animateurs !")

        return reverse("event:detail", args=[event.id, event.slug])


class RemoveActiveEventView(HasVolunteerPermissionMixin, RedirectView):
    http_method_names = ["post"]
    model = Event

    def get_redirect_url(self, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        event.organizers.remove(self.request.user)
        messages.success(self.request, "Retiré des animateurs !")

        return reverse("event:detail", args=[event.id, event.slug])

#### autocomplete views for event form ####

class ConditionOrgaAutocomplete(HasVolunteerPermissionMixin, autocomplete.Select2QuerySetView):

    def get_queryset(self, *args, **kwargs):
        orga_slug = self.kwargs.get("orga_slug")
        organization = get_object_or_404(Organization, slug=orga_slug)

        if not self.request.user.is_authenticated:
            return CustomUser.objects.none()

        qs = organization.conditions.all().order_by("name")

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

class FutureEventActivityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        future_events = Event.future_published_events()
        qs = Activity.objects.filter(
                events__in=future_events
            ).distinct().order_by("name")

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs

class FutureEventPlaceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        future_events = Event.future_published_events()
        qs = Place.objects.filter(
                events__in=future_events
            ).distinct().order_by("address")

        activity_pk = self.forwarded.get('activity', None)

        if activity_pk:
            activity = Activity.objects.get(pk=activity_pk)
            future_events = future_events.filter(activity=activity)
            qs = Place.objects.filter(
                events__in=future_events
            ).distinct().order_by("address")

        if self.q:
            qs = qs.filter(address__icontains=self.q)

        return qs