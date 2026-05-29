# -*- coding: utf-8 -*-
"""环境配置 — 兼容垫片 + 环境变量"""
import os

from config import APP_CODE, BASE_DIR, PROJECT_ROOT  # noqa

# 平台地址（通过环境变量配置，用于向后兼容）
BK_PAAS_HOST = os.environ.get("BK_PAAS_HOST", "http://127.0.0.1")
BK_PAAS_INNER_HOST = os.environ.get("BK_PAAS_INNER_HOST", BK_PAAS_HOST)
BK_URL = BK_PAAS_HOST
RUN_VER = os.environ.get("RUN_VER", "open")

# ==============================================================================
# 环境配置（全部由环境变量驱动）
# ==============================================================================
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
RUN_MODE = os.environ.get("RUN_MODE", "DEVELOP")
