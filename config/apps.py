# -*- coding: utf-8 -*-
"""INSTALLED_APPS + MIDDLEWARE + AUTHENTICATION_BACKENDS"""
import os

# TODO: 移除 IAM，替换为 django-guardian
USE_IAM = os.getenv("USE_IAM", "false").lower() == "true"
IAM_SKIP_AUTH = False

INSTALLED_APPS = (
    # itsm helper 注册首位
    "itsm.helper",
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
    "itsm.notice",
    "itsm.monitor",
    "itsm.meta",
    "data_migration",
    # 第三方
    "django_signal_valve",
    "mptt",
    "django_mptt_admin",
    "django_extensions",
    "rest_framework",
    "corsheaders",
    "django_filters",
    # wiki
    "django.contrib.humanize.apps.HumanizeConfig",
    "django_nyt.apps.DjangoNytConfig",
    "sekizai",
    "sorl.thumbnail",
    "simplemde",
    # TODO: 移除以下 blueking 依赖
    "apigw_manager.apigw",
    "weixin.core",
    "weixin",
    "blueapps.opentelemetry.instrument_app",
    "itsm.plugin_service",
    "bk_notice_sdk",
)

if USE_IAM:
    INSTALLED_APPS += ("iam", "iam.contrib.iam_migration", "itsm.auth_iam")

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "itsm.openapi.authentication.backend.CustomUserBackend",
)

MIDDLEWARE = (
    "itsm.component.misc_middlewares.HttpsMiddleware",
    "itsm.component.misc_middlewares.UserLoginForbiddenMiddleware",
    "itsm.component.misc_middlewares.ServiceSwitchCheck",
    "itsm.component.misc_middlewares.ApiIgnoreCheck",
    "itsm.component.misc_middlewares.WikiIamAuthMiddleware",
    "weixin.core.middlewares.WeixinProxyPatchMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # TODO: 移除以下 blueking 依赖
    "blueapps.account.middlewares.RioLoginRequiredMiddleware",
    "weixin.core.middlewares.WeixinAuthenticationMiddleware",
    "weixin.core.middlewares.WeixinLoginMiddleware",
    "blueapps.account.middlewares.LoginRequiredMiddleware",
    "blueapps.core.exceptions.middleware.AppExceptionMiddleware",
    "iam.contrib.django.middlewares.AuthFailedExceptionMiddleware",
    "itsm.component.misc_middlewares.InstrumentProfilerMiddleware",
    "apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware",
    "apigw_manager.apigw.authentication.ApiGatewayJWTAppMiddleware",
    "apigw_manager.apigw.authentication.ApiGatewayJWTUserMiddleware",
)
