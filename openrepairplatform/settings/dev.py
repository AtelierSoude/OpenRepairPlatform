from .base import *  

INSTALLED_APPS += ["debug_toolbar","livereload"]  

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  
MIDDLEWARE.insert(0, 'livereload.middleware.LiveReloadScript') 

