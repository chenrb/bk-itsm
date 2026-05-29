# -*- coding: utf-8 -*-
"""REST Framework + Templates + CSRF/Session"""
import os

from config import APP_CODE, BASE_DIR  # noqa

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
# ==============================================================================
MAKO_DIR_NAME = "mako_templates"
MAKO_DEFAULT_FILTERS = None
MAKO_TEMPLATE_DIR = (
    os.path.join(BASE_DIR, MAKO_DIR_NAME),
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
            os.path.join(BASE_DIR, "static", "weixin"),
        ),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blueapps.template.context_processors.blue_settings",
                "common.context_processors.mysetting",
                "sekizai.context_processors.sekizai",
                "weixin.core.context_processors.basic",
            ],
        },
    },
    {
        "BACKEND": "blueapps.template.backends.mako.MakoTemplates",
        "DIRS": MAKO_TEMPLATE_DIR,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blueapps.template.context_processors.blue_settings",
                "common.context_processors.mysetting",
                "django.template.context_processors.i18n",
                "sekizai.context_processors.sekizai",
                "weixin.core.context_processors.basic",
            ],
            "module_directory": MAKO_TEMPLATE_MODULE_DIR,
        },
    },
]

DATETIME_FORMAT = "Y-m-d H:i:s"
DATE_FORMAT = "Y-m-d"

# ==============================================================================
# CSRF / Session
# ==============================================================================
CSRF_COOKIE_PATH = "/"
CSRF_COOKIE_NAME = os.environ.get("BKAPP_CSRF_COOKIE_NAME", "bkitsm_csrftoken")
SESSION_COOKIE_NAME = "bkitsm_sessionid"
