from django import forms
from django.forms import ModelForm

from ateliersoude.location.models import Place


class PlaceForm(ModelForm):
    longitude = forms.CharField(widget=forms.HiddenInput)
    latitude = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["picture"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Place
        exclude = ["created_at", "updated_at", "slug", "owner", "organization"]
