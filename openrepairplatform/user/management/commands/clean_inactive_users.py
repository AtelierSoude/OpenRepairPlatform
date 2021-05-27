from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from openrepairplatform.event.models import Event
from openrepairplatform.user.models import CustomUser


# Run every day at a given time
# 10 22 * * *
class Command(BaseCommand):
    help = "Clean inactive users"

    def handle(self, *args, **options):
        """
        Check
        """
        two_week_ago = timezone.now() - timedelta(days=15)
        events = Event.objects.filter(date__gt=two_week_ago.date())
        users = CustomUser.objects.filter(
            first_name="",
            last_name="",
            memberships__isnull=True,
            registered_events__date__lte=two_week_ago.date(),
            presents_events__isnull=True,
        )
        inactive_users = []
        for user in users:
            is_active = False
            for event in events:
                if user in event.registered.all():
                    is_active = True
            if not is_active:
                inactive_users.append(user)

        for user in inactive_users:
            user.delete()
