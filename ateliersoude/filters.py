import django_filters
from django.db import models
from django import forms

from ateliersoude.user.models import (
    Fee
)
class FeeFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Fee 
        fields = ['date']