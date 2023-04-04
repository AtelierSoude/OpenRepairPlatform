from .base import *  

#pourquoi ? ... parceque...
MEDIA_ROOT = "/srv/media/openrepairplatform_media/"

INSTALLED_APPS += ["debug_toolbar","livereload"]  

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  
#MIDDLEWARE.insert(0, 'livereload.middleware.LiveReloadScript') 

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

