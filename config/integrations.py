# -*- coding: utf-8 -*-
"""平台集成配置"""
import os

from config import APP_CODE  # noqa

# 平台 API 基础地址（用于 platform_client HTTP 调用）
PLATFORM_API_BASE_URL = os.environ.get("PLATFORM_API_BASE_URL", "")

# 平台 API 地址（统一，替代原 BK_COMPONENT_API_URL 多处重复）
PLATFORM_API_URL = os.environ.get("PLATFORM_API_URL", "")

# 用户管理
USER_MANAGE_HOST = os.environ.get("USER_MANAGE_HOST", PLATFORM_API_URL)

# 前端地址
FRONTEND_URL = os.environ.get("FRONTEND_URL", "")

# APIGW（仍被 openapi/base_service/views/apigw.py 引用）
API_URL_TEMPLATE = os.getenv("API_URL_TEMPLATE")

# 文档
DOC_CENTER_HOST = os.getenv("DOC_CENTER_HOST", "#")
DOC_URL = "{}/markdown/{{lang}}/ITSM/{{version}}/UserGuide/Introduce/README.md".format(
    DOC_CENTER_HOST
)

# 公共
FOOTER = os.getenv("FOOTER", None)
SHARED_RES_URL = os.getenv("SHARED_RES_URL")
PLATFORM_NAME = os.getenv("PLATFORM_NAME", "")

# 企微 webhook
QW_WEB_HOOK_URL = os.getenv(
    "QW_WEB_HOOK_URL",
    "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}",
)
