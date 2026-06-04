# -*- coding: utf-8 -*-
"""INSTALLED_APPS + MIDDLEWARE + AUTHENTICATION_BACKENDS"""

AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = (
    # 用户管理
    "itsm.users",
    # Django 内置
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 引擎
    "pipeline",
    "pipeline.log",
    "pipeline.engine",
    "pipeline.component_framework",
    "pipeline.variable_framework",
    "pipeline.contrib.engine_admin",
    # itsm 业务
    "itsm.iadmin",
    "itsm.gateway",
    "itsm.role",
    "itsm.pipeline_plugins",
    "itsm.ticket",
    "itsm.service",
    "itsm.project",
    "itsm.workflow",
    "itsm.sla",
    "itsm.ticket_status",
    "itsm.sla_engine",
    "itsm.postman",
    "itsm.misc",
    "itsm.trigger",
    "itsm.task",
    "itsm.openapi",
    "itsm.monitor",
    "itsm.meta",
    # 第三方
    "mptt",
    "rest_framework",
    "corsheaders",
    "django_filters",
    # Celery
    "django_celery_beat",
    "django_celery_results",
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "itsm.users.backends.CustomUserBackend",
)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "itsm.users.validators.SecurityPolicyPasswordValidator"},
]

MIDDLEWARE = (
    "itsm.component.misc_middlewares.ServiceSwitchCheck",
    "itsm.component.misc_middlewares.ApiIgnoreCheck",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
