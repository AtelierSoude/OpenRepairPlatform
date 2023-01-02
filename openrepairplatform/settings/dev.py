from .base import *  # noqa


INSTALLED_APPS += ["debug_toolbar"]  # noqa

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa
