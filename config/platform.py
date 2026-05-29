# -*- coding: utf-8 -*-
"""蓝鲸平台兼容配置（TODO: 后续 plan 逐步清理移除）"""
import base64
import os
from urllib.parse import urljoin

from config import APP_CODE  # noqa
from config.env import BK_PAAS_HOST, BK_PAAS_INNER_HOST  # noqa

# 平台地址
BK_CC_HOST = os.environ.get("BK_CC_HOST", "#")
BK_JOB_HOST = os.environ.get("BK_JOB_HOST", "#")
USER_MANGE_HOST = os.environ.get(
    "BK_COMPONENT_API_URL", BK_PAAS_HOST
)
BK_USER_MANAGE_HOST = os.environ.get("BK_USER_MANAGE_HOST", USER_MANGE_HOST)
LOGIN_URL = os.environ.get("LOGIN_URL", "/account/login/")

# 前端地址
FRONTEND_URL = os.environ.get("BKAPP_FRONTEND_URL") or os.path.join(
    BK_PAAS_HOST, os.environ.get("BKAPP_ITSM_URL", "o/bk_itsm/")
)
WEIXIN_APP_EXTERNAL_SHARE_HOST = "{}weixin/".format(
    os.environ.get("BKAPP_WEIXIN_APP_EXTERNAL_HOST", FRONTEND_URL)
)
TICKET_NOTIFY_HOST = WEIXIN_APP_EXTERNAL_SHARE_HOST

# 标准运维代理
SOPS_PROXY_URL = os.environ.get(
    "BKAPP_SOPS_PROXY_URL", "{}{}".format(BK_PAAS_INNER_HOST, "/o/bk_sops/")
)
SOPS_SITE_URL = os.environ.get(
    "BKAPP_SOPS_SITE_URL", "{}{}".format(BK_PAAS_HOST, "/o/bk_sops/")
)
SOPS_ALLOW_ACCESS = ["/api/v3/component/", "/api/v3/variable/"]
REVPROXY = {"QUOTE_SPACES_AS_PLUS": False}
PREFIX_SOPS = ""

# APIGW
APIGW_APP_CODE = os.environ.get("BKAPP_APIGW_APP_CODE", "")
APIGW_SECRET_KEY = os.environ.get("BKAPP_APIGW_SECRET_KEY", "")
APIGW_USERNAME = os.environ.get("BKAPP_APIGW_USERNAME", "")
BK_API_USE_BKCLOUDS_FIRST = True


def my_before_proxy_func(request, json_data, request_headers):
    json_data["app_code"] = APIGW_APP_CODE
    json_data["app_secret"] = APIGW_SECRET_KEY
    json_data["bk_username"] = APIGW_USERNAME


BEFORE_PROXY_FUNC = my_before_proxy_func
DEFAULT_VARIABLE_NAME = "variable_by_name"

# IAM
BK_IAM_SYSTEM_ID = os.getenv("BKAPP_BK_IAM_SYSTEM_ID", APP_CODE)
BK_IAM_SYSTEM_NAME = os.getenv("BKAPP_BK_IAM_SYSTEM_NAME", "ITSM")
BK_IAM_INNER_HOST = os.environ.get("BK_IAM_V3_INNER_HOST", None)
BK_IAM_APP_CODE = os.getenv("BK_IAM_V3_APP_CODE", "bk_iam")
BK_IAM_SAAS_HOST = os.environ.get(
    "BK_IAM_V3_SAAS_HOST", urljoin(BK_PAAS_HOST, "/o/{}".format(BK_IAM_APP_CODE))
)
BK_IAM_API_PREFIX = "/openapi"
BK_API_USE_TEST_ENV = os.environ.get("BK_API_USE_TEST_ENV") == "True"
IAM_ESB_PAAS_HOST = os.environ.get("BK_COMPONENT_API_URL", BK_PAAS_INNER_HOST)
BK_IAM_ESB_PAAS_HOST = os.environ.get("BK_IAM_ESB_PAAS_HOST", IAM_ESB_PAAS_HOST)
IAM_INITIAL_FILE = os.environ.get("BKAPP_IAM_INITIAL_FILE", "")
IAM_SDK_CLIENT_TIMEOUT = int(os.getenv("BKAPP_IAM_SDK_CLIENT_TIMEOUT", 20))
CALLBACK_AES_KEY = "APPROVAL_RESULT"

