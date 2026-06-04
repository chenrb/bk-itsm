# -*- coding: utf-8 -*-
"""
Unit tests for resolve_processors() and User.has_permission().
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django

django.setup()

from django.test import TestCase, override_settings

from itsm.users.models import (
    Department,
    DeptMembership,
    Permission,
    Role,
    User,
    UserGroup,
)
from itsm.users.resolvers import resolve_processors


@override_settings(
    AUTH_PASSWORD_VALIDATORS=[],
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
)
class ResolveProcessorsTest(TestCase):
    """Test resolve_processors() for each processor type."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django.core.management import call_command

        call_command("migrate", "--run-syncdb", verbosity=0)

    def setUp(self):
        self.user1 = User.objects.create(username="zhangsan", chname="张三")
        self.user2 = User.objects.create(username="lisi", chname="李四")
        self.user3 = User.objects.create(username="wangwu", chname="王五", is_active=False)

    def test_person_type(self):
        """PERSON: 直接拆分 username。"""
        result = resolve_processors("PERSON", "zhangsan,lisi")
        self.assertEqual(sorted(result), sorted(["zhangsan", "lisi"]))

    def test_person_empty(self):
        """PERSON: 空 param 返回空列表。"""
        result = resolve_processors("PERSON", "")
        self.assertEqual(result, [])

    def test_general_type(self):
        """GENERAL: 从 UserGroup.members 解析。"""
        group = UserGroup.objects.create(name="运维组", group_key="TEST_OPS")
        group.members.add(self.user1, self.user2)
        result = resolve_processors("GENERAL", str(group.id))
        self.assertEqual(sorted(result), sorted(["zhangsan", "lisi"]))

    def test_general_filters_inactive(self):
        """GENERAL: 过滤 is_active=False 的用户。"""
        group = UserGroup.objects.create(name="测试组", group_key="TEST_FILT")
        group.members.add(self.user1, self.user3)
        result = resolve_processors("GENERAL", str(group.id))
        self.assertEqual(result, ["zhangsan"])

    def test_organization_type(self):
        """ORGANIZATION: 递归查询部门用户。"""
        dept = Department.objects.create(name="技术部")
        DeptMembership.objects.create(user=self.user1, department=dept, is_primary=True)
        result = resolve_processors("ORGANIZATION", str(dept.id))
        self.assertEqual(result, ["zhangsan"])

    def test_starter_leader_type(self):
        """STARTER_LEADER: 解析直属上级。"""
        self.user1.leader = self.user2
        self.user1.save()
        result = resolve_processors("STARTER_LEADER", "zhangsan")
        self.assertEqual(result, ["lisi"])

    def test_starter_leader_no_leader(self):
        """STARTER_LEADER: 无 leader 返回空。"""
        result = resolve_processors("STARTER_LEADER", "zhangsan")
        self.assertEqual(result, [])

    def test_empty_type(self):
        """EMPTY: 返回空列表。"""
        result = resolve_processors("EMPTY", "")
        self.assertEqual(result, [])

    def test_by_assignor_type(self):
        """BY_ASSIGNOR: 返回空列表（由调用方处理）。"""
        result = resolve_processors("BY_ASSIGNOR", "")
        self.assertEqual(result, [])

    def test_open_type(self):
        """OPEN: 返回空列表（由调用方处理）。"""
        result = resolve_processors("OPEN", "")
        self.assertEqual(result, [])

    def test_api_type(self):
        """API: 返回空列表（由调用方处理）。"""
        result = resolve_processors("API", "")
        self.assertEqual(result, [])

    def test_variable_type(self):
        """VARIABLE: 返回空列表（由调用方处理）。"""
        result = resolve_processors("VARIABLE", "")
        self.assertEqual(result, [])

    def test_unsupported_type_raises(self):
        """不支持的类型抛出 ValueError。"""
        with self.assertRaises(ValueError):
            resolve_processors("CMDB", "some_param")


@override_settings(
    AUTH_PASSWORD_VALIDATORS=[],
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
)
class UserPermissionTest(TestCase):
    """Test User.has_permission() and Role permission checks."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django.core.management import call_command

        call_command("migrate", "--run-syncdb", verbosity=0)

    def setUp(self):
        self.user = User.objects.create(username="testuser", chname="测试用户")
        self.superuser = User.objects.create(
            username="admin", chname="管理员", is_superuser=True
        )
        self.perm = Permission.objects.create(
            code="feature:system:user-manage",
            name="用户管理",
            category="system",
            permission_type="feature",
        )
        self.role = Role.objects.create(name="管理员角色", role_key="TEST_ADMIN")
        self.role.permissions.add(self.perm)

    def test_superuser_has_all_permissions(self):
        """is_superuser 的用户自动拥有全部权限。"""
        self.assertTrue(self.superuser.has_permission("feature:system:user-manage"))
        self.assertTrue(self.superuser.has_permission("any:random:code"))

    def test_user_has_permission_via_role(self):
        """通过 Role 成员关系拥有权限。"""
        self.role.members.add(self.user)
        self.assertTrue(self.user.has_permission("feature:system:user-manage"))

    def test_user_lacks_permission(self):
        """未分配角色的用户没有权限。"""
        self.assertFalse(self.user.has_permission("feature:system:user-manage"))

    def test_role_has_permission(self):
        """Role.has_permission() 正确检查权限。"""
        self.assertTrue(self.role.has_permission("feature:system:user-manage"))
        self.assertFalse(self.role.has_permission("feature:system:role-manage"))

    def test_role_is_itsm_superuser(self):
        """Role.is_itsm_superuser() 类方法。"""
        su_role = Role.objects.create(name="超级管理员", role_key="SUPERUSER")
        su_role.members.add(self.user)
        self.assertTrue(Role.is_itsm_superuser("testuser"))
        self.assertFalse(Role.is_itsm_superuser("admin"))  # admin not in SUPERUSER role

    def test_role_get_access_by_user(self):
        """Role.get_access_by_user() 返回 role_key 列表。"""
        self.role.members.add(self.user)
        access = Role.get_access_by_user("testuser")
        self.assertIn("TEST_ADMIN", access)
