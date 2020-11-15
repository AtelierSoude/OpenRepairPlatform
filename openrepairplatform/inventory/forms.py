from django.forms import ModelForm
from django import forms
from openrepairplatform.user.models import CustomUser
from openrepairplatform.location.models import Place
from .models import Stuff
from dal import autocomplete

class StuffForm(ModelForm):
    class Meta:
        model = Stuff
        fields = [
            "member_owner",
            "organization_owner",
            "place",
            "state"
        ]

class StuffUserForm(ModelForm):
    class Meta:
        model = Stuff
        fields = [
            "state"
        ]

class StuffOrganizationForm(ModelForm):
    class Meta:
        model = Stuff
        fields = [
            "device",
            "place",
            "state"
        ]

class StuffStateForm(ModelForm):
    class Meta:
        model = Stuff
        fields = [
            "state"
        ]

class StuffOwnerForm(ModelForm):
    class Meta:
        model = Stuff
        fields = [
            "member_owner",
            "organization_owner",
        ]

class StuffPlaceForm(ModelForm):
    class Meta:
        model = Stuff
        fields = [
           "place",
        ]

class StuffDeviceForm(ModelForm):
    class Meta:
        model = Stuff
        fields = [
           "device",
        ]