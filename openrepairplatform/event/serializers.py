from datetime import timedelta, date as dt
from dateutil import rrule, relativedelta
from rest_framework import serializers
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
          "conditions",
        ]


class EventCreateSerializer(serializers.ModelSerializer):

    def clean_weeks(self):
        recurrent_type = self.cleaned_data["recurrent_type"]
        error_message = "Vous devez renseigner au moins une semaine de récurrence."
        if recurrent_type == "MONTHLY":
            if not self.cleaned_data["weeks"]:
                self.add_error("weeks", error_message)
                raise serializers.ValidationError(error_message)
        return self.cleaned_data["weeks"]

    def manage_recurrence(self, dates):
        objects = []
        for date in dates:
            params = {
                "date": date.date(),
                "starts_at": self.cleaned_data["starts_at"],
                "ends_at": self.cleaned_data["ends_at"],
                "organization": self.orga,
                "allow_stuffs": self.cleaned_data["allow_stuffs"],
                "needed_organizers": self.cleaned_data["needed_organizers"],
                "collaborator": self.cleaned_data["collaborator"],
                "external": self.cleaned_data["external"],
                "external_url": self.cleaned_data["external_url"],
                "description": self.cleaned_data["description"],
                "location": self.cleaned_data["location"],
                "publish_at": (
                    date
                    - timedelta(days=int(self.cleaned_data["period_before_publish"]))
                ),
                "activity": self.cleaned_data["activity"],
                "available_seats": self.cleaned_data["available_seats"],
            }
            event = Event.objects.create(**params)
            event.organizers.add(*list(self.cleaned_data["organizers"]))
            event.conditions.add(*list(self.cleaned_data["conditions"]))
            objects.append(event)
        return objects

    def get_rule_list(self):
        if self.cleaned_data["weeks"]:
            weekdays = [
                getattr(relativedelta, day)(int(week))
                for week in self.cleaned_data["weeks"]
                for day in self.cleaned_data["days"]
            ]
        else:
            weekdays = [getattr(rrule, day) for day in self.cleaned_data["days"]]
        rule = list(
            rrule.rrule(
                getattr(rrule, self.cleaned_data["recurrent_type"]),
                byweekday=weekdays,
                dtstart=max(self.cleaned_data["date"], dt.today()),
                until=self.cleaned_data["end_date"],
            )
        )
        return rule

    def save(self, **kwargs):
        breakpoint()
        dates = self.get_rule_list()
        objects = self.manage_recurrence(dates)
        return len(objects)

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
