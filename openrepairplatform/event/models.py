from datetime import date, datetime, timedelta

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from openrepairplatform.fields import CleanHTMLField

from openrepairplatform.location.models import Place
from openrepairplatform.user.models import CustomUser, Organization, Fee
from openrepairplatform.utils import get_future_published_events, validate_image
from openrepairplatform.inventory.models import Stuff


class Condition(models.Model):
    name = models.CharField(verbose_name=_("Condition Type"), max_length=100)
    description = models.CharField(
        verbose_name=_("Condition description"), default="", max_length=300
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="conditions"
    )
    price = models.FloatField(verbose_name=_("Price"), default=5)
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse(
            "organization_page",
            kwargs={"orga_slug": self.organization.slug},
        )

    def __str__(self):
        if self.price > 0:
            return f"{self.name} - {self.price}€"
        return self.name


class ActivityCategory(models.Model):
    name = models.CharField(verbose_name=_("Activity type"), max_length=100)
    slug = models.SlugField(blank=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Activity(models.Model):
    name = models.CharField(verbose_name=_("Activity type"), max_length=100)
    category = models.ForeignKey(
        ActivityCategory,
        related_name="category",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    slug = models.SlugField(blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="activities"
    )
    description = CleanHTMLField(verbose_name=_("Activity description"), default="")
    picture = models.ImageField(
        verbose_name=_("Image"),
        upload_to="activities/",
        blank=True,
        null=True,
        validators=[validate_image],
    )
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("event:activity_detail", args=(self.pk, self.slug))

    def next_events(self):
        return get_future_published_events(self.events)[0:3]


class Event(models.Model):
    WEEKS = [
        (1, "Semaine 1"),
        (2, "Semaine 2"),
        (3, "Semaine 3"),
        (4, "Semaine 4"),
        (5, "Semaine 5"),
    ]
    DAYS = [
        ("MO", "Lundi"),
        ("TU", "Mardi"),
        ("WE", "Mercredi"),
        ("TH", "Jeudi"),
        ("FR", "Vendredi"),
        ("SA", "Samedi"),
        ("SU", "Dimanche"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="events"
    )
    conditions = models.ManyToManyField(
        Condition,
        related_name="events",
        verbose_name=_("Conditions"),
        blank=True,
    )
    published = models.BooleanField(verbose_name=_("Published"), default=False)
    publish_at = models.DateTimeField(
        verbose_name=_("Publication date and time"), default=timezone.now
    )
    activity = models.ForeignKey(
        Activity, on_delete=models.SET_NULL, null=True, related_name="events"
    )
    description = CleanHTMLField(
        verbose_name=_(
            "Description supplémentaire de l'événément "
            "(remplace la définition par défaut de l'activité)"
        ),
        blank=True,
    )
    collaborator = models.CharField(
        verbose_name=_("En association avec"), max_length=100, blank=True
    )
    external = models.BooleanField(
        verbose_name=_("Réservation externe au site ?"), default=False
    )
    external_url = models.URLField(
        max_length=200,
        verbose_name=_(
            "Lien vers un site externe. Pour la réservation externe "
            "(si activée) ou simplement pour info"
        ),
        blank=True,
    )
    slug = models.SlugField(blank=True)
    date = models.DateField(verbose_name=_("Jour"), default=date.today)
    starts_at = models.TimeField(verbose_name=_("Heure de début"), default=timezone.now)
    ends_at = models.TimeField(verbose_name=_("Heure de fin"))
    available_seats = models.PositiveIntegerField(
        verbose_name=_("Places disponibles"), default=0
    )
    registered = models.ManyToManyField(
        CustomUser,
        related_name="registered_events",
        verbose_name=_("Utilisateurs attendus"),
        blank=True,
    )
    presents = models.ManyToManyField(
        CustomUser,
        related_name="presents_events",
        verbose_name=_("Presents"),
        blank=True,
        through="Participation",
    )
    needed_organizers = models.PositiveIntegerField(
        verbose_name=_("Nombre d'animateurs attendus"), default=0
    )
    organizers = models.ManyToManyField(
        CustomUser,
        related_name="organizers_events",
        verbose_name=_("Organisateurs / animateurs "),
        blank=True,
    )
    location = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        related_name="events",
        verbose_name="Lieu",
    )
    allow_stuffs = models.BooleanField(
        verbose_name=_("Souhaitez-vous gérer des réparations ?"),
        default=False,
        blank=True,
        help_text=(
            "Les participants pourront déclarer leurs réparations "
            "lors de la réservation"
        ),
    )
    stuffs = models.ManyToManyField(
        Stuff,
        verbose_name=_("Objets attendus"),
        related_name="events",
        blank=True,
    )
    is_free = models.BooleanField(
        default=False, verbose_name=_("Pas de limite de place ?")
    )
    booking = models.BooleanField(
        default=True, verbose_name=_("Réservation interne au site ?")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.activity:
            slug = self.activity.name
        else:
            slug = "no activity type"
        self.slug = slugify(slug)
        return super().save(*args, kwargs)

    @property
    def remaining_seats(self):
        return self.available_seats - (self.registered.count() + self.presents.count())

    def date_interval_format(self):
        date = self.date.strftime("%A %d %B")
        starts_at_time = self.starts_at.strftime("%H:%M")
        ends_at_time = self.ends_at.strftime("%H:%M")

        # ex Lundi 01 Janvier 2018 de 20:01:12 à 22:01:12
        return f"{date} de {starts_at_time} à {ends_at_time}"

    def get_absolute_url(self):
        return reverse("event:detail", args=(self.pk, self.slug))

    @property
    def has_ended(self):
        ends = datetime.combine(
            self.date, self.ends_at, tzinfo=timezone.now().tzinfo
        ) + timedelta(hours=4)
        return ends < timezone.now()

    @property
    def has_started(self):
        starts = datetime.combine(
            self.date, self.starts_at, tzinfo=timezone.now().tzinfo
        ) - timedelta(hours=2)
        return starts < timezone.now()

    @classmethod
    def future_published_events(cls):
        return get_future_published_events(cls.objects)

    def __str__(self):
        if self.activity:
            activity_name = self.activity.name
        else:
            activity_name = "no activity type"
        full_title = "%s du %s" % (
            activity_name,
            self.date.strftime("%d %B"),
        )
        return full_title


class Participation(models.Model):
    PAYMENT_CASH = "1"
    PAYMENT_BANK = "2"
    PAYMENT_BANK_CHECK = "3"
    PAYMENT_CB = "4"
    PAYMENT_LOCAL_CASH = "5"
    PAYMENTS = (
        (PAYMENT_CASH, _("Espèces")),
        (PAYMENT_BANK, _("En ligne")),
        (PAYMENT_BANK_CHECK, _("Chèque")),
        (PAYMENT_CB, _("CB")),
        (PAYMENT_LOCAL_CASH, _("Monnaie locale")),
    )
    payment = models.CharField(
        max_length=1, choices=PAYMENTS, blank=True, default=PAYMENT_CASH
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="participations"
    )
    saved = models.BooleanField(default=False)
    amount = models.PositiveIntegerField(
        verbose_name=_("Montant payé"), default=0, blank=True
    )
    fee = models.OneToOneField(Fee, on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = (("user", "event"),)

    def __str__(self):
        return " Participation " + self.user.first_name + " " + str(self.event)

    def get_absolute_url(self):
        return reverse("event:detail", args=(self.event.pk, self.event.slug))
