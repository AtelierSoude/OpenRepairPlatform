from os.path import dirname, abspath, join
import os

from bootstrap5 import forms
from django.contrib import messages

PROJECT_DIR = dirname(dirname(abspath(__file__)))
BASE_DIR = dirname(PROJECT_DIR)

STATIC_URL = "/static/"
ASSETS_DEBUG = False

SECRET_KEY = "H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP"
PREPROD=os.environ.get("PREPROD")

#Set domains
domainOS = str(os.environ.get("DOMAINDNS")) + " " + str(os.environ.get("DOMAINS")) 
domains = []
domains.append(domainOS.split(" "))
ALLOWED_HOSTS = domains[0]

SITE_ID = 1

INSTALLED_APPS = [
    "dal",
    "dal_select2",
    "tinymce",
    "openrepairplatform.user",
    "openrepairplatform.event",
    "openrepairplatform.location",
    "openrepairplatform.inventory",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django.contrib.gis",
    "simple_history",
    "rest_framework",
    "fontawesome",
    "django_assets",
    "bootstrap5",
    "sorl.thumbnail",
    "import_export",
    "initial_avatars",
    "django_gravatar",
    'django_extensions',
    "django_tables2",
    "django_tables2_column_shifter",
    "django_filters",
    "treebeard",
    "bootstrap_modal_forms",
    "django_better_admin_arrayfield",
]


MIDDLEWARE = [
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "openrepairplatform.event.middleware.middleware.ForceLangMiddleware",
]

ROOT_URLCONF = "openrepairplatform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [(join(BASE_DIR, "openrepairplatform", "templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "openrepairplatform.context_processors.site_title",
                "openrepairplatform.context_processors.settings_variables",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "openrepairplatform.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("POSTGRES_DBNAME"),
        "USER": os.getenv("POSTGRES_USER"),
        "HOST": "db",
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    }
}


# custom User model
AUTH_USER_MODEL = "user.CustomUser"
LOGIN_REDIRECT_URL = "/"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATION = "django.contrib.auth.password_validation."
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": (AUTH_PASSWORD_VALIDATION + "UserAttributeSimilarityValidator")},
    {"NAME": (AUTH_PASSWORD_VALIDATION + "MinimumLengthValidator")},
    {"NAME": (AUTH_PASSWORD_VALIDATION + "CommonPasswordValidator")},
    {"NAME": (AUTH_PASSWORD_VALIDATION + "NumericPasswordValidator")},
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "fr-fr"

INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"]

TIME_ZONE = "Europe/Paris"

USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True


MEDIA_URL = "/srv/media/"
MEDIA_ROOT = "/srv/media/"
# MEDIA_ROOT = join(BASE_DIR, "/media") 

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = join(BASE_DIR, "tmp", "messages")


AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# Session settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Config django-assets
ASSETS_MODULES = ["openrepairplatform.assets"]

# Add class to field wrapper in django-bootstrap5
forms.FORM_GROUP_CLASS += " p-2"

# django messages settings
MESSAGE_TAGS = {messages.ERROR: "danger"}

# Avatar Innitials Settings
AVATAR_COLORS = ((254, 229, 110), (8, 51, 66), (43, 230, 171),)

# Django tables2
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap5.html"

KM_DISTANCE = 50

LOCATION = os.getenv("LOCATION", "False").lower() in ('true', '1', 'y')
SESSION_COOKIE_AGE =2419200
