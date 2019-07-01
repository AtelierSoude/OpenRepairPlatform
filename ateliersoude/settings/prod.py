import os
from .base import *  # noqa

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = [
    "127.0.0.1", "localhost",
    "atelier-soude.fr",
    "www.atelier-soude.fr",
    "dev.atelier-soude.fr"
]

STATIC_ROOT = "/srv/static/"
MEDIA_ROOT = "/srv/media/"
ASSETS_ROOT = STATIC_ROOT

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ateliersoude",
        "USER": "ateliersoude",
        "HOST": "postgres",
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "ateliersoude"),
    }
}

raven = os.getenv("RAVEN_DNS")

if raven:
    RAVEN_CONFIG = {"dsn": raven}
    INSTALLED_APPS += ["raven.contrib.django.raven_compat"]  # noqa

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.atelier-soude.fr"
EMAIL_PORT = 25
EMAIL_HOST_USER = "no-reply@atelier-soude.fr"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
