import os

from .base import *  # NOQA


DOCKER_TEST = os.environ.get("DOCKER_TEST", "")
if DOCKER_TEST == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "mysecretpassword",
            "HOST": "postgres",
            "PORT": "5432",
        }
    }
