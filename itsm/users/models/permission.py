# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    """权限模型，编码格式 {type}:{module}:{action}。"""

    PERMISSION_TYPE_CHOICES = (
        ("page", _("页面")),
        ("button", _("按钮")),
        ("feature", _("功能")),
    )
    CATEGORY_CHOICES = (
        ("workflow", _("流程管理")),
        ("ticket", _("工单管理")),
        ("service", _("服务管理")),
        ("sla", _("SLA 管理")),
        ("system", _("系统管理")),
        ("project", _("项目管理")),
        ("task", _("任务管理")),
    )

    code = models.CharField(
        _("权限编码"),
        max_length=128,
        unique=True,
        help_text=_("格式: {type}:{module}:{action}，如 feature:system:user-manage"),
    )
    name = models.CharField(_("权限名称"), max_length=255)
    category = models.CharField(
        _("业务分类"), max_length=64, choices=CATEGORY_CHOICES
    )
    permission_type = models.CharField(
        _("权限类型"), max_length=16, choices=PERMISSION_TYPE_CHOICES
    )
    description = models.TextField(_("描述"), blank=True, default="")
    is_builtin = models.BooleanField(_("内置权限"), default=False)

    class Meta:
        db_table = "users_permission"
        verbose_name = _("权限")
        verbose_name_plural = _("权限")
        ordering = ["category", "permission_type", "code"]

    def __str__(self):
        return f"{self.code} ({self.name})"
