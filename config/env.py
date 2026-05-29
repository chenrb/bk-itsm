# -*- coding: utf-8 -*-
"""环境配置 — 兼容垫片 + 环境变量 + 静态文件"""
import datetime
import os

from config import APP_CODE, BASE_DIR, PROJECT_ROOT  # noqa

# TODO: 兼容垫片 — 后续逐步清理所有引用
BK_PAAS_HOST = os.environ.get("BK_PAAS_HOST", "http://127.0.0.1")
BK_PAAS_INNER_HOST = os.environ.get("BK_PAAS_INNER_HOST", BK_PAAS_HOST)
BK_URL = BK_PAAS_HOST
RUN_VER = os.environ.get("RUN_VER", "open")

# ==============================================================================
# 环境配置（全部由环境变量驱动）
# ==============================================================================
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
RUN_MODE = os.environ.get("RUN_MODE", "DEVELOP")
BROKER_URL = os.environ.get("BROKER_URL", "redis://localhost:6379/0")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles/")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
BK_STATIC_URL = "/static"
STATIC_VERSION = "2.6.11"
DEPLOY_DATETIME = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
SITE_URL_SOPS = "/o/bk_sops/"

ALLOW_CSRF = os.environ.get("BKAPP_ALLOW_CSRF", None) == "1"
MEDIA_URL = "%smedia/" % os.environ.get("SITE_URL", "/")
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "USERRES")

FILE_CHARSET = "utf-8"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
