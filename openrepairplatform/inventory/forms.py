from datetime import timedelta, date as dt
from django.forms import ModelForm
from django import forms
from openrepairplatform.user.models import CustomUser
from openrepairplatform.location.models import Place
from .models import Stuff, Device, Category, Observation, RepairFolder, Intervention, Brand
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
        queryset = Category.objects.all(),
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
        label = "Ce dossier est-il clos ?",
        required = False, 
    )
    observation = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:observation_autocomplete'),
        help_text="Quel est (ou était) le problème ?",
        required = False
    )
    reasoning = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:reasoning_autocomplete'),
        help_text="Quel en est (ou serait) la cause ?",
        label="Raisonnement",
        required = False
    )
    action = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:action_autocomplete'),
        help_text="Qu'avez-vous fait ?",
        required = False
    )
    status = forms.ChoiceField(
        widget=autocomplete.Select2(url='inventory:status_autocomplete'),
        help_text="Quel est le résultat de l'action ?",
        required = False
    )

    def clean_create_folder(self):
        self.folder = {}
        self.intervention = {}
        self.create_folder = self.cleaned_data.pop('create_folder')
        if self.create_folder:
            self.folder['repair_date'] = self.cleaned_data.pop('repair_date')
            self.folder['ongoing'] = self.cleaned_data.pop('ongoing')
            self.intervention['observation'] = self.cleaned_data.pop('observation')
            self.intervention['reasoning'] = self.cleaned_data.pop('reasoning')
            self.intervention['action'] = self.cleaned_data.pop('action')
            self.intervention['status'] = self.cleaned_data.pop('status')
            for key, value in self.folder:
                if not value:
                    self.add_error(key, 'Ce champ ne peut pas être vide.')
            for key, value in self.intervention:
                if not value:
                    self.add_error(key, 'Ce champ ne peut pas être vide.')

    def clean_device(self):
        device = self.cleaned_data['device']
        import pdb; pdb.set_trace()
        if not device:
            device = {}
            device["category"] = self.cleaned_data.pop('category')
            device["brand"] = self.cleaned_data.pop('brand')
            device["model"] = self.cleaned_data.pop('model')
            if not device["category"]:
              self.add_error("category", "Ce champ ne peut pas être vide")
            device = Device.objects.create(**device)
            self.cleaned_data['device'] = device.pk  

    def clean(self):
        if getattr(self, "user", False):
            self.cleaned_data["member_owner"] = self.user
        if getattr(self, "organization", False):
            self.cleaned_data["organization_owner"] = self.organization

    def save(self, commit=True):
            instance = super().save(commit=commit)
            if self.create_folder:
                self.folder['stuff'] = instance
                folder = RepairFolder.objects.create(**self.folder)
                self.intervention['folder'] = folder
                intervention = Intervention.objects.create(**self.intervention)

    def __init__(self, organization=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['device'] = forms.ModelChoiceField(
                widget=autocomplete.ModelSelect2(url='inventory:device_autocomplete', 
                forward=['category']),
                label="Type d'appareil",
                queryset = Device.objects.all(),
                required = False
            )
        if organization:
            self.organization = organization
            self.Meta.fields += ('place',)
            self.fields['place'] = forms.ChoiceField(
                widget=autocomplete.Select2(url='place_autocomplete'),
                label="Localisation",
                help_text="Où se trouve l'appareil ?",
                required = False
            )
            self.fields['place'].initial = 'whatever you want'
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
            "ongoing",
            "observation",
            "action",
            "reasoning",
            "status",
            "repair_date",
            "brand",
            "model",
            "state",
            "organization_owner",
            "member_owner",
            "information",
            "device",
        )


