from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
from django.urls import reverse
from address.models import AddressField
from users.models import CustomUser
from django.conf import settings
from autoslug import AutoSlugField
from django_markdown.models import MarkdownField
from easy_maps.widgets import AddressWithMapWidget
import locale
# ------------------------------------------------------------------------------

class Organization(models.Model):
    name = models.CharField(max_length=100, null=False,
                            blank=False,
                            verbose_name=_("Organization name"))
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    description = MarkdownField(verbose_name=_("Activity description"),
                            null=False,
                            blank=False, default="")
    picture = models.ImageField(verbose_name=_('Image'), upload_to='organizations/', null=True)
    active = models.BooleanField(verbose_name=_('Active'))
    slug = AutoSlugField(populate_from='name', unique=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organization_detail', args=(self.pk, self.slug,))

class OrganizationPerson(models.Model):
    VISITOR = 0
    MEMBER = 10
    VOLUNTEER = 20
    ADMIN = 30
    MEMBER_TYPES = (
        (VISITOR, _('Visitor')),
        (MEMBER, _('Member')),
        (VOLUNTEER, _('Volunteer')),
        (ADMIN, _('Admin')),
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, db_index=True)
    role = models.SmallIntegerField(
        choices=MEMBER_TYPES,
        default=VISITOR, )

    class Meta:
        unique_together = ('organization', 'user', 'role')


# --- visitor ---
class OrganizationVisitorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.VISITOR)


class OrganizationVisitor(OrganizationPerson):
    objects = OrganizationVisitorManager()

    class Meta:
        proxy = True


# --- member ---
class OrganizationMemberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.MEMBER)


class OrganizationMember(OrganizationPerson):
    objects = OrganizationMemberManager()

    class Meta:
        proxy = True


# --- volunteer ---
class Abilities(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False,
                            verbose_name=_("Abilities"))


class OrganizationVolunteerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.VOLUNTEER)


class OrganizationVolunteer(OrganizationPerson):
    abilities = models.ManyToManyField(Abilities)
    tagline = models.TextField(verbose_name=_('Tagline'))
    objects = OrganizationVolunteerManager()


# --- admin ---
class OrganizationAdminstratorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.ADMIN)


class OrganizationAdministrator(OrganizationPerson):
    objects = OrganizationAdminstratorManager()

    class Meta:
        proxy = True


# extend the Organization with convenience methods

def get_admins(self):
    queryset = OrganizationPerson.objects.filter(role=OrganizationPerson.ADMIN, organization=self)
    ret = []
    for query in queryset:
        ret += [query.user]
    return ret


def get_volunteers(self):
    queryset = OrganizationPerson.objects.filter(role=OrganizationPerson.VOLUNTEER, organization=self)
    ret = []
    for query in queryset:
        ret += [query.user]
    return ret


def get_members(self):
    queryset = OrganizationPerson.objects.filter(role=OrganizationPerson.MEMBER, organization=self)
    ret = []
    for query in queryset:
        ret += [query.user]
    return ret


def get_visitors(self):
    queryset = OrganizationPerson.objects.filter(role=OrganizationPerson.VISITOR, organization=self)
    ret = []
    for query in queryset:
        ret += [query.user]
    return ret


Organization.admins = get_admins
Organization.visitors = get_visitors
Organization.members = get_members
Organization.volunteers = get_volunteers


# ------------------------------------------------------------------------------

class PlaceType(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Type'),
                            null=False, blank=False )
    slug = AutoSlugField(populate_from='name', unique=True)

    def __str__(self):
        return self.slug

    def get_other_place():
        return PlaceType.get_or_create(name="Other")[0]

