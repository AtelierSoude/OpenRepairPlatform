import django_filters
from django.db import models
from django import forms
from dal import autocomplete 

from openrepairplatform.inventory.models import (
    Stuff,
    Device,
    Category
)

class StockFilter(django_filters.FilterSet):

    device__category = django_filters.ModelChoiceFilter(
        widget=autocomplete.ModelSelect2(url='inventory:category_autocomplete'),
        queryset=Category.objects.all()
    )

    class Meta:
        model = Stuff
        fields = ["device__category", "id", "state"]