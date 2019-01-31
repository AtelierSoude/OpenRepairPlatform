"""
For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import os
import socket
import re
import colored_traceback
import users.apps
import plateformeweb.apps

colored_traceback.add_hook(always=True)

POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
DEVELOPMENT = os.environ.get("DEVELOPMENT")

SMTP_HOST = os.environ.get("SMTP_HOST")
EMAIL_ADRESSE = os.environ.get("EMAIL_ADRESSE")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# only run debug if DEBUG=1 (or something else) is specified in the environment
# TODO store the rest of the configuration in environment variables as well
# see http://bruno.im/2013/may/18/django-stop-writing-settings-files/
DEBUG = bool(int(os.environ.get('DJANGO_DEBUG', 0)))

# TODO adjust for production
ALLOWED_HOSTS = ['*']
#ALLOWED_HOSTS = ['"dev.atelier-soude.fr", "127.0.0.1", "localhost"']

# for debug toolbar, localhost (through docker and localhost)
# no wildcards for IPs, possible to use a sort of wildcard for hostnames,
# like ".office.internal.tld"
# ALSO SEE https://stackoverflow.com/a/45624773
INTERNAL_IPS = ['127.0.0.1', ]
# tricks to have debug toolbar when developing with docker
IP = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += [re.sub(r"[0-9]+$", "1", IP)]

APPEND_SLASH = True

# Application definition

INSTALLED_APPS = [
    # django rules autodiscover rules.py files
    'django.contrib.sites',
    'rules.apps.AutodiscoverRulesConfig',
    'datetimepicker',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'axes',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # http://whitenoise.evans.io/en/stable/django.html
    'django.contrib.staticfiles',
    'users.apps.CustomusersConfig',
    'api',
    'dbsettings',
    'django_tables2',
    'import_export',
    'fontawesome',
    'simple_history',
    'debug_toolbar',
    'plateformeweb.apps.PlateformeWebAppConfig',
    'address',
    'avatar',
    'crispy_forms',
    'fm',
    'django_bootstrap_breadcrumbs',
    'django_markdown',
    'easy_maps',
    'actstream',
    'celery',
    'post_office',
]
SITE_ID = 1

DBSETTINGS_USE_SITES = False

MIDDLEWARE = [
    # put the following line first, unless it breaks other middleware
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
]

ROOT_URLCONF = 'ateliersoude.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            (os.path.join(BASE_DIR, 'templates')),
        ],  # handle the /templates base directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors' : [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'plateformeweb.context_processors.user_data',
                'plateformeweb.context_processors.last_events',
                'plateformeweb.context_processors.user_in_organization',
                'plateformeweb.context_processors.admin_of_organizations',
            ],
        },
    },
]

WSGI_APPLICATION = 'ateliersoude.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': '5432',
    }
}

# custom User model
AUTH_USER_MODEL = "users.CustomUser"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# collected and put in temp dir by: python3 manage.py collectstatic
STATIC_URL = '/static/'
STATIC_ROOT = '/tmp/django-static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
CRISPY_TEMPLATE_PACK = 'bootstrap3'
BREADCRUMBS_TEMPLATE = "django_bootstrap_breadcrumbs/bootstrap4.html"
# https://github.com/kevin1024/django-npm
STATICFILES_FINDERS = ['django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                       'npm.finders.NpmFinder']  # for django-npm

# TODO move to a CDN or a different server for media files in production
# See https://trello.com/c/fnTkmBRk
# also see urls.py in the ateliersoude dir, for the setting used during dev
MEDIA_URL = '/media/'
MEDIA_ROOT = '/ateliersoude/media/'

##markdown settings##
MARKDOWN_EDITOR_SKIN = 'simple'

# LOCKDOWN_ENABLED = False
# LOCKDOWN_PASSWORDS = ('76j&6wzz#!9fjP7fFQd',)

# https://docs.djangoproject.com/en/dev/topics/logging/
# redirect all logging to console, same as DEBUG=True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        # TODO remove the 3 configs below and replace them
        # with a single 'usersusers' entry
        'users.views': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'users.forms': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'users.models': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'plateformeweb.views': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'plateformeweb.forms': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'plateformeweb.models': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        # log DB queries, only works when DEBUG is True in
        # the global configuration
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        #     'propagate': False,
        # },
        # 'gunicorn.error': {
        #     'handlers': ['console'],
        #     'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        #     'propagate': True,
        # },
        # 'gunicorn.access': {
        #     'handlers': ['console'],
        #     'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        #     'propagate': False,
        # },
        'axes.watch_login': {
            'handlers': ['console'],
            'level': 'INFO',  # os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        },
    },
}

# http://django-import-export.readthedocs.io/en/latest/installation.html?highlight=transactions
IMPORT_EXPORT_USE_TRANSACTIONS = True

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
  # 'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# Celery application definition
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Paris'

EMAIL_USE_TLS = True
EMAIL_HOST = SMTP_HOST
EMAIL_HOST_USER = EMAIL_ADRESSE
EMAIL_HOST_PASSWORD = EMAIL_PASSWORD
EMAIL_PORT = 587
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = EMAIL_ADRESSE
SERVER_EMAIL = EMAIL_ADRESSE


# where to go after successful authentication?
LOGIN_REDIRECT_URL = '/activity/'
LOGIN_URL = '/auth/login/'

# FIXTURE_DIRS= (
#    os.path.join(BASE_DIR, "fixtures"),
# )

# TODO remove this and use Redis for the shared cache
DBSETTINGS_USE_CACHE = False

# TODO for the address module; change it!
GOOGLE_API_KEY = "AIzaSyD4BbszAhBjzV7S1ag3KKRNX_xLjy6bwEI"
# GOOGLE_API_KEY = "AIzaSyCNZ-rIhY1zyq2LFghBV4x7mUQvtJCOK88"
EASY_MAPS_GOOGLE_MAPS_API_KEY = "AIzaSyD4BbszAhBjzV7S1ag3KKRNX_xLjy6bwEI"
# EASY_MAPS_GOOGLE_MAPS_API_KEY = "AIzaSyCNZ-rIhY1zyq2LFghBV4x7mUQvtJCOK88"

# npm (https://github.com/kevin1024/django-npm)
NPM_FILE_PATTERNS = {
    'purecss': ['build/*.js', 'build/*.css'],
    'stickyfilljs': ['dist/*.js', 'dist/*.css'],
}
NPM_STATIC_FILES_PREFIX = 'npm'
NPM_ROOT_PATH = BASE_DIR

# for django rules
AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

#django-avatar
AVATAR_PROVIDERS = (
    'avatar.providers.PrimaryAvatarProvider',
    'avatar.providers.DefaultAvatarProvider',
)

AVATAR_CLEANUP_DELETED = True
AVATAR_DEFAULT_URL = '../media/default.png'
AVATAR_EXPOSE_USERNAMES = False
AVATAR_THUMB_FORMAT = 'PNG'


POST_OFFICE = {
    #Celery integration see https://github.com/ui/django-post_office
    'DEFAULT_PRIORITY': 'now',
    'SENDING_ORDER': ['created'],
    'LOG_LEVEL': 2, # Log only failed deliveries
}
