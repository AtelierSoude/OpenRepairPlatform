from datetime import timedelta, date as dt
from django.forms import ModelForm
from django import forms
from openrepairplatform.user.models import CustomUser
from openrepairplatform.location.models import Place
from .models import Stuff, Device, Category, Observation, RepairFolder
from dal import autocomplete, forward
from bootstrap_modal_forms.forms import BSModalModelForm

class StuffEditForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['device'] = forms.ModelChoiceField(
            widget=autocomplete.ModelSelect2(url='inventory:device_autocomplete',),
            queryset= Device.objects.all()
        )
    
    class Meta:
        model = Stuff
        fields = [
            "state",
            "device",
            "member_owner",
            "organization_owner",
            "place",
            'information',
        ]

class FolderForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['open_date'] = forms.DateField(
        initial=dt.today(),
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        label="date"
    )
    class Meta:
        model = RepairFolder
        fields = [
            "open_date",
            "ongoing",
        ]

class StuffForm(ModelForm):
    category = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:category_autocomplete'),
        label="Catégorie d'appareil",
        required = True
    )
    device = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:device_autocomplete', 
        forward=['category']),
        label="Type d'appareil",
    )
    create_device = forms.BooleanField(
        label = "Je ne trouve pas mon type d'appareil dans la liste ci dessus",
        required = False
    )
    brand = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:brand_autocomplete'),
        label="Marque",
        required=False,
        )
    model = forms.CharField(
        label="Designation/modèle",
        help_text="Si vous n'êtes pas sûr, ne remplissez pas ce champ",
        required=False
    )
    place = forms.ChoiceField(
        widget=autocomplete.Select2(url='place_autocomplete'),
        label="Localisation",
        help_text="Où se trouve l'appareil ?",
        )
    create_folder = forms.BooleanField(
        label = "Je souhaite ajouter un dossier de réparation",
        required = False
    )
    repair_date = forms.DateField(
        initial=dt.today(),
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        label="date"
    )
    ongoing = forms.BooleanField(
        label = "Ce dossier est-il clos ?",
        required = False, 
    )
    observation = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:observation_autocomplete'),
        help_text="Quel est (ou était) le problème ?"
    )
    reasoning = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:reasoning_autocomplete'),
        help_text="Quel en est (ou serait) la cause ?",
        label="Raisonnement"
    )
    action = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:action_autocomplete'),
        help_text="Qu'avez-vous fait ?"
    )
    status = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:status_autocomplete'),
        help_text="Quel est le résultat de l'action ?"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Stuff
        fields = [
            "state",
            'information',
        ]


