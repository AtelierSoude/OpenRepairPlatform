from datetime import timedelta, date as dt
from django.forms import ModelForm
from django import forms
from openrepairplatform.utils import validate_image
from openrepairplatform.user.models import CustomUser
from openrepairplatform.location.models import Place
from .models import Stuff, Device, Category, Observation, RepairFolder, Intervention, Brand, Reasoning, Action, Status, Intervention
from dal import autocomplete, forward
from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.mixins import CreateUpdateAjaxMixin

class StuffEditOwnerForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member_owner"] = forms.ModelChoiceField(
            queryset=CustomUser.objects.all(),
            widget=autocomplete.ModelSelect2(url='user_autocomplete', attrs={'data-html': True, 'data-allow-clear': "true"}),
            label="Cherchez un utilisateur"
        )

    class Meta:
        model = Stuff
        fields = [
            "member_owner",
            "organization_owner",
        ]

class StuffEditPlaceForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['place'] = forms.ModelChoiceField(
            widget=autocomplete.ModelSelect2(url='place_autocomplete'),
            label="Localisation",
            queryset= Place.objects.all(),
            help_text="Où se trouve l'appareil ?",
        )

    class Meta:
        model = Stuff
        fields = [
            "place",
        ]

class StuffEditStateForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Stuff
        fields = [
            "state",
        ]

