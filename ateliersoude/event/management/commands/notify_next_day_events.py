import datetime

from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from ateliersoude.event.models import Event

from ateliersoude.event.templatetags.app_filters import tokenize


# Run every day at a given time
# 10 16 * * *
class Command(BaseCommand):
    help = "Send email to all registered users the day before the event"

    def add_arguments(self, parser):
        parser.add_argument(
            "website_url",
            help="ex: https://dev.atelier-soude.fr"
        )

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
                unbook_token = tokenize(user, event, "cancel")
                cancel_url = base_url + reverse(
                    "event:cancel_reservation", args=[unbook_token]
                )
                event_url = base_url + reverse(
                    "event:detail", args=[event.id, event.slug]
                )
                msg_plain = render_to_string(
                    "event/mail/event_incoming.txt", context=locals()
                )
                msg_html = render_to_string(
                    "event/mail/event_incoming.html", context=locals()
                )

                send_mail(
                    f"C'est demain - {event.activity.name}",
                    msg_plain,
                    ' f"{event.organization}" <no-reply@atelier-soude.fr>',
                    [user.email],
                    html_message=msg_html,
                )
