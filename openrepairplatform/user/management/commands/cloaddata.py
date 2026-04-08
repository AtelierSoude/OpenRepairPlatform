from django.core.management.commands.loaddata import Command as LoadDataCommand
from django.core.serializers import deserialize
from django.db import transaction
import datetime

from openrepairplatform.event.models import Event
from openrepairplatform.inventory.models import Stuff, Intervention, RepairFolder
from openrepairplatform.user.models import Fee, Membership


class Command(LoadDataCommand):
    """
    Extends the loaddata command to edit the models after their importation
    """
    def handle(self, *fixture_labels, **options):
        self.stdout.write("Start import")

        # Import the data from the fixture
        super().handle(*fixture_labels, **options)

        self.stdout.write("Import finished.")

        # Updates the dates in the objects
        self.stdout.write("Start updates")

        now = datetime.datetime.now()
        for e in Event.objects.all():
            e.date = e.date.replace(year=now.year)
            e.save()

        for o in Fee.objects.all():
            o.date = o.date.replace(year=now.year)
            o.save()

        for o in Membership.objects.all():
            o.first_payment = o.first_payment.replace(year=now.year)
            o.save()

        for s in Stuff.objects.all():
            s.added_date = s.added_date.replace(year=now.year)
            s.save()

        for o in Intervention.objects.all():
            if o.repair_date :
                o.repair_date = o.repair_date.replace(year=now.year)
            o.save()

        for o in RepairFolder.objects.all():
            o.open_date = o.open_date.replace(year=now.year)
            o.save()

        self.stdout.write("Updates finished")