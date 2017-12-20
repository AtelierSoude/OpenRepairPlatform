from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
from address.models import AddressField
from users.models import CustomUser
from django.conf import settings
from autoslug import AutoSlugField


# ------------------------------------------------------------------------------

class Organization(models.Model):
    name = models.CharField(max_length=100, null=False,
                            blank=False,
                            verbose_name=_("Organization name"))
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(verbose_name=_('Active'))
    slug = AutoSlugField(populate_from='name', unique=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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


# --- admin ---
class OrganizationAdminstratorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=OrganizationPerson.ADMIN)


class OrganizationAdministrator(OrganizationPerson):
    objects = OrganizationAdminstratorManager()

    class Meta:
        proxy = True


# extend the Organization with convenience methods

Organization.visitors = OrganizationVisitorManager()
Organization.members = OrganizationMemberManager()
Organization.volunteers = OrganizationVolunteerManager()
Organization.admins = OrganizationAdminstratorManager()


# ------------------------------------------------------------------------------


class Place(models.Model):
    # TODO put these definitions in a DB table -more flexible- or in code?
    REPAIRCAFE = 'rc'
    SCHOOL = 'sc'
    OTHER = 'ot'
    PLACE_TYPES = (
        (REPAIRCAFE, _("Repair café")),
        (SCHOOL, _("School")),
    )

    name = models.CharField(max_length=100, null=False,
                            blank=False,
                            verbose_name=_("Name"))
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                     null=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    description = models.TextField(verbose_name=_("Description"), null=False,
                                   default='')
    type = models.CharField(max_length=2, verbose_name=_('Type'),
                            choices=PLACE_TYPES, null=False, default=OTHER)
    slug = AutoSlugField(populate_from='name', default='', unique=True)
    # geolocation is provided by the AddressField
    address = AddressField(null=False, blank=False,
                           default="",
                           verbose_name=_("Postal address"))
    picture = models.ImageField(verbose_name=_('Image'), upload_to='places/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return " ".join([self.name, '-', self.address.locality.__str__() or ''])


# ------------------------------------------------------------------------------


# TODO put these definitions in a DB table -more flexible- or in code?
class EventType(models.Model):
    name = models.CharField(verbose_name=_("Event type"), max_length=100,
                            null=False,
                            blank=False, default="")

    def __str__(self):
        return self.name


# ------------------------------------------------------------------------------

class Event(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=150,
                             null=False,
                             blank=False,
                             default="")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                     null=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    published = models.BooleanField(verbose_name=_("Published"), null=False,
                                    default=False)
    publish_at = models.DateTimeField(
        verbose_name=_("Publication date and time"),
        null=False,
        blank=False,
        default=timezone.now)
    type = models.ForeignKey(EventType, on_delete=models.DO_NOTHING)
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
    # TODO put organizers and participants in the same through table, with an
    # extra status column, or not?
    attendees = models.ManyToManyField(
        CustomUser, related_name='attendee_user', verbose_name=_('Attendees'),
        blank=True)
    organizers = models.ManyToManyField(
        CustomUser, related_name='organizer_user', verbose_name=_('Organizers'),
        blank=True)
    location = models.ForeignKey(Place, on_delete=models.DO_NOTHING, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PublishedEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True).filter(
            publish_at__lte=timezone.now())


class PublishedEvent(Event):
    objects = PublishedEventManager()

    class Meta:
        proxy = True

# ------------------------------------------------------------------------------
