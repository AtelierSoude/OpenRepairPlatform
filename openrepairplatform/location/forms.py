from django import forms
from django.contrib.gis.geos import Point
from django.forms import ModelForm

from openrepairplatform.location.models import Place


class PlaceForm(ModelForm):
    latitude = forms.CharField(widget=forms.HiddenInput, required=False)
    longitude = forms.CharField(widget=forms.HiddenInput, required=False)
    zipcode = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["picture"].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data["longitude"] and self.cleaned_data["latitude"]:
            longitude = float(self.cleaned_data["longitude"])
            latitude = float(self.cleaned_data["latitude"])
            instance.location = Point(longitude, latitude)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Place
        exclude = [
            "created_at",
            "updated_at",
            "slug",
            "owner",
            "organization",
            "location",
        ]
