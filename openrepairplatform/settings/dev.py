from .base import *  

DEBUG = True

STATIC_ROOT = "/srv/static/"

STATICFILES_DIRS = [
    "/srv/app/openrepairplatform/static/",
    "/srv/app/openrepairplatform/static/js",
    "/srv/app/openrepairplatform/static/css",
    "/srv/app/openrepairplatform/static/scss",
    ]
ASSETS_ROOT = "/srv/static/"




#pourquoi ? ... parceque...
MEDIA_ROOT = "/srv/media/"

INSTALLED_APPS += ["debug_toolbar","livereload"]  

MIDDLEWARE.insert(101, "debug_toolbar.middleware.DebugToolbarMiddleware")  
MIDDLEWARE.insert(100, 'livereload.middleware.LiveReloadScript') 

DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]


if DEBUG:
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

if not DEBUG and os.getenv("SENTRY_DSN"):
    import sentry_sdk
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        # Enable sending logs to Sentry
        enable_logs=True,
    )