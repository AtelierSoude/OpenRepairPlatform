import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from openrepairplatform.event.models import Event
from openrepairplatform.activity.models import Activity
from openrepairplatform.user.models import User  # Adapter selon votre projet

class Command(BaseCommand):
    help = "Generate n events (half recurring electronic repair events, half random)"

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=10, help='Number of events to generate')

    def handle(self, *args, **options):
        n = options['number']
        now = timezone.now()
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        activity, _ = Activity.objects.get_or_create(name="Atelier - Réparation électronique collective")
        users = list(User.objects.all())
        events_created = 0
        day_offset = 0

        # Génère la moitié des évènements comme récurrents (mardi/jeudi)
        rec_events = n // 2
        while events_created < rec_events:
            event_date = start_date + timedelta(days=day_offset)
            weekday = event_date.weekday()
            if weekday == 1:  # Mardi
                starts_at = event_date.replace(hour=14, minute=0)
                ends_at = event_date.replace(hour=17, minute=0)
            elif weekday == 3:  # Jeudi
                starts_at = event_date.replace(hour=17, minute=0)
                ends_at = event_date.replace(hour=20, minute=0)
            else:
                day_offset += 1
                continue
            places = random.randint(6, 8)
            nb_registered = random.randint(0, places)
            event = Event.objects.create(
                date=event_date.date(),
                starts_at=starts_at.time(),
                ends_at=ends_at.time(),
                activity=activity,
                organization=None,
                published=True,
                places=places,
            )
            if users:
                event.registered_users.set(random.sample(users, nb_registered))
            events_created += 1
            day_offset += 1

        # Génère le reste des évènements (non récurrents, dates aléatoires)
        for i in range(n - rec_events):
            event_date = start_date + timedelta(days=random.randint(0, 30))
            starts_hour = random.randint(9, 18)
            starts_at = event_date.replace(hour=starts_hour, minute=0)
            ends_at = starts_at + timedelta(hours=2)
            places = random.randint(6, 8)
            nb_registered = random.randint(0, places)
            event = Event.objects.create(
                date=event_date.date(),
                starts_at=starts_at.time(),
                ends_at=ends_at.time(),
                activity=None,
                organization=None,
                published=True,
                places=places,
            )
            if users:
                event.registered_users.set(random.sample(users, nb_registered))

        self.stdout.write(self.style.SUCCESS(f"{n} events generated."))