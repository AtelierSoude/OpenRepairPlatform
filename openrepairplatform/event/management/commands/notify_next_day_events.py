import datetime

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from openrepairplatform.event.models import Event

from openrepairplatform.mail import event_send_mail


# Run every day at a given time
# 10 16 * * *
class Command(BaseCommand):
    help = "Send email to all registered users the day before the event"

    def add_arguments(self, parser):
        parser.add_argument("website_url", help="ex: https://dev.atelier-soude.fr")

    def handle(self, *args, **options):
        base_url = options["website_url"]
        now = timezone.now()
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_23h59 = tomorrow.replace(hour=23, minute=59, second=59)
        tomorrow_00h00 = tomorrow.replace(hour=0, minute=0, second=0)
        events_next_day = (
            Event.objects.filter(published=True)
            .filter(date=tomorrow.date())
            .filter(starts_at__lte=tomorrow_23h59.time())
            .filter(starts_at__gte=tomorrow_00h00.time())
        )
        for event in events_next_day:
            for user in event.registered.all():
                event_send_mail(
                    event,
                    user,
                    f"C'est demain - {event.activity.name}",
                    "event/mail/event_incoming.txt",
                    "event/mail/event_incoming.html",
                    f"{event.organization} <{settings.DEFAULT_FROM_EMAIL}>",
                    [user.email],
                    base_url=base_url,
                )
