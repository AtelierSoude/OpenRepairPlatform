import os
from .base import *  # noqa

from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = [
    ""
    "127.0.0.1", "localhost",
    os.getenv("DOMAIN_NAME"),
]

STATIC_ROOT = "/srv/static/"
MEDIA_ROOT = "/srv/media/"
ASSETS_ROOT = STATIC_ROOT

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB_NAME"),
        "USER": os.getenv("POSTGRES_USER"),
        "HOST": 'db',
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    }
}

raven = os.getenv("RAVEN_DNS")

if raven:
    RAVEN_CONFIG = {"dsn": raven}
    INSTALLED_APPS += ["raven.contrib.django.raven_compat"]  # noqa

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 25
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")