class Place(models.Model):
    name = models.CharField(max_length=100, null=False,
                            blank=False,
                            verbose_name=_("Name"))
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                     null=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    description = MarkdownField(verbose_name=_("Place description"),
                            null=False,
                            blank=False, default="")

    type = models.ForeignKey(PlaceType, verbose_name=_('Type'),
                             null=False,
                             on_delete=models.SET(PlaceType.get_other_place))

    slug = AutoSlugField(populate_from='name', default='', unique=True)
    # geolocation is provided by the AddressField
    address = AddressField(null=False, blank=False,
                           default="",
                           verbose_name=_("Postal address"))
    picture = models.ImageField(verbose_name=_('Image'), upload_to='places/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('place_detail', args=(self.pk, self.slug,))

    def __str__(self):
        return " ".join([self.name, '-', self.address.locality.__str__() or ''])

# ------------------------------------------------------------------------------

#Condition : mettre ailleurs, en test


class Condition(models.Model):
    name = models.CharField(verbose_name=_("Condition Type"), max_length=100,
                            null=False,
                            blank=False, default="")
    resume = models.CharField(verbose_name=_("Condition resume"), max_length=100,
                            null=False,
                            blank=False, default="")
    description = models.TextField(verbose_name=_("Condition description"),
                            null=False,
                            blank=False, default="")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                     null=True)
    price = models.IntegerField(verbose_name=_('Price'),
                                          null=False, blank=True, default=5)
    def __str__(self):
        return self.name

# EventType is an activity
class Activity(models.Model):
    name = models.CharField(verbose_name=_("Activity type"), max_length=100,
                            null=False,
                            blank=False, default="")
    slug = AutoSlugField(populate_from=('name'), default='',
                         unique=False)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    description = MarkdownField(verbose_name=_("Activity description"),
                            null=False,
                            blank=False, default="")
    picture = models.ImageField(verbose_name=_('Image'), upload_to='activities/')

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('activity_detail', args=(self.pk, self.slug,))





# ------------------------------------------------------------------------------

class Event(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=150,
                             null=True,
                             blank=True,
                             default="")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                     null=False)
    condition = models.ManyToManyField(
    Condition, related_name='condition_activity', verbose_name=_('Conditions'),
        blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    published = models.BooleanField(verbose_name=_("Published"), null=False,
                                    default=False)
    publish_at = models.DateTimeField(
        verbose_name=_("Publication date and time"),
        null=False,
        blank=False,
        default=timezone.now)
    type = models.ForeignKey(Activity, on_delete=models.DO_NOTHING)
    slug = AutoSlugField(populate_from=('title'), default='',
                         unique=True)
    starts_at = models.DateTimeField(verbose_name=_("Start date and time"),
                                     null=False,
                                     blank=False,
                                     default=timezone.now)
    ends_at = models.DateTimeField(verbose_name=_("End date and time"),
                                   null=False,
                                   blank=False,
                                   default=timezone.now)
    available_seats = models.IntegerField(verbose_name=_('Available seats'),
                                          null=False, blank=True, default=0)
    attendees = models.ManyToManyField(
        CustomUser, related_name='attendee_user', verbose_name=_('Attendees'),
        blank=True)
    presents = models.ManyToManyField(
        CustomUser, related_name='present_user', verbose_name=_('Presents'),
        blank=True)
    organizers = models.ManyToManyField(
        CustomUser, related_name='organizer_user', verbose_name=_('Organizers'),
        blank=True)
    location = models.ForeignKey(Place, on_delete=models.DO_NOTHING, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def date_interval_format(self):
        locale.setlocale(locale.LC_ALL, 'fr_FR')
        starts_at_date = self.starts_at.date().strftime("%A %d %B %Y")
        starts_at_time = self.starts_at.time().strftime("%X")
        ends_at_time = self.ends_at.time().strftime("%X")

        # ex Lundi 01 Janvier 2018 de 20:01:12 à 22:01:12
        string = starts_at_date
        string += " de "
        string += starts_at_time
        string += " à "
        string += ends_at_time
        return string

    def get_absolute_url(self):
        return reverse('event_detail', args=(self.pk, self.slug,))



class PublishedEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True).filter(
            publish_at__lte=timezone.now())


class PublishedEvent(Event):
    objects = PublishedEventManager()

    class Meta:
        proxy = True


# ------------------------------------------------------------------------------
