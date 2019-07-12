from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from ateliersoude.event.models import Event


# Run every hour
# 20 * * * *
class Command(BaseCommand):
    help = "Publish non published events"

    def add_arguments(self, parser):
        parser.add_argument("website_url", help="ex: http://dev.atelier-soude.fr:8000")

    def handle(self, *args, **options):
        base_url = options["website_url"]
        unpublished_events = Event.objects.filter(published=False).filter(
            publish_at__lte=timezone.now()
        )
        for event in unpublished_events:
            event.published = True
            event.save()
            orga = event.organization
            for user in orga.actives.all() | orga.admins.all():
                event_url = base_url + reverse(
                    "event:detail", kwargs={"pk": event.id, "slug": event.slug}
                )
                msg_plain = render_to_string(
                    "event/mail/event_published.txt", context=locals()
                )
                msg_html = render_to_string(
                    "event/mail/event_published.html", context=locals()
                )              
#                send_mail(
#                    f" {event.organization} organise {event.title} "
#                    f"- seras-tu présent ?",
#                    msg_plain,
#                    "no-reply@atelier-soude.fr",
#                    [user.email],
#                    html_message=msg_html,
#                )
