from django.conf import settings


def site_title(request):
    return {"site_title": "Reparons.org"}


def settings_variables(request):
    return {
        'PREPROD':settings.PREPROD,
        'LOCATION': settings.LOCATION,
            }
