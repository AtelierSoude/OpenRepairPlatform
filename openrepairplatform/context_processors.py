from django.conf import settings


def site_title(request):
    return {"site_title": "Réparons"}


def settings_variables(request):
    return {
        'PREPROD':settings.PREPROD,
        'LOCATION': settings.LOCATION,
            }
