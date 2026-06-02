# -*- coding: utf-8 -*-
"""REST Framework + Templates + CSRF/Session"""
import os

from config import APP_CODE, BASE_DIR, PROJECT_ROOT  # noqa

# ==============================================================================
# Core URL / WSGI
# ==============================================================================
ROOT_URLCONF = "urls"
WSGI_APPLICATION = "wsgi.application"

# ==============================================================================
# REST FRAMEWORK
# ==============================================================================
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "itsm.component.generics.exception_handler",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "itsm.component.drf.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.OrderingFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "NON_FIELD_ERRORS_KEY": "params_error",
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "itsm.component.drf.parsers.ExtraJSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

# ==============================================================================
# Templates
# TODO: 评估是否完全去除 Mako，迁移到 Django templates
# ==============================================================================
MAKO_TEMPLATE_DIR = (
    os.path.join(BASE_DIR, "mako_templates"),
    os.path.join(BASE_DIR, "static", "dist"),
)
MAKO_TEMPLATE_MODULE_DIR = os.path.join(
    os.path.dirname(BASE_DIR), "templates_module", APP_CODE
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (
            os.path.join(BASE_DIR, "static", "assets"),
            os.path.join(BASE_DIR, "templates"),
        ),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATETIME_FORMAT = "Y-m-d H:i:s"
DATE_FORMAT = "Y-m-d"

# ==============================================================================
# Static files
# ==============================================================================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(os.environ.get("PROJECT_ROOT", BASE_DIR), "staticfiles/")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_VERSION = "2.6.11"

# ==============================================================================
# Media files
# ==============================================================================
MEDIA_URL = "%smedia/" % os.environ.get("SITE_URL", "/")
MEDIA_ROOT = os.path.join(os.environ.get("PROJECT_ROOT", os.path.dirname(BASE_DIR)), "USERRES")

FILE_CHARSET = "utf-8"

# ==============================================================================
# File storage
# ==============================================================================
from django.core.files.storage import FileSystemStorage

STORE = FileSystemStorage()

# ==============================================================================
# CSRF / Session
# ==============================================================================
CSRF_COOKIE_PATH = "/"
CSRF_COOKIE_NAME = os.environ.get("CSRF_COOKIE_NAME", "bkitsm_csrftoken")
SESSION_COOKIE_NAME = "bkitsm_sessionid"
LOGIN_URL = os.environ.get("LOGIN_URL", "/account/login/")

APP_DOMAIN = os.getenv("APP_DOMAIN", "")
CSRF_TRUSTED_ORIGINS = [
    "https://*.{}".format(APP_DOMAIN),
    "http://*.{}".format(APP_DOMAIN),
]

# ==============================================================================
# Email / Notifications
# ==============================================================================
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 25))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "false").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "itsm@localhost")
DEFAULT_WEBHOOK_URL = os.environ.get("DEFAULT_WEBHOOK_URL", "")
