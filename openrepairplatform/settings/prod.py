import os
from .base import *  # noqa

SECRET_KEY = os.getenv("SECRET_KEY")
STATIC_ROOT = "/srv/static/"

STATICFILES_DIRS = [
    "/srv/app/openrepairplatform/static/",
    "/srv/app/openrepairplatform/static/js",
    "/srv/app/openrepairplatform/static/scss",
    "/srv/app/openrepairplatform/static/css",
    ]


DEBUG = False

raven = os.getenv("RAVEN_DNS")

if raven:
    RAVEN_CONFIG = {"dsn": raven}
    INSTALLED_APPS += ["raven.contrib.django.raven_compat"]  # noqa

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 25
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
