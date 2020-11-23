from .base import *  # noqa


INSTALLED_APPS += ["debug_toolbar"]  # noqa

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa

INTERNAL_IPS = ["127.0.0.1"]

DATABASES = {
"default": {
"ENGINE": "django.db.backends.postgresql",
"NAME": os.getenv("POSTGRES_DB_NAME"),
"USER": os.getenv("POSTGRES_USER"),
"HOST": "127.0.0.1",
"PORT": "5432",
"PASSWORD": os.getenv("POSTGRES_PASSWORD"),
}
}