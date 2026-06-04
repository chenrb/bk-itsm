# -*- coding: utf-8 -*-
"""
内置角色组声明式定义。
格式: (group_key, name)
name 使用 gettext 支持多语言。
"""
from django.utils.translation import gettext_lazy as _

BUILTIN_USER_GROUPS = [
    ("DEV", _("开发")),
    ("PM", _("产品/开发经理")),
    ("OPT", _("运营")),
    ("OPS", _("运维")),
    ("TEST", _("测试")),
    ("GENERAL_6", _("变更经理")),
    ("GENERAL_7", _("故障派单员")),
    ("GENERAL_8", _("服务台小组")),
]
