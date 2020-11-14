from django.db import models
from treebeard.mp_tree import MP_Node
from django.urls import reverse
from simple_history.models import HistoricalRecords
from openrepairplatform.fields import CleanHTMLField
from openrepairplatform.user.models import Organization

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
    name = models.CharField(max_length=150)

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
        (BROKEN, "Broken"),
        (WORKING, "Working"),
        (DISASSEMBLED, "Disassembled"),
        (FIXING, "Fixing"),
        (THROWN, "Thrown"),
    ]
    device = models.ForeignKey(
        "inventory.device",
        related_name="device",
        null=True,
        blank=True,
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
        on_delete=models.SET_NULL
    )
    added_date = models.DateField(
        auto_now_add=True,
    )
    state = models.CharField(
        max_length=1,
        choices=STATES,
        default=BROKEN
    )
    information = CleanHTMLField(
        null=True,
        blank=True
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
        upload_to=None,
        height_field=None,
        width_field=None,
        max_length=None,
        null=True,
        blank=True
    )
    defect = models.ForeignKey(
        "inventory.Defect", 
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.category}-{self.brand}-{self.model}"


class Defect(models.Model):
    pass

# NOTE: Comments below are present to help modelling the repair process and objects
# and list fields that should be in the classes

# Observation as done by the owner of the device (either initially or during repair or diagnosis)
# Implement a string e.g. "No power on the output of the switch even when on"
# or "After house was hit by a lightning, the dishwasher would not start anymore" as the initial observation
# Maybe add a list of strings that would be hashtags for indexing e.g. "#NoPower", "#Switch", "#PowerSupply"
# Maybe link to a user or fixer to indicate who made the Observation
class Observation(models.Model):
    name = models.CharField(max_length=150, default="")
    
    def __str__(self):
        return self.name
    
# A reasoning that takes place during repair or diagnosis
# Implement a string that would detail fixer reasoning from an Observation and leading to an Action
# e.g. "There is no power at the output pin of the switch even when the switch is on. The switch must be defective"
# Maybe link to a user or fixer to indicate who made the Reasoning
class Reasoning(models.Model):
    name = models.CharField(max_length=150, default="")
    
    def __str__(self):
        return self.name

# An action taken by the fixer during repair or diagnosis
# Could be implemented as a verb (from a list that must be easily maintained) associated to a Part
# e.g. Replace capacitor C3
# or Resolder Wire Red wire
# Maybe link to a user or fixer to indicate who took the Action
class Action(models.Model):
    name = models.CharField(max_length=150, default="")
    
    def __str__(self):
        return self.name
    
# Implements a status (be it the initial one or the one resulting from an Action being taken)
# Take it from the Stuff class above
class Status(models.Model):
    name = models.CharField(max_length=150, default="")
    
    def __str__(self):
        return self.name


# Implements a step in diagnosis or repair.
# This consists of:
# 1. An Observation
# 2. An optional Reasoning (from the observation) leading to an optional Action
# 3. An optional Action
# 4. A resulting status after Action is taken
# The initial (first) DiagnosisOrRepairStep instance would contain 
# . the initial Observation and
# . the intial status (probably "broken" unless the user comes for an enhancement or minor issue)
class DiagnosisOrRepairStep(models.Model):
    folder = models.ForeignKey("inventory.RepairFolder", related_name="steps", on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey("event.Event", on_delete=models.SET_NULL, null=True, blank=True)
    repair_date = models.DateField(null=True, blank=True)
    observation = models.ForeignKey("inventory.Observation", on_delete=models.SET_NULL, null=True, blank=True)
    reasoning = models.ForeignKey("inventory.Reasoning", on_delete=models.SET_NULL, null=True, blank=True)
    action = models.ForeignKey("inventory.Action", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey("inventory.Status", on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def date(self):
        if self.event:
            return self.event.date
        return self.repair_date
    
    def __str__(self):
        return f"actions réalisées sur {self.folder} le {self.repair_date}"

class RepairFolder(models.Model):
    stuff = models.ForeignKey("inventory.Stuff", related_name="folders", on_delete=models.SET_NULL, null=True, blank=True)
    ongoing = models.BooleanField(default=True)
    open_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"dossier {self.stuff}-{self.open_date}"
 
