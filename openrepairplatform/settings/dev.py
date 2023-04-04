from .base import *  

#pourquoi ? ... parceque...
MEDIA_ROOT = "/srv/media/openrepairplatform_media/"


INSTALLED_APPS += ["debug_toolbar","livereload"]  

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  
MIDDLEWARE.insert(0, 'livereload.middleware.LiveReloadScript') 

