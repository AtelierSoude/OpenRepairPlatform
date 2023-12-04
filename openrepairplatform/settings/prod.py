import os
from .base import *  # noqa

SECRET_KEY = os.getenv("SECRET_KEY")
STATIC_ROOT = "/srv/static/"

STATICFILES_DIRS = [
    "/srv/static/",
    "/srv/static/js",
    "/srv/static/css",
    "/srv/static/scss",
    ]
    
ASSETS_ROOT = "/srv/static/"


DEBUG = True

raven = os.getenv("RAVEN_DNS")

if raven:
    RAVEN_CONFIG = {"dsn": raven}
    INSTALLED_APPS += ["raven.contrib.django.raven_compat"]  # noqa

# Email Settings
MAILJET = os.getenv("MAILJET", "False").lower() in ('true', '1', 'y')

if MAILJET :
    ANYMAIL = {
        # (exact settings here depend on your ESP...)
        "MAILJET_API_KEY": os.getenv("MAILJET_API_KEY"),
        "MAILJET_SECRET_KEY": os.getenv("MAILJET_SECRET_KEY"),
    }
    EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 25
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
