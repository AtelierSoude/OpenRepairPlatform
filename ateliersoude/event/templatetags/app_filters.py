from django import template
from django.core import signing

from ateliersoude.user.models import Fee

register = template.Library()


@register.simple_tag
def tokenize(user, event, action):
    data = {"user_id": user.id, "event_id": event.id}
    return signing.dumps(data, salt=action)


@register.filter
def initial(form, user):
    form.initial.update(user.__dict__)
    return form


@register.simple_tag
def filter_orga(queryset, organization):
    return queryset.filter(organization=organization).first()


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode()


@register.simple_tag
def organization_fees(organization, user):
    return Fee.objects.filter(organization=organization, user=user)
