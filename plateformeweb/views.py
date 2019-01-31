from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.views.generic import DetailView, ListView, FormView, CreateView, \
    UpdateView
from .models import *
from itsdangerous import URLSafeSerializer, BadData
from post_office import mail
from django.urls import reverse_lazy
from django.utils import timezone
from logging import getLogger
from django.template.loader import render_to_string

from django.forms import ModelForm, CharField, HiddenInput, ModelMultipleChoiceField, ModelChoiceField, CheckboxSelectMultiple, MultipleChoiceField
from datetimepicker.widgets import DateTimePicker
from rules.contrib.views import PermissionRequiredMixin

from django_markdown.fields import MarkdownFormField
from django_markdown.widgets import MarkdownWidget

from fm.views import AjaxUpdateView, AjaxCreateView, UpdateView

import datetime
from django import forms

from django.db.models.signals import post_save
from actstream import action
from actstream.actions import follow, unfollow

from actstream.models import actor_stream, following, followers

from django.core.mail import send_mail
from django.utils.timezone import now

logger = getLogger(__name__)



def homepage(request):
    if request.user.is_authenticated():
        return redirect('/activity/')
    else:
        return render (request, 'plateformeweb/home.html')

def send_notification(request, target_object, target_type):
    send_to = followers(target_object)
    
    if target_type == "actor":
        notification = target_object.actor_actions.all()[:1]
    elif target_type == "action_object":
        notification = target_object.action_object_actions.all()[:1]
    elif target_type == "target":
        notification = target_object.target_actions.all()[:1]

    params = {'notification': notification }

    msg_plain = render_to_string('mail/notification.html',
                                params)
    msg_html = render_to_string('mail/notification.html',
                                params)

    subject = "nouvelle notification"

    for user in send_to:
        mail.send(
            [user.email],
            'no-reply@atelier-soude.fr',
            subject=subject,
            message=msg_plain,
            html_message=msg_html
        )


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
    fields = ["name", "description","picture", "active"]

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


class OrganizationEditView(OrganizationFormView,
                           AjaxUpdateView):
    #permission_required = 'plateformeweb.edit_organization'
    queryset = Organization.objects


# -- Admin page to manage the organization contents -- 

def OrganizationManager(request, pk):
    organization = Organization.objects.get(pk=pk)
    organization_admins = organization.admins()
    if request.user in organization_admins:
        context = {"organization": organization}
    return render(request, 'plateformeweb/organization_manager.html', context)


# --- Places ---

class PlaceView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PlaceListView(ListView):
    model = Place

    def get_context_data(self, **kwargs):
        context = {}
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


class PlaceCreateView(PlaceFormView, AjaxCreateView):
    #permission_required = 'plateformeweb.create_place'

    def validate_image(self, image):
        # Asserts image is smaller than 5MB
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("L'image est trop lourde (> 5Mo)")
            return image
        else:
            raise ValidationError("Erreur dans le téléversement du fichier")

    # set owner to current user on creation
    def form_valid(self, form):
        image = form.cleaned_data.get('picture', False)
        self.validate_image(image)
        obj = form.save()
        obj.owner = self.request.user
        action.send(self.request.user, verb=' a créé ', action_object=obj)
        follow(self.request.user, obj, actor_only=False) 
        return super().form_valid(form)


class PlaceEditView(PlaceFormView, AjaxUpdateView):
    #permission_required = 'plateformeweb.edit_place'
    queryset = Place.objects

    def validate_image(self, image):
        # Asserts image is smaller than 5MB
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("L'image est trop lourde (> 5Mo)")
            return image
        else:
            raise ValidationError("Erreur dans le téléversement du fichier")

    def form_valid(self, form):
        image = form.cleaned_data.get('picture', False)
        self.validate_image(image)
        obj = form.save(commit=False)
        action.send(self.request.user, verb=' a modifié ', action_object=obj)
        follow(self.request.user, obj, actor_only=False) 
        return super().form_valid(form)


# --- Conditions ---

