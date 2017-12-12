from django.shortcuts import render
from django.views.generic import DetailView, ListView, FormView, CreateView, \
    UpdateView
from .models import *
from django.urls import reverse_lazy
from django.utils import timezone
from logging import getLogger
from datetimepicker.widgets import DateTimePicker

logger = getLogger(__name__)


def homepage(request):
    events = PublishedEvent.objects.filter(
        starts_at__gte=timezone.now()).order_by('starts_at')[:10]
    context = {"events": events}
    return render(request, 'plateformeweb/home.html', context)


# TODO move all this in separate apps?

class OrganizationView(DetailView):
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OrganizationListView(ListView):
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# --- edit ---

class OrganizationFormView():
    model = Organization
    fields = ["name", "active"]

    def get_success_url(self):
        return reverse_lazy('organization_detail',
                       args=(self.object.pk, self.object.slug,))


class OrganizationCreateView(OrganizationFormView, CreateView):
    pass


class OrganizationEditView(OrganizationFormView, UpdateView):
    pass


# ------

class PlaceView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PlaceListView(ListView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# --- edit ---

class PlaceFormView():
    model = Place
    fields = ["name", "description", "type", "address", "picture"]

    def get_success_url(self):
        return reverse_lazy('place_detail', args=(self.object.pk, self.object.slug,))


class PlaceCreateView(PlaceFormView, CreateView):
    pass


class PlaceEditView(PlaceFormView, UpdateView):
    pass


# ------

class EventView(DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class EventListView(ListView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# --- edit ---

class EventFormView():
    model = Event
    fields = ["title", "type", "starts_at", "ends_at", "available_seats",
              "attendees", "organizers", "location", "publish_at", "published"]

    # datepicker in create view:
    #   https://stackoverflow.com/questions/21405895/datepickerwidget-in-createview
    # fix get_form:
    #   https://github.com/tomwalker/django_quiz/issues/71
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        for field in ("starts_at", "ends_at", "publish_at"):
            form.fields[field].widget=DateTimePicker(
                options={
                    'format': '%Y-%m-%d %H:%M',
                    'lang': self.request.LANGUAGE_CODE[:2],
                    'step': 15,
                }
            )
        return form

    def get_success_url(self):
        return reverse_lazy('event_detail', args=(self.object.pk, self.object.slug,))


class EventCreateView(EventFormView, CreateView):
    pass


class EventEditView(EventFormView, UpdateView):
    queryset = Event.objects

