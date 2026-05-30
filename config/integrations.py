# -*- coding: utf-8 -*-
"""平台集成配置"""
import os

from config import APP_CODE  # noqa

# 平台 API 基础地址（用于 platform_client HTTP 调用）
PLATFORM_API_BASE_URL = os.environ.get("PLATFORM_API_BASE_URL", "")

# 平台地址
BK_CC_HOST = os.environ.get("BK_CC_HOST", "#")
BK_JOB_HOST = os.environ.get("BK_JOB_HOST", "#")
USER_MANGE_HOST = os.environ.get("BK_COMPONENT_API_URL", "")
BK_USER_MANAGE_HOST = os.environ.get("BK_USER_MANAGE_HOST", USER_MANGE_HOST)

BK_PAAS_ESB_HOST = os.environ.get("BK_COMPONENT_API_URL", "")

# 前端地址
FRONTEND_URL = os.environ.get("BKAPP_FRONTEND_URL", "")

# IAM（仍被 cipher、openapi serializer 引用）
BK_IAM_APP_CODE = os.getenv("BK_IAM_V3_APP_CODE", "bk_iam")
IAM_ESB_PAAS_HOST = os.environ.get("BK_COMPONENT_API_URL", "")
CALLBACK_AES_KEY = "APPROVAL_RESULT"

# 蓝盾（仍被 workflow/apps.py 引用）
INIT_DEVOPS_TEMPLATE = os.environ.get("INIT_DEVOPS_TEMPLATE", False)

# APIGW（仍被 openapi/base_service/views/apigw.py 引用）
BK_API_URL_TMPL = os.getenv("BK_API_URL_TMPL")

# 文档
BK_DOC_CENTER_HOST = os.getenv("BK_DOC_CENTER_HOST", "#")
BK_DOC_URL = "{}/markdown/{{lang}}/ITSM/{{version}}/UserGuide/Introduce/README.md".format(
    BK_DOC_CENTER_HOST
)

# TAPD（仍被 component/utils/auth.py 引用）
TAPD_OAUTH_URL = os.environ.get("TAPD_OAUTH_URL", "")

# 公共
BK_DESKTOP_URL = os.environ.get("BK_DESKTOP_URL", "")
FOOTER = os.getenv("BKAPP_FOOTER", None)
BK_SHARED_RES_URL = os.getenv("BKPAAS_SHARED_RES_URL") or os.getenv(
    "BKAPP_SHARED_RES_URL"
)
BK_PLATFORM_NAME = os.getenv("BKAPP_PLATFORM_NAME", "")

# 企微webhook
QW_WEB_HOOK_URL = os.getenv(
    "BKAPP_QW_WEB_HOOK_URL",
    "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}",
)
