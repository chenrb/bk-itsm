# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Department(MPTTModel):
    """部门模型，使用 MPTT 实现树形结构。"""

    name = models.CharField(_("部门名称"), max_length=255)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("上级部门"),
    )
    order = models.IntegerField(_("排序"), default=0)
    is_active = models.BooleanField(_("是否启用"), default=True)

    class MPTTMeta:
        order_insertion_by = ["order", "name"]

    class Meta:
        db_table = "users_department"
        verbose_name = _("部门")
        verbose_name_plural = _("部门")

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """计算属性：祖先路径拼接，如 '总公司/技术部/前端组'。"""
        ancestors = self.get_ancestors(include_self=True)
        return "/".join(a.name for a in ancestors)

    @property
    def has_children(self):
        return self.get_children().exists()


class DeptMembership(models.Model):
    """用户-部门关联中间表，支持多部门归属。"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dept_memberships",
        verbose_name=_("用户"),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="dept_memberships",
        verbose_name=_("部门"),
    )
    is_primary = models.BooleanField(_("是否主部门"), default=False)

    class Meta:
        db_table = "users_dept_membership"
        unique_together = ("user", "department")
        verbose_name = _("部门成员")
        verbose_name_plural = _("部门成员")

    def __str__(self):
        return f"{self.user} - {self.department}"
