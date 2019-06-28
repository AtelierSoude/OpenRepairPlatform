from os.path import dirname, abspath, join

from bootstrap4 import forms
from django.contrib import messages

PROJECT_DIR = dirname(dirname(abspath(__file__)))
BASE_DIR = dirname(PROJECT_DIR)

SECRET_KEY = "H/hXAUnb1ZKNGpToim2cg38dxiyHM6b+zB9zozhpTzkP"

DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1

INSTALLED_APPS = [
    "ateliersoude.event",
    "ateliersoude.user",
    "ateliersoude.location",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "simple_history",
    "rest_framework",
    "bootstrap",
    "fontawesome",
    "django_assets",
    "bootstrap4",
    "sorl.thumbnail",
    "tinymce",
    "import_export",
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
    "ateliersoude.event.middleware.middleware.ForceLangMiddleware"
]

ROOT_URLCONF = "ateliersoude.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [(join(BASE_DIR, "ateliersoude", "templates"))],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ]
        },
    }
]

WSGI_APPLICATION = "ateliersoude.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ateliersoude",
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

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True


STATICFILES_DIRS = [join(PROJECT_DIR, "static")]

STATIC_ROOT = join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = join(BASE_DIR, "media")


# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = join(BASE_DIR, "tmp", "messages")


AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# Config django-assets
ASSETS_MODULES = ["ateliersoude.assets"]
ASSETS_ROOT = STATICFILES_DIRS[0]

# Add class to field wrapper in django-bootstrap4
forms.FORM_GROUP_CLASS += " p-2"

# django messages settings
MESSAGE_TAGS = {messages.ERROR: "danger"}
