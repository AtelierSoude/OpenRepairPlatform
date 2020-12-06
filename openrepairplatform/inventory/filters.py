import django_filters
from django.db import models
from django import forms

from openrepairplatform.inventory.models import (
    Stuff
)
class StockFilter(django_filters.FilterSet):
   
    class Meta:
        model = Stuff
        fields = ["device", "id", "state"]