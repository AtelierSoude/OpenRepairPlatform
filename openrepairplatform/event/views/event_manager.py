from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
    FormView,
)

from openrepairplatform.event.models import Event
from openrepairplatform.event.forms import (
    EventForm,
    EventSearchForm,
    RecurrentEventForm,
    ParticipationForm,
)
from openrepairplatform.mail import event_send_mail
from openrepairplatform.mixins import (
    RedirectQueryParamView,
    HasAdminPermissionMixin,
    HasActivePermissionMixin,
    HasVolunteerPermissionMixin,
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
            ).first
        ctx["users"] = [
            (f"{user.email} ({user.first_name} {user.last_name})", user.email)
            for user in CustomUser.objects.all()
        ]
        ctx["register_form"] = CustomUserEmailForm
        ctx["participation_form"] = ParticipationForm
        ctx["event_menu"] = "active"
        ctx["present_form"] = MoreInfoCustomUserForm
        ctx["total_fees"] = sum([fee.amount for fee in self.get_object().fees.all()])
        ctx["total_participations"] = sum(
            [
                participation.amount
                for participation in self.get_object().participations.all()
            ]
        )
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
        context["event_menu"] = "active"
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
            queryset = queryset.filter(organization=form.cleaned_data["organization"])
        if form.cleaned_data["activity"]:
            queryset = queryset.filter(activity=form.cleaned_data["activity"])
        if form.cleaned_data["starts_before"]:
            queryset = queryset.filter(date__lte=form.cleaned_data["starts_before"])
        if form.cleaned_data["starts_after"]:
            queryset = queryset.filter(date__gte=form.cleaned_data["starts_after"])
        return queryset.select_related(
            "organization", "activity", "location"
        ).prefetch_related(
            "conditions", "registered", "presents", "organizers", "stuffs"
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
