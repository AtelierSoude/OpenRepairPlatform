import os
from datetime import date

from uuid import uuid4
from django.db import models
from treebeard.mp_tree import MP_Node
from django.urls import reverse
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
from django_better_admin_arrayfield.models.fields import ArrayField
from openrepairplatform.fields import CleanHTMLField
from openrepairplatform.user.models import Organization
from openrepairplatform.utils import validate_image
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    name = models.CharField(max_length=100)
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

    node_order_by = ["name"]

    def __str__(self):
        return self.name


class Stuff(models.Model):
    BROKEN = "B"
    WORKING = "W"
    DISASSEMBLED = "D"
    FIXING = "F"
    FIXED = "O"
    THROWN = "T"
    PARTIAL = "P"
    STATES = [
        (BROKEN, "En panne"),
        (WORKING, "Fonctionnel"),
        (DISASSEMBLED, "Désassemblé"),
        (FIXING, "En réparation"),
        (FIXED, "Réparé"),
        (THROWN, "Evaporé"),
        (PARTIAL, "Partiel"),
    ]
    device = models.ForeignKey(
        "inventory.device",
        related_name="stuffs",
        null=True,
        blank=True,
        verbose_name=_("Type d'appareil"),
        on_delete=models.SET_NULL,
    )
    member_owner = models.ForeignKey(
        "user.CustomUser",
        related_name="user_stuffs",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    organization_owner = models.ForeignKey(
        "user.Organization",
        related_name="organization_stuffs",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    subpart = models.ForeignKey(
        "inventory.Stuff",
        related_name="subparts",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    place = models.ForeignKey(
        "location.Place",
        null=True,
        blank=True,
        verbose_name=_("Localisation"),
        help_text="Où se trouve l'objet ?",
        on_delete=models.SET_NULL,
    )
    added_date = models.DateField(
        auto_now_add=True,
    )
    state = models.CharField(
        max_length=1, choices=STATES, default=BROKEN, verbose_name=_("Etat")
    )
    information = CleanHTMLField(
        null=True,
        blank=True,
        verbose_name=_("Information optionnelles sur cet objet"),
        help_text=(
            "D'où vient-il, a t'il des caractéristiques spéciales... "
            "bref, tout ce qui peut le décrire",
        ),
    )
    is_visible = models.BooleanField(
        _("Objet visible"),
        default=False,
        help_text=_(
            "Cet objet est-il visible du public ? (par exemple, s'il est mis en vente)"
        ),
    )
    history = HistoricalRecords()

    @property
    def owner(self):
        if self.member_owner or self.organization_owner:
            return self.member_owner or self.organization_owner
        return None

    def set_owner(self, new_owner):
        if isinstance(new_owner, Organization):
            self.organization_owner = new_owner
            self.member_owner = None
        else:
            self.member_owner = new_owner
        self.save()

    def get_absolute_url(self):
        return reverse("inventory:stuff_view", kwargs={"stuff_pk": self.pk})

    def get_url_qrcode(self):
        domain = os.environ.get("DOMAINDNS", "reparons.org")
        return f"https://{domain}/inventory/stuff/{self.pk}/"
        # return self.get_absolute_url()

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
    model = models.CharField(max_length=200, null=True, blank=True)
    description = CleanHTMLField(null=True, blank=True)
    picture = models.ImageField(
        upload_to="devices/",
        blank=True,
        null=True,
        validators=[validate_image],
        verbose_name=_("Image"),
    )
    links = ArrayField(models.URLField(), blank=True, null=True)
    slug = models.SlugField(
        default="",
        unique=True,
        blank=True,
    )
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.slug = "-".join(
            (slugify(self.category), slugify(self.brand), slugify(self.model))
        )
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("inventory:device_view", args=(self.pk, self.slug))

    def __str__(self):
        return f"{self.category} {self.brand} {self.model}"


class Observation(models.Model):
    name = models.CharField(max_length=250, default="")

    def __str__(self):
        return self.name


class Reasoning(models.Model):
    name = models.CharField(max_length=250, default="")
    verbose_name = _("raisonnement")

    def __str__(self):
        return self.name


class Action(models.Model):
    name = models.CharField(max_length=250, default="")

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=250, default="")

    def __str__(self):
        return self.name


class Intervention(models.Model):
    folder = models.ForeignKey(
        "inventory.RepairFolder",
        related_name="interventions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    event = models.ForeignKey(
        "event.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    repair_date = models.DateField(
        null=True,
        blank=True,
        default=date.today,
    )
    observation = models.ForeignKey(
        "inventory.Observation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Quel est (ou était) le problème ?",
    )
    reasoning = models.ForeignKey(
        "inventory.Reasoning",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Quel en est (ou serait) la cause ?",
    )
    action = models.ForeignKey(
        "inventory.Action",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Qu'avez-vous fait ?",
    )
    status = models.ForeignKey(
        "inventory.Status",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Quel est le résultat de l'action ?",
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
        blank=True,
    )
    ongoing = models.BooleanField(default=True)
    open_date = models.DateField(
        null=True,
        blank=True,
        default=date.today,
    )

    def __str__(self):
        return f"dossier {self.stuff}-{self.open_date}"


class ThermalPrinter(models.Model):
    name = models.CharField(max_length=250)
    # Liste des profils ici : https://python-escpos.readthedocs.io/en/latest/printer_profiles/available-profiles.html
    profile = models.CharField(max_length=250, blank=True, null=True, help_text="Profil de l'imprimante thermique. Liste ici : liste dispo ici : https://python-escpos.readthedocs.io/en/latest/printer_profiles/available-profiles.html")
    ip = models.GenericIPAddressField()
    port = models.IntegerField(blank=True, null=True)
    api_key = models.CharField(max_length=250, default=uuid4().hex)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name