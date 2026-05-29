# -*- coding: utf-8 -*-
"""业务环境变量配置"""
import os

# business_rules
DEFAULT_VARIABLE_NAME = "variable_by_name"

# 初始化管理员
BKAPP_ITSM_ADMIN = os.environ.get("BKAPP_ITSM_ADMIN", "")
INIT_SUPERUSER = set(
    ["admin"] + [u for u in BKAPP_ITSM_ADMIN.split(",") if u]
)

# 微信/企业微信
OUT_LINK = os.environ.get("BKAPP_OUT_LINK", "https://test.bksaas.com/")
WX_QY_AGENTID = os.environ.get("BKAPP_WX_QY_AGENTID", None)
WX_QY_CORPSECRET = os.environ.get("BKAPP_WX_QY_CORPSECRET", None)
WX_USER = os.environ.get("BKAPP_WX_USER", None)
USE_X_FORWARDED_HOST = True

# 自定义
CUSTOM_TITLE = os.environ.get("BKAPP_CUSTOM_TITLE", None)
LOG_NAME = os.environ.get("BKAPP_LOG_NAME", None)
CLOSE_NOTIFY = os.environ.get("BKAPP_CLOSE_NOTIFY", None)

# 用户管理
BK_USER_DEFAULT_FIELDS = "id,username,display_name,domain,logo,category_id,category_name"
BK_USER_WHITE_FIELDS = (
    os.environ.get("BKAPP_BK_USER_WHITE_FIELDS") or BK_USER_DEFAULT_FIELDS
).split(",")

# 短信评价
IS_USE_INVITE_SMS = os.environ.get("IS_USE_INVITE_SMS", None)
AUTO_COMMENT_DAYS = int(os.environ.get("BKAPP_AUTO_COMMENT_DAYS", 3))
TICKET_INVITE_SMS_COUNT = int(os.getenv("BKAPP_TICKET_INVITE_SMS_COUNT", 10))

# 系统账户
SYSTEM_CALL_USER = "admin"
SYSTEM_USE_API_ACCOUNT = os.environ.get("SYSTEM_USE_API_ACCOUNT", "admin")

# 自动过单
try:
    AUTO_APPROVE_TIME = int(os.environ.get("BKAPP_AUTO_APPROVE_TIME", 5))
except Exception:
    AUTO_APPROVE_TIME = 5

# 语音通知
OPEN_VOICE_NOTICE = os.getenv("BKAPP_OPEN_VOICE_NOTICE", "false").lower() == "true"

# 通知
CONTENT_CREATOR_WITH_TRANSLATION = (
    os.getenv("CONTENT_CREATOR_WITH_TRANSLATION", "true").lower() == "true"
)
ENABLE_NOTIFY_ROUTER = os.getenv("BKAPP_ENABLE_NOTIFY_ROUTER", False)
NOTIFY_ROUTER_NAME = os.getenv("BKAPP_NOTIFY_ROUTER_NAME", "router")
CLOSE_EVERY_DAY_TICKET_NOTIFY = bool(
    os.getenv("BKAPP_CLOSE_EVERY_DAY_TICKET_NOTIFY", False)
)

# 框架
IS_BKUI_HISTORY_MODE = False
IS_AJAX_PLAIN_MODE = True
TEST_RUNNER = "itsm.tests.runner.ItsmTestRunner"

# 性能分析
try:
    NEED_PROFILE = bool(int(os.environ.get("BKAPP_NEED_PROFILE", False)))
except Exception:
    NEED_PROFILE = False
