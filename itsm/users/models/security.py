# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class SecurityPolicy(models.Model):
    """安全策略，存储在数据库中，运行时可修改。"""

    CATEGORY_CHOICES = (
        ("password", _("密码策略")),
        ("login", _("登录策略")),
        ("session", _("会话策略")),
    )

    key = models.CharField(
        _("策略键"), max_length=128, unique=True, help_text=_("如 password_min_length")
    )
    value = models.JSONField(_("策略值"), help_text=_("JSON 格式，支持 int/bool/str"))
    category = models.CharField(_("策略分类"), max_length=32, choices=CATEGORY_CHOICES)
    description = models.TextField(_("描述"), blank=True, default="")
    is_builtin = models.BooleanField(_("内置策略"), default=True)

    class Meta:
        db_table = "users_security_policy"
        verbose_name = _("安全策略")
        verbose_name_plural = _("安全策略")
        ordering = ["category", "key"]

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get_value(cls, key, default=None):
        """便捷查询：返回指定策略键的值，不存在则返回 default。"""
        try:
            policy = cls.objects.get(key=key)
            return policy.value
        except cls.DoesNotExist:
            return default


class LoginAttempt(models.Model):
    """登录尝试记录，用于锁定策略。"""

    username = models.CharField(_("用户名"), max_length=128, db_index=True)
    ip_address = models.GenericIPAddressField(_("IP 地址"))
    attempts = models.IntegerField(_("失败次数"), default=0)
    locked_until = models.DateTimeField(_("锁定至"), null=True, blank=True)

    class Meta:
        db_table = "users_login_attempt"
        unique_together = ("username", "ip_address")
        verbose_name = _("登录尝试")
        verbose_name_plural = _("登录尝试")

    def __str__(self):
        return f"{self.username}@{self.ip_address} ({self.attempts})"


class PasswordHistory(models.Model):
    """密码历史记录，防止密码重复使用。"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_histories",
        verbose_name=_("用户"),
    )
    password_hash = models.CharField(_("密码哈希"), max_length=255)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        db_table = "users_password_history"
        verbose_name = _("密码历史")
        verbose_name_plural = _("密码历史")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.created_at}"
