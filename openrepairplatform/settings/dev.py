from .base import *  # noqa
from dotenv import load_dotenv

load_dotenv()

INSTALLED_APPS += ["debug_toolbar"]  # noqa

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa

INTERNAL_IPS = ["127.0.0.1"]
