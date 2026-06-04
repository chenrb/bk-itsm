# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_("用户名不能为空"))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("超级用户必须设置 is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("超级用户必须设置 is_superuser=True"))
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _("用户名"), max_length=128, unique=True, db_index=True
    )
    nickname = models.CharField(_("昵称"), max_length=255, blank=True, default="")
    chname = models.CharField(
        _("中文名"), max_length=255, blank=True, default=""
    )
    email = models.EmailField(_("邮箱"), blank=True, default="")
    phone = models.CharField(_("电话"), max_length=32, blank=True, default="")
    leader = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
        verbose_name=_("直属上级"),
        help_text=_("用户的直属上级，用于工单 STARTER_LEADER / ASSIGN_LEADER 处理人解析"),
    )
    department = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_members",
        verbose_name=_("主部门"),
        help_text=_("用户的主要所属部门"),
    )
    is_staff = models.BooleanField(_("后台访问权限"), default=False)
    is_active = models.BooleanField(_("启用"), default=True)
    date_joined = models.DateTimeField(_("注册时间"), auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users_user"
        verbose_name = _("用户")
        verbose_name_plural = _("用户")

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        """显示名称优先级：nickname > chname > username"""
        return self.nickname or self.chname or self.username

    def get_property(self, key):
        """
        兼容旧代码通过 KV 表查询用户属性的模式。
        chname 直接返回字段值，不查 UserProperty。
        """
        if key == "chname":
            return self.chname
        try:
            prop = self.properties.get(key=key)
            return prop.value
        except UserProperty.DoesNotExist:
            return None

    def has_permission(self, code):
        """
        检查用户是否拥有指定权限编码。
        superuser 直接返回 True。
        聚合用户所属所有 Role 的 permissions 取并集。
        """
        if self.is_superuser:
            return True
        # Avoid circular import
        from itsm.users.models.role import Role

        return Role.objects.filter(
            members=self, is_deleted=False
        ).filter(
            permissions__code=code
        ).exists()


class UserProperty(models.Model):
    """兼容旧代码的 KV 属性存储。"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="properties",
        verbose_name=_("用户"),
    )
    key = models.CharField(_("属性键"), max_length=128)
    value = models.TextField(_("属性值"), blank=True, default="")

    class Meta:
        db_table = "users_user_property"
        unique_together = ("user", "key")
        verbose_name = _("用户属性")
        verbose_name_plural = _("用户属性")

    def __str__(self):
        return f"{self.user} - {self.key}"
