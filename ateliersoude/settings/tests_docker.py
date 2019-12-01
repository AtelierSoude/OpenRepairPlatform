from .base import *  # noqa
import os
import socket
import sys
import os

debug = True

INSTALLED_APPS += ['debug_toolbar', ]
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']

ALLOWED_HOSTS = ALLOWED_HOSTS + ['localhost', '127.0.0.1', 'djangotests']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "ateliersoudedb",
    }
}
