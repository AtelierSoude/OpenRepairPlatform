from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now
from plateformeweb.models import Event, PublishedEvent, Place
from users.models import CustomUser


# See https://stackoverflow.com/a/28533875

# NOTE requiert plateformeweb.context_processors.user_data dans les context
# processors de settings.py

# rajoute 2 variables de template dans le contexte
# - my_events_attending (events futurs ou le user participe, publiés uniquement)
# - my_events_organizing (tous les events futurs où le user organise, publiés
#   ou non)

# les variables de templates donnent accès au queryset (lazy evaluation, donc
# pas de requête si pas d'affichage), exemple:

#     <ul>
#         {% for item in my_events_attending %}
#             <li>{{ item.title }}</li>
#         {% endfor %}
#     </ul>
#     <ul>
#         {% for item in my_events_organizing %}
#             <li>{{ item.title }}</li>
#         {% endfor %}
#     </ul>

# See
# https://docs.djangoproject.com/en/1.11/topics/db/queries/#spanning-multi-valued-relationships
# for the filter() call


def user_data(request):
    if isinstance(request.user, AnonymousUser) or request.user is None:
        return {}
    events_attending = PublishedEvent.objects.all().filter(
        attendees=request.user, ends_at__gte=now())
    events_organizing = Event.objects.all().filter(
        organizers=request.user, ends_at__gte=now())
    return {'my_events_attending': events_attending,
            'my_events_organizing': events_organizing}

def last_events(request):
    events = PublishedEvent.objects.all().filter(
        starts_at__gte=now()).order_by('starts_at')[:4]
    return {'last_events': events}
