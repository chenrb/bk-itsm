# -*- coding: utf-8 -*-
"""
自定义密码验证器，从 SecurityPolicy 读取策略。
注册在 Django AUTH_PASSWORD_VALIDATORS 中。
"""
import re

from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import ngettext


class SecurityPolicyPasswordValidator:
    """从数据库 SecurityPolicy 读取密码策略并验证。"""

    def validate(self, password, user=None):
        from itsm.users.models import SecurityPolicy

        errors = []

        min_length = SecurityPolicy.get_value("password_min_length", 8)
        if len(password) < min_length:
            errors.append(
                _("密码长度不能少于 %(min_length)s 个字符")
                % {"min_length": min_length}
            )

        if SecurityPolicy.get_value("password_require_uppercase", True):
            if not re.search(r"[A-Z]", password):
                errors.append(_("密码必须包含大写字母"))

        if SecurityPolicy.get_value("password_require_lowercase", True):
            if not re.search(r"[a-z]", password):
                errors.append(_("密码必须包含小写字母"))

        if SecurityPolicy.get_value("password_require_digit", True):
            if not re.search(r"\d", password):
                errors.append(_("密码必须包含数字"))

        if SecurityPolicy.get_value("password_require_special", False):
            if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,<.>/?`~]', password):
                errors.append(_("密码必须包含特殊字符"))

        if errors:
            raise ValueError(errors)

    def get_help_text(self):
        from itsm.users.models import SecurityPolicy

        min_length = SecurityPolicy.get_value("password_min_length", 8)
        parts = [_("密码长度至少 %(min_length)s 个字符") % {"min_length": min_length}]
        if SecurityPolicy.get_value("password_require_uppercase", True):
            parts.append(_("包含大写字母"))
        if SecurityPolicy.get_value("password_require_lowercase", True):
            parts.append(_("包含小写字母"))
        if SecurityPolicy.get_value("password_require_digit", True):
            parts.append(_("包含数字"))
        if SecurityPolicy.get_value("password_require_special", False):
            parts.append(_("包含特殊字符"))
        return "，".join(parts)
