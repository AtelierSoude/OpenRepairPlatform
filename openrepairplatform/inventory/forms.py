from django.forms import ModelForm
from django import forms
from ateliersoude.user.models import CustomUser
from ateliersoude.location.models import Place
from .models import Stuff
from dal import autocomplete

class StuffForm(ModelForm):
    # type = ChoiceField(
    #     choices=(
    #         ("D", "Device"),
    #         ("T", "Tool"),
    #         ("P", "Part"),
    #     )
    # )
    class Meta:
        model = Stuff
        fields = [
            "member_owner",
            "organization_owner",
            "place",
            "state"
        ]

class StuffUserForm(ModelForm):
    # type = ChoiceField(
    #     choices=(
    #         ("D", "Device"),
    #         ("T", "Tool"),
    #         ("P", "Part"),
    #     )
    # )
    class Meta:
        model = Stuff
        fields = [
            "state"
        ]

class StuffOrganizationForm(ModelForm):
    # type = ChoiceField(
    #     choices=(
    #         ("D", "Device"),
    #         ("T", "Tool"),
    #         ("P", "Part"),
    #     )
    # )
    class Meta:
        model = Stuff
        fields = [
            "place",
            "state"
        ]