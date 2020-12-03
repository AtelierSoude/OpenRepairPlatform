from datetime import timedelta, date as dt
from django.forms import ModelForm
from django import forms
from openrepairplatform.user.models import CustomUser
from openrepairplatform.location.models import Place
from .models import Stuff, Device, Category, Observation, RepairFolder, Intervention, Brand, Reasoning, Action, Status
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

class StuffForm(BSModalModelForm):
    category = forms.ModelChoiceField(
        widget=autocomplete.ModelSelect2(url='inventory:category_autocomplete'),
        label="Catégorie d'appareil",
        required = False,
        queryset = Category.objects.all(),
    )
    device = forms.ModelChoiceField(
        widget=autocomplete.ModelSelect2(url='inventory:device_autocomplete', 
        forward=['category']),
        label="Type d'appareil",
        queryset = Device.objects.all(),
        required = False
    )
    create_device = forms.BooleanField(
        label = "Je ne trouve pas mon type d'appareil dans la liste ci dessus",
        required = False,
    )
    brand = forms.ModelChoiceField(
        widget=autocomplete.ModelSelect2(url='inventory:brand_autocomplete'),
        label="Marque",
        required=False,
        queryset = Brand.objects.all()
        )
    model = forms.CharField(
        label="Designation/modèle",
        help_text="Si vous n'êtes pas sûr, ne remplissez pas ce champ",
        required=False
    )
    create_folder = forms.BooleanField(
        label = "Je souhaite ajouter un dossier de réparation",
        required = False
    )
    repair_date = forms.DateField(
        initial=dt.today(),
        label="date",
        required = False, 
    )
    ongoing = forms.BooleanField(
        label = "Ce dossier est-il en cours ?",
        required = False, 
        initial= True,
    )
    observation = forms.ModelChoiceField(
        widget=autocomplete.ModelSelect2(url='inventory:observation_autocomplete'),
        help_text="Quel est (ou était) le problème ?",
        required = False,
        queryset = Observation.objects.all()
    )
    reasoning = forms.ModelChoiceField(
        widget=autocomplete.ModelSelect2(url='inventory:reasoning_autocomplete'),
        help_text="Quel en est (ou serait) la cause ?",
        label="Raisonnement",
        required = False,
        queryset = Reasoning.objects.all()
    )
    action = forms.ModelChoiceField(
        widget=autocomplete.ModelSelect2(url='inventory:action_autocomplete'),
        help_text="Qu'avez-vous fait ?",
        required = False,
        queryset = Action.objects.all()
    )
    status = forms.ModelChoiceField(
        widget=autocomplete.ModelSelect2(url='inventory:status_autocomplete'),
        help_text="Quel est le résultat de l'action ?",
        required = False,
        queryset = Status.objects.all()
    )

    def clean_device(self):
        device = self.cleaned_data['device']
        if not device:
            device = {}
            device["category"] = self.cleaned_data['category']
            device["brand"] = self.cleaned_data['brand']
            device["model"] = self.cleaned_data['model']
            if not device["category"]:
              self.add_error("category", "Ce champ ne peut pas être vide")
            device = Device.objects.create(**device)
            self.cleaned_data['device'] = device
        return self.cleaned_data['device']

    def init_folder(self, data):
        self.folder = {}
        self.intervention = {}
        self.folder['open_date'] = data['repair_date']
        self.folder['ongoing'] = data['ongoing']
        self.intervention['repair_date'] = data['repair_date']
        self.intervention['observation'] = data['observation']
        self.intervention['reasoning'] = data['reasoning']
        self.intervention['action'] = data['action']
        self.intervention['status'] = data['status']
        for key, value in self.folder.items():
            if not value:
                self.add_error(key, f'le champ {key} ne peut pas être vide.')
        for key, value in self.intervention.items():
            if not value:
                self.add_error(key, f'le champ {key} ne peut pas être vide.')
        self.create_folder = data['create_folder']

    def clean(self):
        if getattr(self, "user", False):
            self.cleaned_data["member_owner"] = self.user
        if getattr(self, "organization", False):
            self.cleaned_data["organization_owner"] = self.organization
        if self.cleaned_data['create_folder']: 
            self.init_folder(self.cleaned_data)

    def save(self, commit=True):
            instance = super().save(commit=commit)
            if self.create_folder:
                self.folder['stuff'] = instance
                folder = RepairFolder.objects.create(**self.folder)
                self.intervention['folder'] = folder
                intervention = Intervention.objects.create(**self.intervention)

    def __init__(self, organization=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if organization:
            self.organization = organization
            self.fields['place'] = forms.ModelChoiceField(
                widget=autocomplete.ModelSelect2(url='place_autocomplete'),
                label="Localisation",
                queryset= Place.objects.all(),
                help_text="Où se trouve l'appareil ?",
                required = False
            )
        elif user:
            self.user = user 
        else:
          raise forms.ValidationError('Vous devez avoir une organisation ou un utilisateur lié à ce formulaire.')
    
    class Meta:
        model = Stuff
        fields = (
            "category",
            "create_folder",
            "create_device",
            "brand",
            "model",
            "state",
            "organization_owner",
            "member_owner",
            "information",
            "device",
            "ongoing",
            "observation",
            "action",
            "reasoning",
            "status",
            "repair_date",
        )


