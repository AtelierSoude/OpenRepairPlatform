from itsdangerous import URLSafeSerializer, BadData
from django.http import JsonResponse, HttpResponse
from users.models import CustomUser
from plateformeweb.models import Event

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
