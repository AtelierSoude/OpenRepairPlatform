from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from ateliersoude.fields import CleanHTMLField

from ateliersoude.user.models import Organization
from ateliersoude.utils import validate_image, get_future_published_events


class Place(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="places",
    )
    description = CleanHTMLField(
        default="", verbose_name=_("Place description")
    )
    category = models.CharField(max_length=100, default="Other")
    slug = models.SlugField(default="", blank=True)
    address = models.CharField(
        max_length=255, verbose_name=_("street address")
    )
    longitude = models.FloatField()
    latitude = models.FloatField()
    picture = models.ImageField(
        upload_to="places/",
        blank=True,
        null=True,
        validators=[validate_image],
        verbose_name=_("Image"),
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

    def __str__(self):
        return self.name
