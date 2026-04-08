import os
from .base import *  # noqa

SECRET_KEY = os.getenv("SECRET_KEY")
STATIC_ROOT = "/srv/static/"

STATICFILES_DIRS = [
    "/srv/app/openrepairplatform/static/",
    "/srv/app/openrepairplatform/static/js",
    "/srv/app/openrepairplatform/static/css",
    "/srv/app/openrepairplatform/static/scss",
    ]
    
ASSETS_ROOT = "/srv/static/"
MEDIA_URL = "/media/"

if os.getenv("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.logging import ignore_logger

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        send_default_pii=True,
        enable_logs=True,
    )

    # Les requêtes par IP directe (scanners, bots) déclenchent DisallowedHost.
    # C'est du bruit opérationnel, pas un bug — on ne l'envoie pas à Sentry.
    # Direct IP requests (scanners, bots) trigger DisallowedHost.
    # This is operational noise, not a bug — we don't send it to Sentry.
    ignore_logger("django.security.DisallowedHost")
elif os.getenv("RAVEN_DNS"):
    RAVEN_CONFIG = {"dsn": os.getenv("RAVEN_DNS")}
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
