from .base import *  # noqa
import os


INSTALLED_APPS += ["debug_toolbar"]  # noqa

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa

INTERNAL_IPS = ["127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ateliersoude",
        "USER": "ateliersoude",
        "HOST": "db",
        "PORT": "5432",
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "ateliersoude"),
    }
}