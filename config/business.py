# -*- coding: utf-8 -*-
"""业务环境变量配置"""
import os

# 用户查询适配器（替代原 adapter/config/sites/open/api）
ADAPTER_API = __import__(
    "itsm.component.utils.user_adapter", fromlist=["get_batch_users", "get_all_users"]
)

# business_rules
DEFAULT_VARIABLE_NAME = "variable_by_name"

# 初始化管理员
ITSM_ADMIN = os.environ.get("ITSM_ADMIN", "")
INIT_SUPERUSER = set(
    ["admin"] + [u for u in ITSM_ADMIN.split(",") if u]
)

# 自定义
CLOSE_NOTIFY = os.environ.get("CLOSE_NOTIFY", None)

# 用户管理
USER_DEFAULT_FIELDS = "id,username,display_name,domain,logo,category_id,category_name"
USER_WHITE_FIELDS = (
    os.environ.get("USER_WHITE_FIELDS") or USER_DEFAULT_FIELDS
).split(",")

# 短信评价
IS_USE_INVITE_SMS = os.environ.get("IS_USE_INVITE_SMS", None)
AUTO_COMMENT_DAYS = int(os.environ.get("AUTO_COMMENT_DAYS", 3))
TICKET_INVITE_SMS_COUNT = int(os.getenv("TICKET_INVITE_SMS_COUNT", 10))

# 系统账户
SYSTEM_CALL_USER = "admin"
SYSTEM_USE_API_ACCOUNT = os.environ.get("SYSTEM_USE_API_ACCOUNT", "admin")

# 自动过单
try:
    AUTO_APPROVE_TIME = int(os.environ.get("AUTO_APPROVE_TIME", 5))
except Exception:
    AUTO_APPROVE_TIME = 5

# 语音通知
OPEN_VOICE_NOTICE = os.getenv("OPEN_VOICE_NOTICE", "false").lower() == "true"

# 通知
CONTENT_CREATOR_WITH_TRANSLATION = (
    os.getenv("CONTENT_CREATOR_WITH_TRANSLATION", "true").lower() == "true"
)
ENABLE_NOTIFY_ROUTER = os.getenv("ENABLE_NOTIFY_ROUTER", False)
NOTIFY_ROUTER_NAME = os.getenv("NOTIFY_ROUTER_NAME", "router")
CLOSE_EVERY_DAY_TICKET_NOTIFY = bool(
    os.getenv("CLOSE_EVERY_DAY_TICKET_NOTIFY", False)
)

# 框架
IS_BKUI_HISTORY_MODE = False
IS_AJAX_PLAIN_MODE = True
