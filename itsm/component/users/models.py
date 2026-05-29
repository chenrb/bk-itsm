# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The username field must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField("用户名", max_length=128, unique=True, db_index=True)
    nickname = models.CharField("昵称", max_length=255, blank=True, default="")
    chname = models.CharField("中文名", max_length=255, blank=True, default="")
    phone = models.CharField("电话", max_length=32, blank=True, default="")
    email = models.EmailField("邮箱", blank=True, default="")
    is_staff = models.BooleanField("后台访问权限", default=False)
    is_active = models.BooleanField("启用", default=True)
    date_joined = models.DateTimeField("注册时间", auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users_user"
        verbose_name = "用户"

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        return self.nickname or self.chname or self.username


class UserProperty(models.Model):
    """兼容 blueapps UserProperty"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    key = models.CharField(max_length=128)
    value = models.TextField(blank=True, default="")

    class Meta:
        db_table = "users_user_property"
        unique_together = ("user", "key")