class FolderForm(BSModalModelForm):
    BROKEN = "B"
    WORKING = "W"
    DISASSEMBLED = "D"
    FIXING = "F"
    THROWN = "T"
    PARTIAL = "P"
    STATES = [
        (BROKEN, "En panne"),
        (WORKING, "Fonctionnel"),
        (DISASSEMBLED, "Désassemblé"),
        (FIXING, "En réparation"),
        (THROWN, "Evaporé"),
        (PARTIAL, "Partiel"),
    ]
    stuff_state = forms.ChoiceField(
        choices=STATES,
        label="Etat"
    )
    change_stuff_state = forms.BooleanField(
        label = "Ce dossier change l'état général de l'appareil",
        required = False, 
        initial= False,
    )
    ongoing = forms.BooleanField(
        label = "Dossier en cours",
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

    def init_folder(self, data):
        self.folder = {}
        self.intervention = {}
        self.folder['open_date'] = data['open_date']
        self.folder['ongoing'] = data['ongoing']
        self.intervention['repair_date'] = data['open_date']
        self.intervention['observation'] = data['observation']
        self.intervention['reasoning'] = data['reasoning']
        self.intervention['action'] = data['action']
        self.intervention['status'] = data['status']
        for key, value in self.folder.items():
            if not value:
                self.add_error(key, f'le champ {key} ne peut pas être vide.')
        if not self.intervention['observation']:
            self.add_error(f'Veuillez rentrer au moins une observation.')
    
    def clean(self):
        self.init_folder(self.cleaned_data)

    def save(self, commit=True):
            instance = super().save(commit=commit)
            self.folder['stuff'] = self.stuff
            folder = RepairFolder.objects.create(**self.folder)
            self.intervention['folder'] = folder
            intervention = Intervention.objects.create(**self.intervention)
            if self.cleaned_data["change_stuff_state"]:
                state = self.cleaned_data["stuff_state"]
                if state:
                    self.stuff.__dict__.update(state=state)
                    self.stuff.save()
            else: 
                self.add_error(f"Si vous souhaitez modifier l'état de l'appareil, renseignez un état")
            return instance 

    def __init__(self, stuff=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if stuff:
            self.stuff = stuff
        self.fields['open_date'] = forms.DateField(
            initial=dt.today(),
            widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            label="date",
        )
        self.fields['ongoing'] = forms.BooleanField(
            label = "Dossier en cours",
            initial = True
        )

    class Meta:
        model = RepairFolder
        fields = [
            "open_date",
            "ongoing",
            "observation",
            "reasoning",
            "action",
            "status",
            "stuff_state",
            "change_stuff_state"
        ]

class InterventionForm(BSModalModelForm):
    BROKEN = "B"
    WORKING = "W"
    DISASSEMBLED = "D"
    FIXING = "F"
    THROWN = "T"
    PARTIAL = "P"
    STATES = [
        (BROKEN, "En panne"),
        (WORKING, "Fonctionnel"),
        (DISASSEMBLED, "Désassemblé"),
        (FIXING, "En réparation"),
        (THROWN, "Evaporé"),
        (PARTIAL, "Partiel"),
    ]
    stuff_state = forms.ChoiceField(
        choices=STATES,
        label="Etat"
    )
    close_folder = forms.BooleanField(
        label = "Cette intervention clos ce dossier",
        required = False, 
        initial= False,
    )
    change_stuff_state = forms.BooleanField(
        label = "Cette intervention a modifier l'état général de l'appareil",
        required = False, 
        initial= False,
    )

    def clean(self):
        if getattr(self, "folder", False):
            self.cleaned_data["folder"] = self.folder

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if self.cleaned_data["close_folder"]:
            self.folder.__dict__.update(ongoing=False)
            self.folder.save()
        if self.cleaned_data["change_stuff_state"]:
            state = self.cleaned_data["stuff_state"]
            if state:
                self.stuff.__dict__.update(state=state)
                self.stuff.save()
            else: 
                self.add_error(f"Si vous souhaitez modifier l'état de l'appareil, renseignez un état")
        return instance 

    def __init__(self, folder=None, stuff=None, *args, **kwargs):
        if folder:
            self.folder = folder
        if stuff:
            self.stuff = stuff 
        super().__init__(*args, **kwargs)
        self.fields['repair_date'] = forms.DateField(
            initial=dt.today(),
            widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            label="date",
        )
        self.fields["observation"] = forms.ModelChoiceField(
            widget=autocomplete.ModelSelect2(url='inventory:observation_autocomplete'),
            help_text="Quel est (ou était) le problème ?",
            required = False,
            queryset = Observation.objects.all()
        )
        self.fields["reasoning"] = forms.ModelChoiceField(
            widget=autocomplete.ModelSelect2(url='inventory:reasoning_autocomplete'),
            help_text="Quel en est (ou serait) la cause ?",
            label="Raisonnement",
            required = False,
            queryset = Reasoning.objects.all()
        )
        self.fields["action"] = forms.ModelChoiceField(
            widget=autocomplete.ModelSelect2(url='inventory:action_autocomplete'),
            help_text="Qu'avez-vous fait ?",
            required = False,
            queryset = Action.objects.all()
        )
        self.fields["status"] = forms.ModelChoiceField(
            widget=autocomplete.ModelSelect2(url='inventory:status_autocomplete'),
            help_text="Quel est le résultat de l'action ?",
            required = False,
            queryset = Status.objects.all()
        )

    class Meta:
        model = Intervention
        fields = [
            "repair_date",
            "observation",
            "reasoning",
            "action",
            "status",
            "folder",
            "close_folder",
            "change_stuff_state",
            "stuff_state",
        ]

class StuffForm(BSModalModelForm, CreateUpdateAjaxMixin):
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
    picture = forms.ImageField(
        required=False,
        label="Photo"
    )
    create_folder = forms.BooleanField(
        label = "Je souhaite ajouter un dossier de réparation",
        required = False
    )
    repair_date = forms.DateField(
        initial=dt.today(),
        label="date",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        required = False, 
    )
    ongoing = forms.BooleanField(
        label = "Dossier en cours",
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
            device["picture"] = self.cleaned_data['picture']
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
        if getattr(self, "event", False):
            self.intervention['event'] = self.event
        self.intervention['observation'] = data['observation']
        self.intervention['reasoning'] = data['reasoning']
        self.intervention['action'] = data['action']
        self.intervention['status'] = data['status']
        for key, value in self.folder.items():
            if not value:
                self.add_error(key, f'le champ {key} ne peut pas être vide.')
        if not self.intervention['observation']:
            self.add_error(f'Veuillez rentrer au moins une observation.')
        self.create_folder = data['create_folder']

    def clean(self):
        if getattr(self, "user", False):
            self.cleaned_data["member_owner"] = self.user
        if getattr(self, "organization", False):
            self.cleaned_data["organization_owner"] = self.organization
        if self.cleaned_data["create_folder"]:
            self.init_folder(self.cleaned_data)

    def save(self, commit=True):
            if not self.request.is_ajax() or self.request.POST.get('asyncUpdate') == 'True':
                instance = super().save(commit=commit)
            else:
                instance = super().save(commit=False)
            if self.cleaned_data["create_folder"]:
                self.folder['stuff'] = instance
                folder = RepairFolder.objects.create(**self.folder)
                self.intervention['folder'] = folder
                intervention = Intervention.objects.create(**self.intervention)
            return instance 

    def __init__(self, organization=None, user=None, visitor_user=None, event=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if event:
            self.event = event
        if organization:
            self.organization = organization
            self.fields['place'] = forms.ModelChoiceField(
                widget=autocomplete.ModelSelect2(url='place_autocomplete'),
                label="Localisation",
                queryset= Place.objects.all(),
                help_text="Où se trouve l'appareil ?",
            )
            self.fields['is_visible'] = forms.BooleanField(
                label="Cet appareil est-il visible du public ?",
                initial=False,
                help_text = "par exemple s'il est en vente",
                required = False
            )
        elif visitor_user:
            self.user = user
            del self.fields['action']
            del self.fields['reasoning']
            del self.fields['status']
            del self.fields['place']
        elif user:
            self.user = user 
            del self.fields['place']

    class Meta:
        model = Stuff
        fields = (
            "category",
            "create_folder",
            "create_device",
            "brand",
            "model",
            "picture",
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
            "place",
            "repair_date",
        )


