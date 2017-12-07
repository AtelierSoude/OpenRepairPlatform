from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
from address.models import AddressField
from users.models import CustomUser


class Organization(models.Model):
    name = models.CharField(max_length=100, null=False,
                            blank=False,
                            verbose_name=_("Organization name"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrganizationMember(models.Model):
    VISITOR = 0
    MEMBER = 10
    REPAIRMAN = 20
    ADMIN = 30
    MEMBER_TYPES = (
        (VISITOR, _('Visitor')),
        (MEMBER, _('Member')),
        (REPAIRMAN, _('Repairman')),
        (ADMIN, _('Admin')),
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.SmallIntegerField(
        choices=MEMBER_TYPES,
        default=VISITOR,
    )

    class Meta:
        unique_together = ('organization', 'member', 'role')


class Place(models.Model):
    name = models.CharField(max_length=100, null=False,
                              blank=False,
                              verbose_name=_("Place name"))
    address = AddressField(null=False, blank=False,
                             default="",
                             verbose_name=_("Place postal address"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EventType(models.Model):
    name = models.CharField(verbose_name=_("Event type"), max_length=100,
                            null=False,
                            blank=False, default="")


class Event(models.Model):
    title = models.CharField(verbose_name=_("Event title"), max_length=150,
                             null=False,
                             blank=False,
                             default="")
    date = models.DateTimeField(verbose_name=_("Event date"), null=False,
                                blank=False,
                                default=timezone.now)
    type = models.ForeignKey(EventType, on_delete=models.DO_NOTHING)
    # TODO put organizers and participants in the same through table, with an
    # extra status column
    participants = models.ManyToManyField(CustomUser, related_name='participant_user')
    organizers = models.ManyToManyField(CustomUser, related_name='organizer_user')
    location = models.ManyToManyField(Place)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
