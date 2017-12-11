from django.shortcuts import render
from django.views.generic import DetailView, ListView, FormView, CreateView, \
    UpdateView
from .models import Organization,Place,Event
from django.urls import reverse


def homepage(request):
    return render(request, 'plateformeweb/home.html')


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
        return reverse('organization_detail', args=(self.object.pk, self.object.slug,))


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
        return reverse('place_detail', args=(self.object.pk, self.object.slug,))


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
    fields = ["title", "type", "starts_at", "ends_at", "available_seats", "attendees", "organizers", "location"]
    def get_success_url(self):
        return reverse('event_detail', args=(self.object.pk, self.object.slug,))


class EventCreateView(EventFormView, CreateView):
    pass


class EventEditView(EventFormView, UpdateView):
    pass

