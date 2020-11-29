from django.db import models
from treebeard.mp_tree import MP_Node
from django.urls import reverse
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
from openrepairplatform.fields import CleanHTMLField
from openrepairplatform.user.models import Organization
from openrepairplatform.utils import validate_image
from django.utils.translation import ugettext_lazy as _

class Brand(models.Model):
    name = models.CharField(max_length=50)
    picture = models.ImageField(
        upload_to=None,
        height_field=None,
        width_field=None,
        max_length=None,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

class Category(MP_Node):
    name = models.CharField(max_length=350)

    node_order_by = ['name']
    
    def __str__(self):
        return self.name

class Stuff(models.Model):
    BROKEN = "B"
    WORKING = "W"
    DISASSEMBLED = "D"
    FIXING = "F"
    THROWN = "T"
    STATES = [
        (BROKEN, "En panne"),
        (WORKING, "Fonctionnel"),
        (DISASSEMBLED, "Désassemblé"),
        (FIXING, "Réparé"),
        (THROWN, "Evaporé"),
    ]
    device = models.ForeignKey(
        "inventory.device",
        related_name="stuffs",
        null=True,
        blank=True,
        verbose_name=_("Type d'appareil"),
        on_delete=models.SET_NULL
    )
    member_owner = models.ForeignKey(
        "user.CustomUser",
        related_name="member_owner",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    organization_owner = models.ForeignKey(
        "user.Organization",
        related_name="organization_owner",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    subpart = models.ForeignKey(
        "inventory.Stuff",
        related_name="subparts",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    place = models.ForeignKey(
        "location.Place",
        related_name="place",
        null=True,
        blank=True,
        verbose_name=_("Localisation"),
        help_text="Où se trouve l'appareil ?",
        on_delete=models.SET_NULL
    )
    added_date = models.DateField(
        auto_now_add=True,
    )
    state = models.CharField(
        max_length=1,
        choices=STATES,
        default=BROKEN,
        verbose_name=_("Etat")
    )
    information = CleanHTMLField(
        null=True,
        blank=True,
        verbose_name=_("Information optionnelles sur cet appareil"),
        help_text="D'où vient-il, a t'il des caractéristiques spéciales... bref, tout ce qui peut le décrire",
    )
    history = HistoricalRecords()

    @property
    def owner(self):
        if self.member_owner or self.organization_owner:
            return self.member_owner or self.organization_owner

    def set_owner(self, new_owner):
        if isinstance(new_owner, Organization):
            self.organization_owner = new_owner
            self.member_owner = None
        else:
            self.member_owner = new_owner
        self.save()

    def get_absolute_url(self):
        return reverse(
            "inventory:stuff_view", kwargs={'stuff_pk': self.pk}
        )
    
    def __str__(self):
        return f"{self.device} - #{self.id}"


class Device(models.Model):
    category = models.ForeignKey(
        "inventory.Category", 
        on_delete=models.SET_NULL,  
        blank=True,
        null=True,
    )
    brand = models.ForeignKey(
        "inventory.Brand",  
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    model = models.CharField(
        max_length=50, 
        null=True,
        blank=True
    )
    description = CleanHTMLField(
        null=True,
        blank=True
    )
    picture = models.ImageField(
        upload_to="devices/", 
        blank=True, 
        null=True,
        validators=[validate_image],
        verbose_name=_("Image"),
    )
    slug = models.SlugField(
        default="",
        unique=True,
        blank=True,
    )
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.slug = '-'.join((slugify(self.category), slugify(self.brand), slugify(self.model)))
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("inventory:device_view", args=(self.pk, self.slug))

    def __str__(self):
        return f"{self.category}-{self.brand}-{self.model}"


class Observation(models.Model):
    name = models.CharField(max_length=150, default="")
    
    def __str__(self):
        return self.name
    

class Reasoning(models.Model):
    name = models.CharField(max_length=150, default="")
    verbose_name=_("raisonnement")

    def __str__(self):
        return self.name


class Action(models.Model):
    name = models.CharField(max_length=150, default="")
    
    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=150, default="")
    
    def __str__(self):
        return self.name


class Intervention(models.Model):
    folder = models.ForeignKey(
        "inventory.RepairFolder", 
        related_name="interventions", 
        on_delete=models.SET_NULL, null=True,
        blank=True
        )
    event = models.ForeignKey(
        "event.Event", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
        )
    repair_date = models.DateField(
        null=True, 
        blank=True
        )
    observation = models.ForeignKey(
        "inventory.Observation", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Quel est (ou était) le problème ?"
        )
    reasoning = models.ForeignKey(
        "inventory.Reasoning", 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        help_text="Quel en est (ou serait) la cause ?"
    )
    action = models.ForeignKey(
        "inventory.Action", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Qu'avez-vous fait ?"
    )
    status = models.ForeignKey(
        "inventory.Status", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Quel est le résultat de l'action ?"
    )

    @property
    def date(self):
        if self.event:
            return self.event.date
        return self.repair_date
    
    def __str__(self):
        return f"actions réalisées sur {self.folder} le {self.repair_date}"

class RepairFolder(models.Model):
    stuff = models.ForeignKey(
        "inventory.Stuff", 
        related_name="folders", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
        )
    ongoing = models.BooleanField(default=True)
    open_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"dossier {self.stuff}-{self.open_date}"
 
