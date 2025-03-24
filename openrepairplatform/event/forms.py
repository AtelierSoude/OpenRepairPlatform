from datetime import timedelta, date as dt
from dateutil import rrule, relativedelta
from dal import autocomplete

from django import forms
from django.forms import ModelForm

from openrepairplatform.event.models import Event, Activity, Condition, Participation
from openrepairplatform.location.models import Place
from openrepairplatform.user.models import Organization


class EventForm(ModelForm):
    date = forms.DateField(
        initial=dt.today,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    starts_at = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    ends_at = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    publish_at = forms.DateTimeField(
        initial=dt.today,
        widget=forms.DateTimeInput(format="%Y-%m-%d %H:%M:%S"),
        help_text=(
            "Modifier la date de publication que si nécessaire "
            "(par défaut la date du jour)"
        )
    )

    def __init__(self, *args, **kwargs):
        self.orga = kwargs.pop("orga")
        super().__init__(*args, **kwargs)
        self.fields["organizers"] = forms.ModelMultipleChoiceField(
            queryset=(
                self.orga.actives.all()
                | self.orga.admins.all()
                | self.orga.volunteers.all()
            ),
            widget=autocomplete.ModelSelect2Multiple(
                url="/" + self.orga.slug + "/user_orga_autocomplete/"
            ),
            required=False,
        )
        self.fields["conditions"] = forms.ModelMultipleChoiceField(
            queryset=self.orga.conditions,
            widget=autocomplete.ModelSelect2Multiple(
                url="/event/" + self.orga.slug + "/condition_orga_autocomplete/"
            ),
            required=False,
        )
        self.fields["activity"] = forms.ModelChoiceField(
            widget=autocomplete.ModelSelect2(url="activity_autocomplete"),
            queryset=Activity.objects.all(),
        )

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
            "internal_notes",
        ]
        widgets = {
            "location": autocomplete.ModelSelect2(url="place_autocomplete"),
        }


class RecurrentEventForm(forms.ModelForm):
    recurrent_type = forms.ChoiceField(
        choices=[("WEEKLY", "semaine"), ("MONTHLY", "mois")], label="Par"
    )
    days = forms.MultipleChoiceField(
        choices=Event.DAYS,
        widget=forms.CheckboxSelectMultiple(),
        label="Jour(s)",
    )
    weeks = forms.MultipleChoiceField(
        choices=Event.WEEKS,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "for-month"}),
        label="La ou les semaines",
        required=False,
    )
    starts_at = forms.TimeField(
        label="De", widget=forms.TimeInput(attrs={"type": "time"})
    )
    ends_at = forms.TimeField(label="À", widget=forms.TimeInput(attrs={"type": "time"}))
    date = forms.DateField(
        initial=dt.today,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        label="Date de début",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        label="Date de fin",
    )
    period_before_publish = forms.ChoiceField(
        choices=[
            (1, "1 jour avant"),
            (2, "2 jours avant"),
            (7, "Une semaine avant"),
            (14, "Deux semaines avant"),
            (21, "Trois semaines avant"),
            (28, "Quatre semaines avant"),
            (35, "Cinq semaines avant"),
            (42, "Six semaines avant"),
        ],
        label="Publication",
    )

    def __init__(self, *args, **kwargs):
        self.orga = kwargs.pop("orga")
        super().__init__(*args, **kwargs)
        self.fields["organizers"] = forms.ModelMultipleChoiceField(
            queryset=(
                self.orga.actives.all()
                | self.orga.admins.all()
                | self.orga.volunteers.all()
            ).distinct(),
            widget=autocomplete.ModelSelect2Multiple(
                url="/" + self.orga.slug + "/user_orga_autocomplete/"
            ),
            required=False,
        )
        self.fields["conditions"] = forms.ModelMultipleChoiceField(
            queryset=self.orga.conditions,
            widget=autocomplete.ModelSelect2Multiple(
                url="/event/" + self.orga.slug + "/condition_orga_autocomplete/"
            ),
            required=False,
        )
        self.fields["activity"] = forms.ModelChoiceField(
            widget=autocomplete.ModelSelect2(url="activity_autocomplete"),
            queryset=Activity.objects.all(),
        )

    def clean_weeks(self):
        recurrent_type = self.cleaned_data["recurrent_type"]
        error_message = "Vous devez renseigner au moins une semaine de récurrence."
        if recurrent_type == "MONTHLY":
            if not self.cleaned_data["weeks"]:
                self.add_error("weeks", error_message)
                raise forms.ValidationError(error_message)
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

    def save(self, commit=False):
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
            "internal_notes",
        ]
        widgets = {
            "location": autocomplete.ModelSelect2(url="place_autocomplete"),
        }


class ActivityForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["picture"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Activity
        exclude = ["slug", "organization"]


class ConditionForm(ModelForm):
    class Meta:
        model = Condition
        exclude = ["slug", "organization"]


class EventSearchForm(forms.Form):
    starts_after = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        required=False,
        label="Commence après le",
    )
    starts_before = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        required=False,
        label="Commence avant le",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        future_events = Event.future_published_events()
        self.fields["activity"] = forms.ModelChoiceField(
            required=False,
            queryset=Activity.objects.filter(events__in=future_events).distinct(),
            widget=autocomplete.ModelSelect2(
                url="event:future_event_activity_autocomplete"
            ),
            label="Activité",
        )
        self.fields["organization"] = forms.ModelChoiceField(
            required=False,
            queryset=Organization.objects.filter(events__in=future_events).distinct(),
            label="Organisateur",
        )


class ParticipationForm(ModelForm):
    class Meta:
        model = Participation
        fields = ["amount", "payment"]


class InvitationForm(forms.Form):
    email_participant = forms.EmailField(
        label="Inviter un participant",
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "d-none form-control"}
        ),
        required=False
    )
    email_animator = forms.EmailField(
        label="Inviter un animateur",
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "d-none form-control"}
        ),
        required=False
    )

    def is_valid(self):
        res = super().is_valid()
        data = self.cleaned_data
        if not data["email_participant"] and not data["email_animator"]:
            return False
        return res
