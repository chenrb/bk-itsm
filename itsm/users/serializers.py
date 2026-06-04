# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers

from itsm.users.models import (
    Department,
    DeptMembership,
    LoginAttempt,
    PasswordHistory,
    Permission,
    Role,
    SecurityPolicy,
    UserGroup,
    UserProperty,
)

User = get_user_model()


# ── User ──────────────────────────────────────────────────


class UserPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProperty
        fields = ("key", "value")


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(
        source="department.name", read_only=True, default=""
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "nickname",
            "chname",
            "email",
            "phone",
            "leader",
            "department",
            "department_name",
            "display_name",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined", "display_name", "is_superuser")
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("旧密码不正确"))
        return value


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)


# ── Department ────────────────────────────────────────────


class DepartmentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    has_children = serializers.BooleanField(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
            "parent",
            "order",
            "is_active",
            "full_name",
            "has_children",
            "member_count",
        )
        read_only_fields = ("id", "full_name", "has_children", "member_count")

    def get_member_count(self, obj):
        return obj.dept_memberships.count()


class DeptMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    chname = serializers.CharField(source="user.chname", read_only=True)

    class Meta:
        model = DeptMembership
        fields = ("id", "user", "username", "chname", "department", "is_primary")


# ── Permission ────────────────────────────────────────────


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            "id",
            "code",
            "name",
            "category",
            "permission_type",
            "description",
            "is_builtin",
        )
        read_only_fields = ("id",)


# ── Role ──────────────────────────────────────────────────


class RoleSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field="username",
        queryset=User.objects.all(),
        required=False,
    )
    owners = serializers.SlugRelatedField(
        many=True,
        slug_field="username",
        queryset=User.objects.all(),
        required=False,
    )
    permissions = serializers.SlugRelatedField(
        many=True,
        slug_field="code",
        queryset=Permission.objects.all(),
        required=False,
    )
    member_count = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "role_key",
            "desc",
            "members",
            "owners",
            "permissions",
            "is_builtin",
            "creator",
            "create_at",
            "update_at",
            "updated_by",
            "member_count",
            "permission_count",
        )
        read_only_fields = (
            "id",
            "create_at",
            "update_at",
            "member_count",
            "permission_count",
        )

    def get_member_count(self, obj):
        return obj.members.count()

    def get_permission_count(self, obj):
        return obj.permissions.count()


# ── UserGroup ─────────────────────────────────────────────


class UserGroupSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field="username",
        queryset=User.objects.all(),
        required=False,
    )
    owners = serializers.SlugRelatedField(
        many=True,
        slug_field="username",
        queryset=User.objects.all(),
        required=False,
    )
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = UserGroup
        fields = (
            "id",
            "name",
            "group_key",
            "desc",
            "members",
            "owners",
            "is_builtin",
            "project_key",
            "creator",
            "create_at",
            "update_at",
            "updated_by",
            "member_count",
        )
        read_only_fields = ("id", "create_at", "update_at", "member_count")

    def get_member_count(self, obj):
        return obj.members.count()


# ── SecurityPolicy ────────────────────────────────────────


class SecurityPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityPolicy
        fields = ("id", "key", "value", "category", "description", "is_builtin")
        read_only_fields = ("id", "key", "category", "is_builtin")


class UnlockSerializer(serializers.Serializer):
    username = serializers.CharField()


# ── LoginAttempt (for locked accounts) ────────────────────


class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = ("id", "username", "ip_address", "attempts", "locked_until")
