# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """角色模型（权限授权）。与 UserGroup（处理人分组）分离。"""

    name = models.CharField(_("角色名称"), max_length=255)
    role_key = models.CharField(
        _("角色标识"), max_length=128, unique=True, help_text=_("唯一标识，如 SUPERUSER")
    )
    desc = models.TextField(_("描述"), blank=True, default="")
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="auth_roles",
        blank=True,
        verbose_name=_("角色成员"),
    )
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="owned_auth_roles",
        blank=True,
        verbose_name=_("角色负责人"),
    )
    permissions = models.ManyToManyField(
        "users.Permission",
        related_name="roles",
        blank=True,
        verbose_name=_("权限列表"),
    )
    is_builtin = models.BooleanField(_("内置角色"), default=False)
    # 审计字段
    creator = models.CharField(_("创建人"), max_length=128, blank=True, default="")
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(_("更新时间"), auto_now=True)
    updated_by = models.CharField(_("更新人"), max_length=128, blank=True, default="")
    is_deleted = models.BooleanField(_("已删除"), default=False)
    end_at = models.DateTimeField(_("删除时间"), null=True, blank=True)

    class Meta:
        db_table = "users_role"
        verbose_name = _("角色")
        verbose_name_plural = _("角色")

    def __str__(self):
        return f"{self.name} ({self.role_key})"

    def soft_delete(self):
        self.is_deleted = True
        self.end_at = timezone.now()
        self.save(update_fields=["is_deleted", "end_at", "update_at"])

    def has_permission(self, code):
        """检查角色是否拥有指定权限编码。"""
        return self.permissions.filter(code=code).exists()

    @classmethod
    def is_itsm_superuser(cls, username):
        """兼容旧接口：检查用户是否为超级管理员。"""
        return cls.objects.filter(
            role_key="SUPERUSER", is_deleted=False, members__username=username
        ).exists()

    @classmethod
    def is_workflow_manager(cls, username):
        """兼容旧接口：检查用户是否为流程管理员。"""
        return cls.objects.filter(
            role_key="WORKFLOW_MANAGER",
            is_deleted=False,
            members__username=username,
        ).exists()

    @classmethod
    def is_statics_manager(cls, username):
        """兼容旧接口：检查用户是否为统计查看员。"""
        return cls.objects.filter(
            role_key="STATICS_MANAGER",
            is_deleted=False,
            members__username=username,
        ).exists()

    @classmethod
    def get_access_by_user(cls, username):
        """兼容旧接口：返回用户拥有的角色 role_key 列表。"""
        return list(
            cls.objects.filter(
                is_deleted=False, members__username=username
            ).values_list("role_key", flat=True)
        )
