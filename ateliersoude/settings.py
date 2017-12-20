"""
For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import colored_traceback

colored_traceback.add_hook(always=True)

import os

POSTGRES_DB=os.environ["POSTGRES_DB"]
DEVELOPMENT=os.environ["DEVELOPMENT"]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP'

# only run debug if DEBUG=1 (or something else) is specified in the environment
# TODO store the rest of the configuration in environment variables as well
# see http://bruno.im/2013/may/18/django-stop-writing-settings-files/
DEBUG = bool(int(os.environ.get('DJANGO_DEBUG', 0)))

# TODO adjust for production
ALLOWED_HOSTS = ["dev.atelier-soude.fr", "ns60.amakuru.net", "127.0.0.1", "localhost"]

# for debug toolbar, localhost (through docker and localhost)
# no wildcards for IPs, possible to use a sort of wildcard for hostnames,
# like ".office.internal.tld"
# ALSO SEE https://stackoverflow.com/a/45624773
INTERNAL_IPS = ['127.0.0.1', ]
import socket
import os
# tricks to have debug toolbar when developing with docker
ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + '1']

APPEND_SLASH = True

# Application definition

INSTALLED_APPS = [
    # django rules autodiscover rules.py files
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
    'users',
    'django_tables2',
    'import_export',
    'fontawesome',
    'simple_history',
    'dbsettings',
    'debug_toolbar',
    'plateformeweb',
    'phonenumber_field',
    'address',
    'avatar',
    'crispy_forms',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # put it first unless it breaks other middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
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
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
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
        'NAME': 'ateliersoude',
        'USER': 'ateliersoude',
        'PASSWORD': 'ateliersoude',
        'HOST': POSTGRES_DB,
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
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
# https://github.com/kevin1024/django-npm
STATICFILES_FINDERS = ['django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                       'npm.finders.NpmFinder']  # for django-npm

# TODO move to a CDN or a different server for media files in production
# See https://trello.com/c/fnTkmBRk
# also see urls.py in the ateliersoude dir, for the setting used during dev
MEDIA_URL = '/media/'
MEDIA_ROOT = '/tmp/media/'


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
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'dmorel@amakuru.net'
EMAIL_HOST_PASSWORD = 'bammyvwcqbuvtdni'
EMAIL_PORT = 587

# where to go after successful authentication?
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/auth/login/'

# FIXTURE_DIRS= (
#    os.path.join(BASE_DIR, "fixtures"),
# )

# TODO remove this and use Redis for the shared cache
DBSETTINGS_USE_CACHE = False

# TODO for the address module; change it!
GOOGLE_API_KEY = "AIzaSyCNZ-rIhY1zyq2LFghBV4x7mUQvtJCOK88"

# npm (https://github.com/kevin1024/django-npm)
NPM_FILE_PATTERNS = {
    'purecss': ['build/*.js', 'build/*.css'],
    'stickyfilljs': ['dist/*.js', 'dist/*.css'],
    'semantic-ui': ['dist/*'],
}
NPM_STATIC_FILES_PREFIX = 'npm'
NPM_ROOT_PATH = BASE_DIR

# for django rules
AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)
