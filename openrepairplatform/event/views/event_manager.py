import json
from django.conf import settings
from django.contrib import messages
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    FormView,
)

from openrepairplatform.event.models import Event, Condition, Activity
from openrepairplatform.event.forms import (
    EventForm,
    EventSearchForm,
    RecurrentEventForm,
    ParticipationForm,
    InvitationForm,
)
from openrepairplatform.location.models import Place
from openrepairplatform.mail import event_send_mail
from openrepairplatform.mixins import (
    RedirectQueryParamView,
    HasAdminPermissionMixin,
    HasActivePermissionMixin,
    HasVolunteerPermissionMixin,
    LocationRedirectMixin,
)
from openrepairplatform.user.forms import CustomUserEmailForm, MoreInfoCustomUserForm
from openrepairplatform.user.mixins import PermissionOrgaContextMixin
from openrepairplatform.user.models import CustomUser


class EventViewMixin(PermissionOrgaContextMixin, DetailView):
    model = Event
    template_name = "event/event_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if not self.request.user.is_anonymous:
            ctx["user_is_member"] = self.request.user.memberships.filter(
                organization=self.object.organization
            ).first()
        ctx["register_form"] = CustomUserEmailForm
        ctx["event_menu"] = "active"
        # Display success booking informations and inventory
        if self.request.GET.get("success_booking"):
            user_pk = self.request.GET.get("user_pk")
            user = get_object_or_404(CustomUser, pk=user_pk)
            if user:
                ctx["user_success_booking"] = user
        return ctx


class EventView(EventViewMixin):
    template_name = "event/event_detail.html"


class EventAdminView(HasVolunteerPermissionMixin, EventViewMixin):
    template_name = "event/event_admin_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invitation_form"] = InvitationForm
        context["emails"] = [
            (f"{user.email} ({user.first_name} {user.last_name})", user.email)
            for user in CustomUser.objects.only("email", "first_name", "last_name")
        ]
        context["present_form"] = MoreInfoCustomUserForm
        context["total_fees"] = sum(
            [fee.amount for fee in self.get_object().fees.all()]
        )
        context["total_participations"] = sum(
            [
                participation.amount
                for participation in self.get_object().participations.all()
            ]
        )
        context["participation_form"] = ParticipationForm
        return context


class EventListView(LocationRedirectMixin, ListView):
    model = Event
    form_class = EventSearchForm
    context_object_name = "event_list"
    template_name = "event/event_list.html"
    paginate_by = 30
    future_published_events = None
    object_list = None

    def serializer_places(self, queryset):
        return [
            {
                "pk": event.location.pk,
                "latitude": event.location.latitude,
                "longitude": event.location.longitude,
                "absolute_url": event.location.get_absolute_url(),
                "name": event.location.name,
                "address": event.location.address,
                "future_events": event.location.future_published_events().count(),
            }
            for event in queryset
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = EventSearchForm()
        context["register_form"] = CustomUserEmailForm
        context["event_menu"] = "active"
        context["results_number"] = self.get_queryset().count()
        context["places"] = self.serializer_places(self.get_queryset())
        return context

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        if not self.object_list and self.future_published_events:
            addresses = "<br/>".join(
                {
                    f"- {event.location.zipcode}"
                    for event in self.future_published_events
                }
            )
            message = f"""
                <p>
                    <b>
                    Il n'y a pas d'événements dans la zone selectionnée.
                    Vous pouvez retrouver nos événements de réparation dans
                    les zones suivantes :
                    </b>
                </p>
                {addresses}
            """
            messages.info(request, message, extra_tags="safe")
            return HttpResponseRedirect(reverse("homepage"))
        return res

    def get_queryset(self):
        self.future_published_events = Event.future_published_events()
        queryset = self.filter_queryset_location(self.future_published_events)
        form = EventSearchForm(self.request.GET)
        if not form.is_valid():
            return queryset.select_related(
                "organization",
                "activity",
                "activity__category",
                "activity__organization",
                "location",
            ).prefetch_related(
                "conditions",
                "registered",
                "presents",
                "organizers",
                "stuffs",
                "organization__members",
                "organization__volunteers",
                "organization__actives",
                "organization__admins",
            )
        if form.cleaned_data["organization"]:
            queryset = queryset.filter(organization=form.cleaned_data["organization"])
        if form.cleaned_data["activity"]:
            queryset = queryset.filter(activity=form.cleaned_data["activity"])
        if form.cleaned_data["starts_before"]:
            queryset = queryset.filter(date__lte=form.cleaned_data["starts_before"])
        if form.cleaned_data["starts_after"]:
            queryset = queryset.filter(date__gte=form.cleaned_data["starts_after"])
        return queryset.select_related(
            "organization",
            "activity",
            "activity__category",
            "activity__organization",
            "location",
            "location__organization",
        ).prefetch_related(
            "conditions",
            "registered",
            "presents",
            "organizers",
            "stuffs",
            "organization__members",
            "organization__volunteers",
            "organization__actives",
            "organization__admins",
        )


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
        ctx["event_menu"] = "active"
        return ctx


class EventEditView(RedirectQueryParamView, EventFormView, UpdateView):
    success_message = "L'évènement a bien été modifié"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["json_event"] = serialize("json", [self.object])
        ctx["json_activities"] = serialize(
            "json", Activity.objects.all(), fields=["name", "description", "picture"]
        )
        ctx["json_locations"] = serialize(
            "json", Place.objects.all(), fields=["name", "description", "picture"]
        )
        ctx["json_conditions"] = serialize(
            "json",
            Condition.objects.filter(organization=self.object.organization),
            fields=["name", "description", "price"],
        )
        ctx["json_organizers"] = serialize(
            "json",
            self.object.organization.organizers,
            fields=["first_name", "last_name", "avatar_img"],
        )
        return ctx


class EventCreateView(RedirectQueryParamView, EventFormView, CreateView):
    success_message = "L'évènement a bien été créé"


class EventDeleteView(HasAdminPermissionMixin, RedirectQueryParamView, DeleteView):
    model = Event
    success_url = reverse_lazy("event:list")

    def send_mail(self, event, user):
        date = event.date.strftime("%d %B")
        subject = (
            f"IMPORTANT : Annulation événement du {date} : "
            f"{event.activity.name} à {event.location.name}"
        )
        event_send_mail(
            event,
            user,
            subject,
            "event/mail/event_delete.txt",
            "event/mail/event_delete.html",
            f"{event.organization} <{settings.DEFAULT_FROM_EMAIL}>",
            [user.email],
            request=self.request,
        )

    def delete(self, request, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        users = event.organizers.all().union(
            event.presents.all(), event.registered.all()
        )
        if users:
            for user in users:
                self.send_mail(event, user)

        messages.success(
            request, "L'évènement a bien été supprimé et les participants avertis"
        )
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
        messages.success(self.request, f"Vous avez créé {count} événements récurrents")
        return res

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orga"] = self.organization
        ctx["event_menu"] = "active"
        return ctx
