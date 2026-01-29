from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    if not d:
        return None
    return d.get(key)
