import django_filters
from dal import autocomplete

from openrepairplatform.user.models import Fee, CustomUser, Membership
from openrepairplatform.event.models import Event
from openrepairplatform.location.models import Place
from openrepairplatform.event.models import Activity


class EventFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter()
    location = django_filters.ModelChoiceFilter(
        widget=autocomplete.ModelSelect2(url="place_autocomplete"),
        queryset=Place.objects.all(),
    )
    activity = django_filters.ModelChoiceFilter(
        widget=autocomplete.ModelSelect2(url="activity_autocomplete"),
        queryset=Activity.objects.all(),
    )

    class Meta:
        model = Event
        fields = ["date", "activity", "location"]


class FeeFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Fee
        fields = ["date"]


class MemberFilter(django_filters.FilterSet):
    class Meta:
        model = Membership
        fields = {
            "user__first_name": ["icontains"],
            "user__last_name": ["icontains"],
            "user__street_address": ["icontains"],
        #   add a filter in order to filter only up to date memberships
        }
