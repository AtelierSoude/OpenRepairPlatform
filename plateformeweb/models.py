from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
from address.models import AddressField
from users.models import CustomUser
from django.conf import settings


# -------------------------------------------------------------------------------

class Organization(models.Model):
    name = models.CharField(max_length=100, null=False,
                            blank=False,
                            verbose_name=_("Organization name"))
    active = models.BooleanField(verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.SmallIntegerField(
        choices=MEMBER_TYPES,
        default=VISITOR, )

    class Meta:
        unique_together = ('organization', 'member', 'role')


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
Organization.admins= OrganizationAdminstratorManager()

# -------------------------------------------------------------------------------

class Place(models.Model):
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
    description = models.TextField(verbose_name=_("Description"), null=False,
                                   default='')
    type = models.CharField(max_length=2, verbose_name=_('Type'),
                            choices=PLACE_TYPES, null=False, default=OTHER)
    # geolocation is provided by the AddressField
    address = AddressField(null=False, blank=False,
                           default="",
                           verbose_name=_("Postal address"))
    picture = models.ImageField(verbose_name=_('Image'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# -------------------------------------------------------------------------------

class EventType(models.Model):
    name = models.CharField(verbose_name=_("Event type"), max_length=100,
                            null=False,
                            blank=False, default="")


class Event(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=150,
                             null=False,
                             blank=False,
                             default="")
    type = models.ForeignKey(EventType, on_delete=models.DO_NOTHING)
    starts_at = models.DateTimeField(verbose_name=_("Start date and time"),
                                     null=False,
                                     blank=False,
                                     default=timezone.now)
    ends_at = models.DateTimeField(verbose_name=_("End date and time"),
                                   null=False,
                                   blank=False,
                                   default=timezone.now)
    # TODO put organizers and participants in the same through table, with an
    # extra status column
    attendees = models.ManyToManyField(
        CustomUser, related_name='attendee_user', verbose_name=_('Attendees'))
    organizers = models.ManyToManyField(
        CustomUser, related_name='organizer_user', verbose_name=_('Organizers'))
    location = models.ManyToManyField(Place)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
