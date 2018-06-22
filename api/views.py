from itsdangerous import URLSafeSerializer, BadData
from django.http import JsonResponse, HttpResponse
from users.models import CustomUser
from plateformeweb.models import Event, Organization, OrganizationPerson
from urllib.parse import parse_qs
from django.utils import timezone


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

def book(request):
    if request.method != 'POST':
        # TODO change this
        return HttpResponse("Circulez, il n'y a rien à voir")
    else:
        person = CustomUser.objects.get(email=request.user)
        print("person")
        print(person)
        serial = URLSafeSerializer('some_secret_key',
                                   salt='book')

        print(request.POST)
        # event = serial.loads(request.POST['event_id']);
        # print("event")
        # print(event)
