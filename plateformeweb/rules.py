import rules
import logging

from .models import *

logger = logging.getLogger(__name__)


class AppError(Exception):
    pass


# PREDICATES

def is_org_whatever_for_object(user, obj, org_member_class):
    try:
        if isinstance(obj, Organization):
            org = obj
        elif hasattr(obj, 'organization'):
            org = obj.organization
        else:
            raise AppError(
                "object is neither an organization, nor has an organization "
                "field",
                obj)
        if org_member_class.objects.filter(user=user).filter(
                organization=org).exists():
            return True
        return False

    # TODO error handling
    except AppError as e:
        logger.error(e)
        raise


@rules.predicate
def is_org_admin_for_object(user, obj):
    return is_org_whatever_for_object(user, obj, OrganizationAdministrator)


@rules.predicate
def is_org_volunteer_for_object(user, obj):
    return is_org_whatever_for_object(user, obj, OrganizationVolunteer)


@rules.predicate
def is_org_member_for_object(user, obj):
    return is_org_whatever_for_object(user, obj, OrganizationMember)


@rules.predicate
def is_owner_for_object(user, obj):
    if not hasattr(obj, 'owner'):
        raise AppError("object doesn't have an 'owner' field", obj)
    return obj.owner == user


# RULES

# organizations
rules.add_perm('plateformeweb.create_organization',
               rules.is_staff | rules.is_superuser)
rules.add_perm('plateformeweb.edit_organization',
               is_org_admin_for_object | rules.is_staff | rules.is_superuser)

#activities
rules.add_perm('plateformeweb.create_activity',
               is_org_admin_for_object | rules.is_staff | rules.is_superuser)
rules.add_perm('plateformeweb.edit_activity',
               is_owner_for_object | is_org_admin_for_object | rules.is_staff \
               | rules.is_superuser)
rules.add_perm('plateformeweb.delete_activity',
               is_org_admin_for_object | rules.is_staff | rules.is_superuser)

# events
rules.add_perm('plateformeweb.create_event',
               is_org_admin_for_object | rules.is_staff | rules.is_superuser)

rules.add_perm('plateformeweb.edit_event',
               is_owner_for_object | is_org_admin_for_object | rules.is_staff \
               | rules.is_superuser)
rules.add_perm('plateformeweb.delete_event',
               is_org_admin_for_object | rules.is_staff | rules.is_superuser)

# places
rules.add_perm('plateformeweb.create_place',
               is_org_admin_for_object | rules.is_staff | rules.is_superuser)
rules.add_perm('plateformeweb.edit_place',
               is_owner_for_object | is_org_admin_for_object | rules.is_staff \
               | rules.is_superuser)
rules.add_perm('plateformeweb.delete_place',
               is_org_admin_for_object | rules.is_staff | rules.is_superuser)

# TODO add non-django rules (command-line, admin?)