# 蓝盾
INIT_DEVOPS_TEMPLATE = os.environ.get("INIT_DEVOPS_TEMPLATE", False)
BKAPP_CI_ENABLED = os.environ.get("BKAPP_CI_ENABLED", "") == "1"
DEVOPS_CLIENT_URL = os.environ.get("DEVOPS_CLIENT_URL", "")
DEVOPS_BASE_URL = os.environ.get("DEVOPS_BASE_URL", "")

# 文档
BK_DOC_CENTER_HOST = os.getenv(
    "BK_DOC_CENTER_HOST",
    os.getenv("BK_DOCS_URL_PREFIX", "{}o/bk_docs_center".format(BK_PAAS_HOST)),
)
BK_DOC_URL = "{}{}".format(
    BK_DOC_CENTER_HOST,
    "/markdown/{lang}/ITSM/{version}/UserGuide/Introduce/README.md",
)

# BKCHAT
USE_BKCHAT = os.getenv("USE_BKCHAT", "true").lower() == "true"
if USE_BKCHAT:
    BKCHAT_URL = os.environ.get("BKCHAT_URL", "")
    BKCHAT_CALLBACK_URL = os.environ.get("BKCHAT_CALLBACK_URL", "")
    ITSM_SUMMARY_URL = os.environ.get("ITSM_SUMMARY_URL", "")
    BKCHAT_ENV = os.environ.get("BKCHAT_ENV", None)
    BKCHAT_ENV_FLAG = os.environ.get("BKCHAT_ENV_FLAG", "")

# TAPD
ITSM_TAPD_APIGW = os.environ.get("ITSM_TAPD_APIGW", "")
TAPD_OAUTH_URL = os.environ.get("TAPD_OAUTH_URL", "")

# 公钥
api_public_key = os.environ.get("APIGW_PUBLIC_KEY", "")
APIGW_PUBLIC_KEY = base64.b64decode(api_public_key) if api_public_key else b""

# APIGW
BK_APIGW_NAME = os.getenv("BK_APIGW_NAME", "bk-itsm")
BK_API_URL_TMPL = os.getenv("BK_API_URL_TMPL")
BK_NOTICE = {"BK_API_URL_TMPL": BK_API_URL_TMPL or ""}
PLUGIN_DISTRIBUTOR_NAME = os.getenv("BKAPP_PLUGIN_DISTRIBUTOR_NAME", APP_CODE)

# BKCRYPTO
if os.getenv("BKPAAS_BK_CRYPTO_TYPE") == "SHANGMI":
    BKCRYPTO_SYMMETRIC_CIPHER_TYPE = "SM4"
else:
    BKCRYPTO_SYMMETRIC_CIPHER_TYPE = "AES"
BLUEAPPS_ENABLE_DB_ENCRYPTION = True

# 加密配置（需要 APP_TOKEN）
from config import APP_TOKEN  # noqa
BKCRYPTO = {
    "SYMMETRIC_CIPHER_TYPE": BKCRYPTO_SYMMETRIC_CIPHER_TYPE,
    "SYMMETRIC_CIPHERS": {
        "blueapps": {
            "common": {"key": APP_TOKEN},
        },
    },
}

# 公共
BK_DESKTOP_URL = os.environ.get("BK_DESKTOP_URL") or BK_PAAS_HOST
FOOTER = os.getenv("BKAPP_FOOTER", None)
BK_SHARED_RES_URL = os.getenv("BKPAAS_SHARED_RES_URL") or os.getenv(
    "BKAPP_SHARED_RES_URL"
)
BK_PLATFORM_NAME = os.getenv("BKAPP_PLATFORM_NAME", "")
BK_IEOD_LOGIN_URL = os.environ.get("BK_IEOD_LOGIN_URL", "")
MY_OA_CALLBACK_URL = os.environ.get("MY_OA_CALLBACK_URL", "")

# CSRF
BKPAAS_BK_DOMAIN = os.getenv("BKPAAS_BK_DOMAIN", "")
CSRF_TRUSTED_ORIGINS = [
    "https://*.{}".format(BKPAAS_BK_DOMAIN),
    "http://*.{}".format(BKPAAS_BK_DOMAIN),
]

# 企微webhook
QW_WEB_HOOK_URL = os.getenv(
    "BKAPP_QW_WEB_HOOK_URL",
    "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}",
)
