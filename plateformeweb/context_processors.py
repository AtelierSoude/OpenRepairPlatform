from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now
from .models import Event, PublishedEvent
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

# <h1>
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
# </h1>

def user_data(request):
    if isinstance(request.user, AnonymousUser) or request.user is None:
        return {}
    events_attending = PublishedEvent.objects.all().filter(
        attendees=request.user).filter(
        ends_at__gte=now())
    events_organizing = Event.objects.all().filter(
        organizers=request.user).filter(
        ends_at__gte=now())
    return {'my_events_attending': events_attending,
            'my_events_organizing': events_organizing}
