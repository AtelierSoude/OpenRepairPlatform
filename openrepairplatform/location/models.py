from django.contrib.gis.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from openrepairplatform.fields import CleanHTMLField

from openrepairplatform.user.models import Organization
from openrepairplatform.utils import validate_image, get_future_published_events


class Place(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="places",
    )
    description = CleanHTMLField(default="", verbose_name=_("Place description"))
    category = models.CharField(max_length=100, default="Other")
    slug = models.SlugField(default="", blank=True)
    address = models.CharField(max_length=255, verbose_name=_("street address"))
    location = models.PointField(null=True, blank=True, geography=True)
    zipcode = models.CharField(default="", blank=True, max_length=5)
    picture = models.ImageField(
        upload_to="places/",
        blank=True,
        null=True,
        validators=[validate_image],
        verbose_name=_("Image"),
    )
    is_visible = models.BooleanField(
        _("Lieu principal"),
        null=True,
        default=False,
        help_text=_(
            "Est-ce que ce lieu est un lieu de votre organisation ? "
            "Si vous cochez oui, il sera visible sur votre page"
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("location:detail", args=(self.pk, self.slug))

    def future_published_events(self):
        return get_future_published_events(self.events)

    @property
    def latitude(self):
        if self.location:
            return self.location.y
        return None

    @property
    def longitude(self):
        if self.location:
            return self.location.x
        return None

    def __str__(self):
        return self.name + ", " + str(self.address)
