from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords
from ateliersoude.fields import CleanHTMLField


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
    member_owner = models.ForeignKey(
        "user.CustomUser",
        related_name="stock",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    organization_owner = models.ForeignKey(
        "user.Organization",
        related_name="stock",
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
        related_name="stock",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    added_date = models.DateField(
        auto_now_add=True,
    )
    state = models.CharField(
        max_length=1,
        choices=STATES,
        default=BROKEN
    )
    history = HistoricalRecords()

    @property
    def owner(self):
        if self.member_owner or self.organization_owner:
            return self.member_owner or self.organization_owner

    def set_owner(self, new_owner):
        if isinstance(new_owner, "user.Organization"):
            self.organization_owner = new_owner
            self.member_owner = None
        else:
            self.member_owner = new_owner

    def __str__(self):
        return self.state + str(self.owner)


class RepairFolder(models.Model):
    Stuff = models.ForeignKey("inventory.Stuff", on_delete=models.CASCADE)
    ongoing = models.BooleanField(default=True)


class Repair(models.Model):
    repair_folder = models.ForeignKey(
        "inventory.RepairFolder",
        on_delete=models.CASCADE
    )
    fixer = models.ManyToManyField("user.CustomUser",)
    actions = models.ManyToManyField("inventory.Action",)
    event = models.ForeignKey("event.Event", on_delete=models.CASCADE)
    repair_date = models.DateField(null=True, blank=True)

    @property
    def date(self):
        if self.event:
            return self.event.date
        return self.repair_date


class Device(Stuff):
    category = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    description = CleanHTMLField()
    picture = models.ImageField(
        upload_to=None,
        height_field=None,
        width_field=None,
        max_length=None
    )
    defect = models.ForeignKey("inventory.Defect", on_delete=models.CASCADE)


class Part(Stuff):
    pass


class Tool(Stuff):
    pass


class Defect(models.Model):

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("defect_detail", kwargs={"pk": self.pk})


class Action(models.Model):

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("action_detail", kwargs={"pk": self.pk})
