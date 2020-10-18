import django_filters
from django.db import models
from django import forms

from ateliersoude.user.models import (
    Fee, CustomUser
)
class FeeFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Fee 
        fields = ['date']

class MemberFilter(django_filters.FilterSet):
   
    class Meta:
        model = CustomUser
        fields = {
            'first_name': ['icontains'],
            'last_name': ['icontains'],
            'email': ['icontains'],
        }