import os
from datetime import timezone
from openrepairplatform.user.management.commands.data.t import users
from django.core.management.base import BaseCommand, CommandError
from openrepairplatform.user.models import CustomUser
import json
from datetime import date
from django.utils import timezone
import pathlib
from django.core import serializers


class Command(BaseCommand):
    help = "Create objects in database for development purposes"

    types = [
        "user.customuser",
        "inventory.category",
        "inventory.device",
        "inventory.stuff",
        "event.event",
        "user.fee",
        "event.participation",
        "inventory.status",
        "inventory.observation",
        "inventory.reasoning",
        "inventory.repairfolder",
        "user.organization",
        "inventory.intervention",
        "event.activitycategory",
        "event.activity",
        "user.membership",
        "event.condition",
        "location.place",
        "inventory.brand",
        "inventory.action",
    ]

    # def add_arguments(self, parser):
    #     parser.add_argument("test")

    def handle(self, *args, **options):

        with open(
            "deployment/saves-bdd/dev_data_reparons.json", "r", encoding="utf-8"
        ) as file:
            # data = json.load(file)
            # data = json.dumps(data, ensure_ascii=False).encode("utf-8").decode("utf-8")
            # data = json.loads(data)
            data = file.read()

            obj_count = 0

            objects = serializers.deserialize(
                "json",
                data,
                handle_forward_references=True,
                ignorenonexistent=True,
            )

            for obj in objects:
                instance = obj.object

                # Check if this is an event and if organization_id is missing/null
                if hasattr(instance, 'organization_id') and instance.organization_id is None:
                    print(f"Skipping event {instance.pk}: missing organization_id")
                    continue  # Skip this object

                obj.save()
                obj_count+=1
                print(f"Processed {obj_count} objects")



            return 0

            for obj in objects :
                print(type(obj))
                obj.save()
                obj_count+=1
                print(f"Processed {obj_count} objects")

            return 0
            users = [obj["model"] for obj in data if obj["model"] == "user.customuser"]
            types = []

            for d in data:
                if not types.__contains__(d["model"]):
                    types.append(d["model"])

            # print(types)

    def create_users(self):
        pass

    def create_organizations(self):
        pass

    def create_events(self):
        pass