class ConditionView(DetailView):
    model = Condition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ConditionFormView():
    model = Condition
    fields = ["name", "resume", "description", "organization", "price"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        
        limited_choices = [["", '---------']]
        form.fields['description'] = CharField(widget=MarkdownWidget())
        user_orgs = OrganizationPerson.objects.filter(user=self.request.user,
                                                      role__gte=OrganizationPerson.ADMIN)
        for result in user_orgs:
            organization = result.organization
            limited_choices.append([organization.pk, organization.name])
        form.fields['organization'].choices = limited_choices
      
        return form

    def get_success_url(self):
        return reverse_lazy('activity_detail',
                            args=(self.object.pk, self.object.slug,))


class ConditionCreateView( ConditionFormView, AjaxCreateView):
    #permission_required = 'plateformeweb.create_activity'

        # set owner to current user on creation
    def form_valid(self, form):
        return super().form_valid(form)


class ConditionEditView(ConditionFormView, AjaxUpdateView):
   # permission_required = 'plateformeweb.edit_acivity'
    queryset = Activity.objects


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



class ActivityFormView():
    model = Activity
    fields = ["name", "description", "organization", "picture"]

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.fields['description'] = CharField(widget=MarkdownWidget())

        limited_choices = [["", '---------']]
        form.fields['description'] = CharField(widget=MarkdownWidget())
        user_orgs = OrganizationPerson.objects.filter(user=self.request.user,
                                                      role__gte=OrganizationPerson.ADMIN)
        for result in user_orgs:
            organization = result.organization
            limited_choices.append([organization.pk, organization.name])
        form.fields['organization'].choices = limited_choices

        return form

    def get_success_url(self):
        return reverse_lazy('activity_detail',
                            args=(self.object.pk, self.object.slug,))


class ActivityCreateView(ActivityFormView, AjaxCreateView):
    #permission_required = 'plateformeweb.create_activity'

        # set owner to current user on creation
    def form_valid(self, form):
        obj = form.save()
        obj.owner = self.request.user
        action.send(self.request.user, verb=' a créé ', action_object=obj)
        follow(self.request.user, obj, actor_only=False)  
        send_notification(self.request, target_object=obj, target_type="action_object")    
        return super().form_valid(form)


class ActivityEditView( ActivityFormView, AjaxUpdateView):
   # permission_required = 'plateformeweb.edit_acivity'
    queryset = Activity.objects

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        action.send(self.request.user, verb=' a modifié ', action_object=obj)
        send_notification(self.request, target_object=obj, target_type="action_object")    
        return super().form_valid(form)


# --- Events ---

def cancel_reservation(request, token):
    s = URLSafeSerializer('some_secret_key', salt='cancel_reservation')
    ret = s.loads(token)
    event_id = ret['event_id']
    user_id = ret['user_id']
    event = Event.objects.get(pk=event_id)
    user = CustomUser.objects.get(pk=user_id)
    context = {'event': event, 'user': user}
    attendees = event.attendees.all()
    if user in attendees:
        event.attendees.remove(user)
        event.available_seats += 1
        event.save()
        return render(request, 'mail/cancel_ok.html', context)
    else:
        return render(request, 'mail/cancel_failed.html', context)


class EventView(DetailView):
    model = Event

    def get(self, request, **kwargs):
        event = Event.objects.get(pk=kwargs['pk'])
        confirmed = event.presents.all()
        for person in confirmed:
            event.attendees.remove(person)

        return super().get(request)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = context['event']
        context['event_id'] = event.id
        orga = event.organization
        admins = orga.admins()
        orga_volunteers = orga.volunteers()

        volunteers = []
        for v in orga_volunteers:
            if v in event.attendees.all():
                volunteers.append(v)

        context['admin_or_volunteer'] = admins + volunteers
        context['volunteers'] = volunteers
        context['admins'] = admins
        return context


class EventListView(ListView):
    queryset = {}

    def get(self, request, **kwargs):
        return render(request, "plateformeweb/event_list.html", {})


    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     context["list_type"] = "event"
    #     return context


# --- edit ---

class EventEditView(PermissionRequiredMixin, AjaxUpdateView):
    permission_required = 'plateformeweb.edit_event'
    fields = ["title", "type", "starts_at", "ends_at", "available_seats",
              "organizers", "location", "publish_at", "published",
              "organization", "condition"]
    queryset = Event.objects


# --- booking form for current user ---


class BookingFormView():
    def send_booking_mail(self, user, event):
        user_id = user.id
        event_id = event.id

        serial = URLSafeSerializer('some_secret_key',
                                   salt='cancel_reservation')
        data = {'event_id': event_id, 'user_id': user_id}

        cancel_token = serial.dumps(data)
        cancel_url = reverse('cancel_reservation', args=[cancel_token])
        cancel_url = self.request.build_absolute_uri(cancel_url)

        event_url = reverse('event_detail', args=[event_id, event.slug])
        event_url = self.request.build_absolute_uri(event_url)

        params = {'cancel_url': cancel_url,
                  'event_url': event_url,
                  'event': event}

        msg_plain = render_to_string('mail/relance.html',
                                    params)
        msg_html = render_to_string('mail/relance.html',
                                    params)

        date = event.starts_at.date().strftime("%d %B")
        location = event.location.name
        subject = "Votre réservation pour le " + date + " à " + location

        mail.send(
            [user.email],
            'no-reply@atelier-soude.fr',
            subject=subject,
            message=msg_plain,
            html_message=msg_html
        )

class BookingEditView(BookingFormView, UpdateView):

    template_name = 'plateformeweb/booking_form.html'
    queryset = Event.objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = context['event'].id

        serial = URLSafeSerializer('some_secret_key',
                                   salt='book')

        data = {'event_id': event_id}
        context['booking_id'] = serial.dumps(data)
        return context



# --- mass event ---

class EventCreateView(CreateView):
   # permission_required = 'plateformeweb.create_event'
    template_name = 'plateformeweb/event_form.html'
    model = Event
    fields = ["type",  "available_seats",
              "organization", "location", "condition",
              "starts_at", "ends_at", "publish_at"]

    def date_substract(self, starts_at, countdown):
        #TODO: change this if haing a publish_date in the past is a problem
        return starts_at - datetime.timedelta(days=countdown)


    def post(self, request, *args, **kwargs):
        try:
            import simplejson as json
        except (ImportError,):
            import json

        json_data = request.POST['dates']
        starts_at = request.POST['starts_at']
        ends_at = request.POST['ends_at']
        publish_countdown = int(request.POST['publish_at'])
        date_timestamps = json.loads(json_data)

        event_type=Activity.objects.get(pk=request.POST['type'])
        organization=Organization.objects.get(pk=request.POST['organization'])
        available_seats=int(request.POST['available_seats'])
        location=Place.objects.get(pk=request.POST['location'])

        new_slug = str(event_type)
        new_slug += '-' + organization.slug
        new_slug += '-' + location.slug

        # today = timezone.now()

        for date in date_timestamps:
            starts_at = datetime.datetime.fromtimestamp(
                int(date + int(request.POST['starts_at'])))
            ends_at = datetime.datetime.fromtimestamp(
                int(date + int(request.POST['ends_at'])))
            publish_date = self.date_substract(starts_at, publish_countdown)

            e = Event.objects.create(
                organization=organization,
                slug=new_slug,
                owner=request.user,
                starts_at=starts_at,
                ends_at=ends_at,
                publish_at=publish_date,
                available_seats=available_seats,
                location=location,
                type=event_type,
            )

            e.organizers.add(CustomUser.objects.get(email=request.user.email))
            e.title = e.type.name
            e.save()
            action.send(self.request.user, verb=' a créé ', action_object=e, target=e.location)  
            follow(self.request.user, e, actor_only=False)  

        
        return HttpResponseRedirect(reverse("event_create"))

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        for field in ("starts_at", "ends_at", "publish_at"):
            form.fields[field].widget = forms.HiddenInput()

        limited_choices = [["", '---------']]
        user_orgs = OrganizationPerson.objects.filter(user=self.request.user,
                                                      role__gte=OrganizationPerson.ADMIN)

        for result in user_orgs:
            organization = result.organization
            limited_choices.append([organization.pk, organization.name])

        form.fields['organization'].choices = limited_choices
        # form.fields['organization'].queryset = user_orgs

        return form


    # set owner to current user on creation
    def form_valid(self, form):
        return super().form_valid(form)


class MassBookingCreateView(CreateView):
    template_name = 'plateformeweb/mass_event_book.html'
    model = Event
    fields = []

    def post(self, request, *args, **kwargs):
        try:
            import simplejson as json
        except (ImportError,):
            import json

        json_data = request.POST['dates']
        events_pk = json.loads(json_data)
        events_pk = list(map(int, events_pk))
        events = Event.objects.filter(pk__in=events_pk)
        #TODO: bulk insert somehow?
        for event in events:
            event.attendees.add(request.user)
        return HttpResponse("OK!")

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_success_url(self):
        return render(request, 'plateformeweb/event_list.html', message="c'est tout bon")
