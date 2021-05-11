import os
from .base import *  # noqa
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP"

DEBUG = False

ALLOWED_HOSTS = ["openrepairplatform.hashbang.fr"]

INSTALLED_APPS += ["raven.contrib.django.raven_compat"]  # noqa

STATIC_ROOT = "/srv/app/openrepairplatform/static/"
MEDIA_ROOT = "/srv/app/openrepairplatform/media/"
ASSETS_ROOT = STATIC_ROOT


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB_NAME"),
        "USER": os.getenv("POSTGRES_USER"),
        "HOST": "db",
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    }
}

RAVEN_CONFIG = {"dsn": os.getenv("RAVEN_DNS")}

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 25
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
