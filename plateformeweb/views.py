from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.views.generic import DetailView, ListView, FormView, CreateView, \
    UpdateView
from .models import *
from django.urls import reverse_lazy
from django.utils import timezone
from logging import getLogger

from django.forms import ModelForm, CharField, HiddenInput, ModelMultipleChoiceField, ModelChoiceField, CheckboxSelectMultiple, MultipleChoiceField
from datetimepicker.widgets import DateTimePicker
from rules.contrib.views import PermissionRequiredMixin

from django_markdown.fields import MarkdownFormField
from django_markdown.widgets import MarkdownWidget

from fm.views import AjaxCreateView, AjaxUpdateView

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
        context["list_type"] = "organization"
        return context


# --- edit ---

class OrganizationFormView():
    model = Organization
    fields = ["name", "description", "active"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields['description'] = CharField(widget=MarkdownWidget())
        return form


    def get_success_url(self):
        return reverse_lazy('organization_detail',
                            args=(self.object.pk, self.object.slug,))


class OrganizationCreateView(PermissionRequiredMixin, OrganizationFormView,
                             CreateView):
    permission_required = 'plateformeweb.create_organization'


class OrganizationEditView(PermissionRequiredMixin, OrganizationFormView,
                           AjaxUpdateView):
    permission_required = 'plateformeweb.edit_organization'
    queryset = Organization.objects


# --- Places ---

class PlaceView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PlaceListView(ListView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "place"
        return context


# --- edit ---

class PlaceFormView():

    model = Place
    fields = ["name", "description", "type", "address", "picture",
              "organization"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields['description'] = CharField(widget=MarkdownWidget())
        return form

    def get_success_url(self):
        return reverse_lazy('place_detail',
                            args=(self.object.pk, self.object.slug,))


class PlaceCreateView(PermissionRequiredMixin, PlaceFormView, CreateView):
    permission_required = 'plateformeweb.create_place'

    def validate_image(self, image):
        # Asserts image is smaller than 5MB
        if image:
            if image._size > 5 * 1024 * 1024:
                raise ValidationError("L'image est trop lourde (> 5Mo)")
            return image
        else:
            raise ValidationError("Erreur dans le téléversement du fichier")

    # set owner to current user on creation
    def form_valid(self, form):
        image = form.cleaned_data.get('picture', False)
        self.validate_image(image)
        obj = form.save(commit=False)
        obj.owner = self.request.user
        return super().form_valid(form)


class PlaceEditView(PermissionRequiredMixin, PlaceFormView, AjaxUpdateView):
    permission_required = 'plateformeweb.edit_place'
    queryset = Place.objects

    def validate_image(self, image):
        # Asserts image is smaller than 5MB
        if image:
            if image._size > 5 * 1024 * 1024:
                raise ValidationError("L'image est trop lourde (> 5Mo)")
            return image
        else:
            raise ValidationError("Erreur dans le téléversement du fichier")

    def form_valid(self, form):
        image = form.cleaned_data.get('picture', False)
        self.validate_image(image)
        return super().form_valid(form)


# --- Activity Types ---


class ActivityView(DetailView):
    model = Activity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ActivityListView(ListView):
    model = Activity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "activity"
        return context


# --- edit ---

class ActivityFormView():
    model = Activity
    fields = ["name", "description", "picture"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields['description'] = CharField(widget=MarkdownWidget())
        return form

    def get_success_url(self):
        return reverse_lazy('activity_detail',
                            args=(self.object.pk, self.object.slug,))


class ActivityCreateView(PermissionRequiredMixin, ActivityFormView, CreateView):
    permission_required = 'plateformeweb.create_activity'

        # set owner to current user on creation
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        return super().form_valid(form)


class ActivityEditView(PermissionRequiredMixin, ActivityFormView, AjaxUpdateView):
    permission_required = 'plateformeweb.edit_acivity'
    queryset = Activity.objects



# --- Events ---

class EventView(DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class EventListView(ListView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "event"
        return context


# --- edit ---

class EventFormView():
    model = Event
    fields = ["title", "type", "starts_at", "ends_at", "available_seats",
              "attendees", "presents", "organizers", "location", "publish_at", "published",
              "organization", "condition"]

    # date picker from
    #   https://xdsoft.net/jqplugins/datetimepicker/
    # installed as a django app by
    #   https://github.com/beda-software/django-datetimepicker
    # fix get_form:
    #   https://github.com/tomwalker/django_quiz/issues/71
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        for field in ("starts_at", "ends_at", "publish_at"):
            form.fields[field].widget = DateTimePicker(
                options={
                    'format': '%Y-%m-%d %H:%M',
                    # todo: i18n not working yet, needs to add a static JS
                    # file for translations ?
                    # see https://xdsoft.net/jqplugins/datetimepicker/
                    'lang': self.request.LANGUAGE_CODE[:2],
                    'step': 15,
                }
            )
        return form

    def get_success_url(self):
        return reverse_lazy('event_detail',
                            args=(self.object.pk, self.object.slug,))


class EventCreateView(PermissionRequiredMixin, EventFormView, CreateView):
    permission_required = 'plateformeweb.create_event'

    # set owner to current user on creation
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        return super().form_valid(form)


class EventEditView(PermissionRequiredMixin, EventFormView, AjaxUpdateView):
    permission_required = 'plateformeweb.edit_event'
    queryset = Event.objects


# --- booking form for current user ---


class BookingFormView():
    model = Event
    fields = []
    def get_form(self, form_class=None, **kwargs):

        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)

        user_id = self.request.user.id
        event_id = self.request.resolver_match.kwargs['pk']
        user = CustomUser.objects.get(pk=user_id)
        event = Event.objects.get(pk=event_id)
        attendees = event.attendees.all()

        if form.is_valid():
            # print("----------------")
            # print(event.title)
            # print("----------------")

            if user in attendees:
                print(attendees)
                print ("wazaa")
                event.attendees.remove(user)
            else:
                event.attendees.add(user)
        return form


    def get_success_url(self):
        return render(request, 'plateformeweb/event_list.html', message="c'est tout bon")


class BookingEditView(BookingFormView, AjaxUpdateView):
    template_name = 'plateformeweb/booking_form.html'
    queryset = Event.objects
