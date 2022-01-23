import logging

import datetime
from datetime import date
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
        help_text=_("Designates whether the user can log into this admin site."),
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
        return "{0} {1}".format(self.first_name, self.last_name)

    @property
    def active_organizations(self):
        organizations = (
            self.active_organizations.all()
            .union(self.volunteer_organizations.all(), self.admin_organizations.all())
            .prefetch_related("organization")
        )
        return organizations

    def clean(self):
        super().clean()
        self.email = self.email.lower()


class Organization(models.Model):

    MEMBERSHIP_SYSTEMS = [
        (
            "date_year",
            "L'adhésion dure un an à partir de la date de la première contribution.",
        ),
        (
            "date_month",
            "L'adhésion dure un mois à partir de la date de la première contribution.",
        ),
        (
            "year",
            (
                "L'adhésion est pour l'année en cours et se renouvelle "
                "à chaque début d'année."
            ),
        ),
        ("month", "L'adhésion est mensuelle, elle se renouvelle chaque début de mois."),
    ]

    name = models.CharField(
        max_length=100, default="", verbose_name=_("Organization name")
    )
    description = CleanHTMLField(verbose_name=_("Activity description"), default="")
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
    slug = models.SlugField(default="", unique=True)
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
    membership_system = models.CharField(
        choices=MEMBERSHIP_SYSTEMS, default="date_year", max_length=10
    )
    membership_url = models.URLField(
        max_length=255, verbose_name="Lien d'adhésion en ligne", default="", blank=True
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
        (PAYMENT_LOCAL_CASH, _("Monnaie locale")),
    )
    payment = models.CharField(
        max_length=1, choices=PAYMENTS, blank=True, default=PAYMENT_CASH
    )
    event = models.ForeignKey(
        "event.Event", null=True, on_delete=models.SET_NULL, related_name="fees"
    )
    date = models.DateField(default=date.today)
    amount = models.PositiveIntegerField(default=0)
    membership = models.ForeignKey(
        "user.Membership",
        on_delete=models.SET_NULL,
        related_name="fees",
        null=True,
        blank=True,
        verbose_name="Liée à une adhésion",
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="fees"
    )

    def computed_membership_payment(self, membership):
        """
        When a fee is create, check if a membership is linked
        Update the membership first payment if the fee date is
        after the membership date limit.
        Computed the membership amount.
        """

        if membership:
            membership.update_first_payment()
            membership.computed_amount()
            membership.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.computed_membership_payment(self.membership)

    def delete(self, *args, **kwargs):
        membership = self.membership
        super().delete(*args, **kwargs)
        self.computed_membership_payment(membership)

    def __str__(self):
        return f"{self.date}-{self.user}-{self.organization}-{self.amount}"

    class Meta:
        ordering = ["-date"]


class MembershipManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(disabled=False)


class DisabledMembershipManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(disabled=True)


class Membership(models.Model):

    objects = MembershipManager()
    disableds = DisabledMembershipManager()

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="memberships"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    first_payment = models.DateField(default=date.today)
    amount = models.PositiveIntegerField(
        verbose_name=_("Amount paid"), default=0, blank=True
    )
    history = HistoricalRecords()
    disabled = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.user}-{self.organization}"

    def update_first_payment(self):
        """
        If a new fee linked to current membership is add after the date limit
        Then is a new cycle of membership, so the first_payment field is
        updated with this fee date. If there is'nt fees, first_payment is today.
        """
        last_fee = self.fees.first()
        if last_fee:
            if last_fee.date > self.date_limit:
                self.first_payment = last_fee.date
        else:
            self.first_payment = date.today()

    def computed_amount(self):
        """
        The current amount is the sum of fees between the first payment date
        And the date limit.
        """

        fees = self.fees.filter(date__gte=self.first_payment, date__lte=self.date_limit)
        self.amount = sum(fee.amount for fee in fees)

    @property
    def date_limit(self):
        """
        Determines date limit according to the membership system.
        """
        membership_system = self.organization.membership_system
        start_date = self.first_payment
        if membership_system == "date_year":
            # Date limit is exactly one year after first payment.
            return start_date + relativedelta(years=1)
        if membership_system == "date_month":
            # Date limit is exactly one month after first payment.
            return start_date + relativedelta(months=1)
        if membership_system == "year":
            # Date limit is the first day of the year after the first payment.
            return datetime.date(day=1, month=1, year=(start_date.year + 1))
        if membership_system == "month":
            # Date limit is the first day of the month after the first payment.
            return datetime.date(
                day=1, month=(start_date.month + 1), year=start_date.year
            )

    @property
    def has_expired(self):
        """
        Check if the current day if after date limit.
        """
        return timezone.now().date() > self.date_limit

    @property
    def current_contribution(self):
        if self.has_expired:
            self.amount = 0
            self.save()
        return self.amount

    class Meta:
        unique_together = (("user", "organization"),)
