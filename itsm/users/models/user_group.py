# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserGroup(models.Model):
    """角色组（处理人分组），用于工作流处理人分配。与 Role（权限授权）分离。"""

    name = models.CharField(_("角色组名称"), max_length=255)
    group_key = models.CharField(
        _("角色组标识"), max_length=128, unique=True, help_text=_("唯一标识，如 DEV, OPS")
    )
    desc = models.TextField(_("描述"), blank=True, default="")
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="user_groups",
        blank=True,
        verbose_name=_("组成员"),
    )
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="owned_user_groups",
        blank=True,
        verbose_name=_("组负责人"),
    )
    is_builtin = models.BooleanField(_("内置角色组"), default=False)
    project_key = models.CharField(
        _("项目标识"), max_length=64, default="0", help_text=_("默认 '0' 表示全局")
    )
    # 审计字段
    creator = models.CharField(_("创建人"), max_length=128, blank=True, default="")
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("更新人"), max_length=128, blank=True, default="")
    is_deleted = models.BooleanField(_("已删除"), default=False)
    end_at = models.DateTimeField(_("删除时间"), null=True, blank=True)

    class Meta:
        db_table = "users_user_group"
        verbose_name = _("角色组")
        verbose_name_plural = _("角色组")

    def __str__(self):
        return f"{self.name} ({self.group_key})"

    def soft_delete(self):
        self.is_deleted = True
        self.end_at = timezone.now()
        self.save(update_fields=["is_deleted", "end_at", "update_at"])
