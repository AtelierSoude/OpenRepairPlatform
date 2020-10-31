import logging

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords
from openrepairplatform.fields import CleanHTMLField

from openrepairplatform.utils import validate_image


logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_MALE = "m"
    GENDER_FEMALE = "f"
    GENDER_OTHER = "n"
    GENDERS = (
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
        (GENDER_OTHER, _("Other")),
    )

    email = models.EmailField(_("email address"), max_length=254, unique=True)
    first_name = models.CharField(_("first name"), max_length=30, default="")
    last_name = models.CharField(_("last name"), max_length=30, default="")
    street_address = models.CharField(
        verbose_name=_("street address"), max_length=255, default="-"
    )
    phone_number = models.CharField(
        _("phone number"), max_length=10, blank=True, default="-"
    )
    birth_date = models.DateField(_("date of birth"), blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=GENDERS, blank=True, default=GENDER_OTHER
    )
    avatar_img = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to="media/avatar/",
        null=True,
        blank=True,
    )

    username = ""

    bio = CleanHTMLField(_("bio"), blank=True, default="")

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    is_visible = models.BooleanField(
        _("Profile visible"),
        default=False,
        help_text=_("Should people be able to see your profile?"),
    )
    history = HistoricalRecords()

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def get_organizations(self):
        return self.member_organizations.all().union(
            self.visitor_organizations.all(),
            self.active_organizations.all(),
            self.volunteer_organizations.all(),
            self.admin_organizations.all(),
        )

    def get_absolute_url(self):
        return reverse("user:user_detail", kwargs={"pk": self.pk})

    def __str__(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    @property
    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)
        
class Organization(models.Model):
    name = models.CharField(
        max_length=100, default="", verbose_name=_("Organization name")
    )
    description = CleanHTMLField(
        verbose_name=_("Activity description"), default=""
    )
    email = models.EmailField(
        max_length=200, verbose_name=_("Organization mail address"), blank=True
    )
    website = models.URLField(
        max_length=200, verbose_name=_("Organization website mail"), blank=True
    )
    phone_number = models.CharField(
        _("Organization phone number"), max_length=10, blank=True, default="-"
    )
    picture = models.ImageField(
        verbose_name=_("Image"),
        upload_to="organizations/",
        validators=[validate_image],
    )
    slug = models.SlugField(
        default="",
        unique=True
    )
    visitors = models.ManyToManyField(
        CustomUser, related_name="visitor_organizations", blank=True
    )
    members = models.ManyToManyField(
        CustomUser,
        related_name="member_organizations",
        blank=True,
        through="Membership",
    )
    volunteers = models.ManyToManyField(
        CustomUser, related_name="volunteer_organizations", blank=True
    )
    actives = models.ManyToManyField(
        CustomUser, related_name="active_organizations", blank=True
    )
    admins = models.ManyToManyField(
        CustomUser, related_name="admin_organizations", blank=True
    )
    min_fee = models.PositiveIntegerField(
        verbose_name=_("Minimum contribution"), default=0, blank=True
    )
    advised_fee = models.PositiveIntegerField(
        verbose_name=_("Advised contribution"), default=0, blank=True
    )
    fee_description = models.TextField(
        verbose_name=_("Explain how the contribution system works"),
        default="",
        blank=True,
    )
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("organization_page", kwargs={"orga_slug": self.slug})

    @property
    def actives_or_more(self):
        return self.actives.union(self.admins.all())

    def __str__(self):
        return self.name


class Fee(models.Model):
    PAYMENT_CASH = "1"
    PAYMENT_BANK = "2"
    PAYMENT_BANK_CHECK = "3"
    PAYMENT_CB = "4"
    PAYMENT_LOCAL_CASH = "5"
    PAYMENTS = (
        (PAYMENT_CASH, _("Espèces")),
        (PAYMENT_BANK, _("Online")),
        (PAYMENT_BANK_CHECK, _("Chèque")),
        (PAYMENT_CB, _("CB")),
        (PAYMENT_LOCAL_CASH, _("Gonettes")),
    )
    payment = models.CharField(
        max_length=1, choices=PAYMENTS, blank=True, default=PAYMENT_CASH
    )
    date = models.DateField(default=timezone.now)
    amount = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="fees"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="fees"
    )

    def __str__(self):
        return f"{self.date}-{self.user}-{self.organization}-{self.amount}"
    
    class Meta:
        ordering = ['-date']


class Membership(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="memberships"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    fee = models.OneToOneField(
        Fee, on_delete=models.SET_NULL, null=True, blank=True
    )
    first_payment = models.DateTimeField(default=timezone.now)
    amount = models.PositiveIntegerField(
        verbose_name=_("Amount paid"), default=0, blank=True
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user}-{self.organization}"

    @property
    def current_contribution(self):
        if self.first_payment < timezone.now() - relativedelta(years=1):
            self.amount = 0
            self.save()
        return self.amount

    class Meta:
        unique_together = (("user", "organization"),)
