from dal import autocomplete
from django.shortcuts import get_object_or_404

from openrepairplatform.event.models import Event, Activity
from openrepairplatform.location.models import Place
from openrepairplatform.mixins import HasVolunteerPermissionMixin
from openrepairplatform.user.models import Organization, CustomUser


class ConditionOrgaAutocomplete(
    HasVolunteerPermissionMixin, autocomplete.Select2QuerySetView
):
    def get_queryset(self, *args, **kwargs):
        orga_slug = self.kwargs.get("orga_slug")
        organization = get_object_or_404(Organization, slug=orga_slug)

        if not self.request.user.is_authenticated:
            return CustomUser.objects.none()

        qs = organization.conditions.all().order_by("name")

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class FutureEventActivityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        future_events = Event.future_published_events()
        qs = (
            Activity.objects.filter(events__in=future_events)
            .distinct()
            .order_by("name")
        )

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class FutureEventPlaceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        future_events = Event.future_published_events()
        qs = (
            Place.objects.filter(events__in=future_events)
            .distinct()
            .order_by("address")
        )

        activity_pk = self.forwarded.get("activity", None)

        if activity_pk:
            activity = Activity.objects.get(pk=activity_pk)
            future_events = future_events.filter(activity=activity)
            qs = (
                Place.objects.filter(events__in=future_events)
                .distinct()
                .order_by("address")
            )

        if self.q:
            qs = qs.filter(address__icontains=self.q)

        return qs
