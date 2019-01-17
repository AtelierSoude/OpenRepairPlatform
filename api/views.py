from itsdangerous import URLSafeSerializer, BadData
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from users.models import CustomUser
from django.db.models import Q
from functools import reduce
from operator import __or__ as OR

from time import strftime
import locale
from plateformeweb.models import Event, Organization, OrganizationPerson, Place
from urllib.parse import parse_qs
from django.utils import timezone

from django.db.models.signals import post_save
from actstream import action

def delete_event(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        request_body = request.body.decode("utf-8")
        post_data = parse_qs(request_body)

        event_id = post_data['event_id'][0]
        event = Event.objects.get(pk=event_id)
        person = CustomUser.objects.get(email=request.user)
        if person in event.organizers.all():
            event.delete()
            return JsonResponse({'status': "OK"})

        return JsonResponse({'status': -1})



def set_present(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        serial = URLSafeSerializer('some_secret_key',
                                    salt='presence')

        data = serial.loads(request.POST['idents'])
        print(data)
        event_id = data['event_id']
        user_id = data['user_id']

        person = CustomUser.objects.get(pk=user_id)
        event = Event.objects.get(pk=event_id)
        event.attendees.remove(person)
        event.presents.add(person)

        return JsonResponse({'status': "OK", 'user_id': user_id})

def set_absent(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        serial = URLSafeSerializer('some_secret_key',
                                    salt='presence')

        data = serial.loads(request.POST['idents'])
        print(data)
        event_id = data['event_id']
        user_id = data['user_id']

        person = CustomUser.objects.get(pk=user_id)
        event = Event.objects.get(pk=event_id)
        event.presents.remove(person)
        event.attendees.add(person)

        return JsonResponse({'status': "OK", 'user_id': user_id})

def get_organizations(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        person = CustomUser.objects.get(email=request.user)
        organizations = OrganizationPerson.objects.filter(user=request.user)
        volunteer_of = {}
        for person in organizations:
            if person.role >= OrganizationPerson.VOLUNTEER:
                volunteer_of[person.organization.pk] = person.organization.name

        return JsonResponse({'status': "OK", "organizations": volunteer_of})

def get_all_places(request):
    if request.method != 'GET':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        places = {}
        places_qs = Place.objects.all()
        for place in places_qs:
            place_slug = place.slug
            place_pk = place.pk
            organization = place.organization
            organization_detail_url = reverse('organization_detail',
                                              args=[organization.pk,
                                                    organization.slug])

            place_detail_url = reverse('place_detail',
                                       args=[place_pk,
                                             place_slug])

            longitude = place.address.longitude
            latitude = place.address.latitude

            places[place_pk] = {
                'pk': place_pk,
                'name': place.name,
                'place_detail_url': place_detail_url,
                "address": place.address.formatted,
                'type': place.type.name,
                'organization': place.organization.name,
                'organization_url': organization_detail_url,
                'latitude': latitude,
                'longitude': longitude,
                'picture': place.picture.url,
                'description': place.description[:250],
                }

        return JsonResponse({'status': "OK", "places": places})

def get_places_for_organization(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        places = {}
        organization_pk = request.POST['organization_id']
        organization = Organization.objects.get(pk=organization_pk)
        places_qs = Place.objects.filter(organization=organization)
        for place in places_qs:
            places[place.pk] = str(place)

        return JsonResponse({'status': "OK", "places": places})

def get_dates(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        events = {}
        request_body = request.body.decode("utf-8")
        post_data = parse_qs(request_body)
        organization_pk = int(post_data['organization_pk'][0])
        today = timezone.now()

        target_organization = Organization.objects.get(pk=organization_pk)
        all_future_events = Event.objects.filter(organization=target_organization, starts_at__gte=today)

        for event in all_future_events:
            events[event.pk] = {'title': event.title,
                                'formatted_date': event.date_interval_format(),
                                'timestamp': event.starts_at.timestamp()}

        return JsonResponse({'status': "OK", "dates": events})


def list_events_in_context(request, context_pk=None, context_type=None, context_user=None, context_place=None, context_org=None ):
    if request.method != 'GET':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        events = []
        organizations = {}
        places = {}
        activitys = {}
        today = timezone.now()

        if context_place:
            this_place = Place.objects.get(pk=context_pk)
            all_future_events = Event.objects.filter(
                location=this_place, 
                starts_at__gte=today, 
                published=True).order_by('starts_at')
        
        elif context_org:
            this_organization = Organization.objects.get(pk=context_pk)
            all_future_events = Event.objects.filter(
                organization=this_organization, 
                starts_at__gte=today, 
                published=True).order_by('starts_at')
        
        elif context_user:
            lst = [Q(attendees__pk=context_pk) , Q(presents__pk=context_pk) , Q(organizers__pk=context_pk)]
            all_future_events = Event.objects.filter(reduce(OR, lst)).filter(
                starts_at__gte=today, 
                published=True).order_by('starts_at')

        else:
            all_future_events = Event.objects.filter(
                starts_at__gte=today, 
                published=True).order_by('starts_at')


        locale.setlocale(locale.LC_ALL, 'fr_FR')

        for event in all_future_events:
            event_pk = event.pk
            event_slug = event.slug
            event_detail_url = reverse('event_detail', args=[event_pk, event_slug])
            event_start_timestamp = event.starts_at.timestamp() * 1000
            organization = event.organization
            place = event.location
            activity = event.type

            if organization.pk not in organizations:
                organization_slug = organization.slug
                organization_pk = organization.pk
                organization_detail_url = reverse('organization_detail',
                                                  args=[organization_pk,
                                                        organization_slug])
                organizations[organization_pk] = {
                    'pk': organization_pk,
                    'name': organization.name,
                    'slug': organization_slug,
                    'organization_detail_url': organization_detail_url,
                }
            
            if place.pk not in places:
                place_slug = place.slug
                place_pk = place.pk
                place_detail_url = reverse('place_detail',
                                                  args=[place_pk,
                                                        place_slug])
                places[place_pk] = {
                    'pk': place_pk,
                    'name': place.name,
                    'truncated_name': place.name[0:25],
                    'slug': place_slug,
                    'place_detail_url': place_detail_url,
                }

            if activity.pk not in activitys:
                activity_slug = activity.slug
                activity_pk = activity.pk
                activity_detail_url = reverse('activity_detail',
                                                    args=[activity_pk,
                                                        activity_slug])
                activitys[activity_pk] = {
                    'pk': activity_pk,
                    'name': activity.name,
                    'truncated_name': activity.name[0:25],
                    'slug': activity_slug,
                    'activity_detail_url': activity_detail_url,
                }

            events += [{
                'pk': event.pk,
                'title': event.title,
                'slug': event_slug,
                'available_seats': event.available_seats,
                'type_picture_url': event.type.picture.url,
                'event_detail_url': event_detail_url,
                'book_url': reverse('booking_form', args=[event_pk]),
                'edit_url': reverse('event_edit', args=[event_pk]),
                'organization_pk': organization.pk,
                'place_pk': event.location.pk,
                'type_pk': event.type.pk,
                'published': event.published,
                'starts_at': event.starts_at.strftime("%H:%M"),
                'ends_at': event.ends_at.strftime("%H:%M"),
                'start_timestamp': event_start_timestamp,
                'user_in_attendees': request.user in event.attendees.all(),
                'user_in_presents': request.user in event.presents.all(),
                'user_in_organizers': request.user in event.organizers.all(),
                'day_month_str': event.starts_at.strftime("%d %B"),
            }]

        return JsonResponse({'status': "OK", "dates": events, "organizations": organizations, "places": places, "activities": activitys, })



def book_event(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        request_body = request.body.decode("utf-8")
        post_data = parse_qs(request_body)
        event_id = post_data['event_id'][0]
        user = CustomUser.objects.get(email=request.user)
        event = Event.objects.get(pk=event_id)
        organization = event.organization
        attendees = event.attendees.all()

        user_volunteer_orgs = OrganizationPerson.objects.filter(user=user,
                                                      role__gte=OrganizationPerson.VOLUNTEER)


        if user in attendees:
            if organization not in user_volunteer_orgs:
                event.available_seats += 1
            event.attendees.remove(user)
            event.save()
            return JsonResponse({'status': 'unbook',
                                 'available_seats': event.available_seats})
        else:
            if event.available_seats >= 0:
                if organization not in user_volunteer_orgs:
                    event.available_seats -= 1
                action.send(request.user, verb='sest inscris', action_object=event)
                event.attendees.add(user)
                # send booking mail here
            else:
                return JsonResponse({'status': -1})

        event.save()
        return JsonResponse({'status': 'unbook',
                             'available_seats': event.available_seats})

def list_users(request, organization_pk, event_pk):
    if request.method != 'GET':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        user = CustomUser.objects.get(email=request.user)
        organization = Organization.objects.get(pk=organization_pk)
        user_is_admin = OrganizationPerson.objects.get(user=user, organization=organization, role__gte=OrganizationPerson.ADMIN)
        if not user_is_admin:
            return JsonResponse({'status': -1})

        users = OrganizationPerson.objects.filter(organization=organization)
        event = Event.objects.get(pk=event_pk)
        every_attendee = event.attendees.all() | event.presents.all() | event.organizers.all()
        users_dict = []
        for user in users:
            if user.user not in every_attendee:
                new_user = {
                    'pk': user.user.pk,
                    'name': user.user.get_full_name(),
                    'email': user.user.email,
                    'role': user.role,
                }
                users_dict += [new_user]
        return JsonResponse({'status': "OK",
                             'users': users_dict})
def add_users(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        request_body = request.body.decode("utf-8")
        post_data = parse_qs(request_body)
        event_pk = post_data['event_pk'][0]
        user_list = post_data['user_list'][0].split(',')
        event = Event.objects.get(pk=event_pk)
        every_attendee = event.attendees.all() | event.presents.all() | event.organizers.all()
        seats = event.available_seats
        presents_pk = []
        attending_pk = []

        for user_pk in user_list:
            user = CustomUser.objects.get(pk=user_pk)
            now = timezone.now()

            if event.starts_at <= now:
                event.presents.add(user)
                pesents_pk += [user.pk]
            else:
                if user not in every_attendee:
                    print("a")
                    seats -= 1

                    event.attendees.add(user)
                    attending_pk += [user.pk]
                else:
                    event.presents.add(user)
                    presents_pk += [user.pk]



        event.available_seats = seats;
        event.save()
        return JsonResponse({'status': 'OK',
                             'seats': seats,
                             'presents_pk': presents_pk,
                             'attending_pk': attending_pk})

