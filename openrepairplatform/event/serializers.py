from datetime import timedelta, date as dt
from dateutil import rrule, relativedelta
from rest_framework import serializers
from rest_framework.fields import empty
from .models import Event


class EventUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
          "activity",
          "is_free",
          "members_only",
          "available_seats",
          "booking",
          "allow_stuffs",
          "collaborator",
          "external",
          "external_url",
          "description",
          "location",
          "date",
          "starts_at",
          "ends_at",
          "publish_at",
          "needed_organizers",
          "organizers",
          "organization",
          "conditions",
        ]


class EventCreateSerializer(serializers.ModelSerializer):
    recurrent_type = serializers.ChoiceField(
        choices=[("WEEKLY", "semaine"), ("MONTHLY", "mois")], required=False
    )
    period_before_publish = serializers.ChoiceField(
        choices=[1, 2, 7, 14, 21, 28, 35, 42], required=False
    )
    days = serializers.MultipleChoiceField(choices=Event.DAYS, required=False)
    weeks = serializers.MultipleChoiceField(choices=Event.WEEKS, required=False)
    starts_at = serializers.TimeField(required=False)
    ends_at = serializers.TimeField(required=False)
    date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def clean_weeks(self):
        recurrent_type = self.validated_data["recurrent_type"]
        error_message = "Vous devez renseigner au moins une semaine de récurrence."
        if recurrent_type == "MONTHLY":
            if not self.validated_data["weeks"]:
                self.add_error("weeks", error_message)
                raise serializers.ValidationError(error_message)
        return self.validated_data["weeks"]

    def manage_recurrence(self, dates):
        objects = []
        for date in dates:
            params = {
                "date": date.date(),
                "starts_at": self.validated_data["starts_at"],
                "ends_at": self.validated_data["ends_at"],
                "organization": self.validated_data["organization"],
                "allow_stuffs": self.validated_data["allow_stuffs"],
                "needed_organizers": self.validated_data["needed_organizers"],
                "collaborator": self.validated_data.get("collaborator", ""),
                "external": self.validated_data["external"],
                "external_url": self.validated_data["external_url"],
                "description": self.validated_data["description"],
                "location": self.validated_data["location"],
                "publish_at": (
                    date
                    - timedelta(days=int(self.validated_data["period_before_publish"]))
                ),
                "activity": self.validated_data["activity"],
                "available_seats": self.validated_data["available_seats"],
            }
            event = Event.objects.create(**params)
            event.organizers.add(*list(self.validated_data["organizers"]))
            event.conditions.add(*list(self.validated_data["conditions"]))
            objects.append(event)
        return objects

    def get_rule_list(self):
        if self.validated_data["weeks"]:
            weekdays = [
                getattr(relativedelta, day)(int(week))
                for week in self.validated_data["weeks"]
                for day in self.validated_data["days"]
            ]
        else:
            weekdays = [getattr(rrule, day) for day in self.validated_data["days"]]
        rule = list(
            rrule.rrule(
                getattr(rrule, self.validated_data["recurrent_type"]),
                byweekday=weekdays,
                dtstart=max(self.validated_data["date"], dt.today()),
                until=self.validated_data["end_date"],
            )
        )
        return rule

    def save(self, **kwargs):
        if self.validated_data.get("recurrent_type", False):
            dates = self.get_rule_list()
            objects = self.manage_recurrence(dates)
            return len(objects)
        else:
            return super().save(**kwargs)

    class Meta:
        model = Event
        fields = [
            "activity",
            "is_free",
            "available_seats",
            "members_only",
            "booking",
            "allow_stuffs",
            "collaborator",
            "external",
            "external_url",
            "description",
            "organization",
            "organizers",
            "needed_organizers",
            "conditions",
            "location",
            "recurrent_type",
            "date",
            "days",
            "weeks",
            "starts_at",
            "ends_at",
            "end_date",
            "period_before_publish",
        ]
