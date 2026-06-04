# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from itsm.users.models import (
    Department,
    DeptMembership,
    LoginAttempt,
    PasswordHistory,
    Permission,
    Role,
    SecurityPolicy,
    User,
    UserGroup,
    UserProperty,
)


# ── User ──────────────────────────────────────────────────


class UserPropertyInline(admin.TabularInline):
    model = UserProperty
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "chname", "email", "department", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "department")
    search_fields = ("username", "chname", "email")
    inlines = [UserPropertyInline]
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "chname",
                    "nickname",
                    "phone",
                    "leader",
                    "department",
                )
            },
        ),
    )


# ── Department ────────────────────────────────────────────


class DeptMembershipInline(admin.TabularInline):
    model = DeptMembership
    extra = 0


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    inlines = [DeptMembershipInline]


@admin.register(DeptMembership)
class DeptMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("user__username", "department__name")


# ── Permission ────────────────────────────────────────────


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "permission_type", "is_builtin")
    list_filter = ("category", "permission_type", "is_builtin")
    search_fields = ("code", "name")
    readonly_fields = ("code",) if True else ()


# ── Role ──────────────────────────────────────────────────


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "role_key", "is_builtin", "is_deleted", "create_at")
    list_filter = ("is_builtin", "is_deleted")
    search_fields = ("name", "role_key")
    filter_horizontal = ("members", "owners", "permissions")


# ── UserGroup ─────────────────────────────────────────────


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "group_key", "is_builtin", "project_key", "create_at")
    list_filter = ("is_builtin", "project_key", "is_deleted")
    search_fields = ("name", "group_key")
    filter_horizontal = ("members", "owners")


# ── SecurityPolicy ────────────────────────────────────────


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "category", "is_builtin")
    list_filter = ("category", "is_builtin")
    search_fields = ("key",)
    readonly_fields = ("key", "category", "is_builtin")


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("username", "ip_address", "attempts", "locked_until")
    search_fields = ("username",)


@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username",)
    readonly_fields = ("user", "password_hash", "created_at")
