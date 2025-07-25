from django import template
from django.core import signing

from openrepairplatform.user.models import Fee

register = template.Library()


@register.simple_tag
def tokenize(user, event, action):
    data = {"user_id": user.id, "event_id": event.id}
    return signing.dumps(data, salt=action)


@register.filter
def initial(form, user):
    form.initial.update(user.__dict__)
    return form


@register.filter
def initial_stuff(form, stuff):
    form.initial.update(
        {
            "state": stuff.state,
            "organization_owner": stuff.organization_owner,
            "member_owner": stuff.member_owner,
            "place": stuff.place,
            "device": stuff.device,
        }
    )
    return form


@register.simple_tag
def filter_orga(queryset, organization):
    return queryset.filter(organization=organization).first()


@register.simple_tag
def filter_user(queryset, user):
    return queryset.filter(user=user).first()


@register.simple_tag
def related_user(queryset, user):
    return queryset.filter(user=user)


@register.simple_tag
def related_membership(queryset, membership):
    return queryset.filter(membership=membership)


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode()


@register.simple_tag
def sum_conditions(conditions):
    return sum(condition.price for condition in conditions)

@register.simple_tag
def organization_fees(organization, user):
    """
    Returns the fees for a given user and organization.
    """
    return Fee.objects.filter(organization=organization, membership__user=user)