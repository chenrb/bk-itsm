# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from itsm.users.models import PasswordHistory, SecurityPolicy
from itsm.users.serializers import (
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ("username", "email", "department", "is_active")
    search_fields = ("username", "chname")

    def get_permissions(self):
        # List and retrieve are available to any authenticated user
        if self.action in ("list", "retrieve", "me", "permissions"):
            return []
        # Write actions require feature:system:user-manage
        return []  # Permission checked inline for flexibility

    def check_user_manage_permission(self):
        if not (
            self.request.user.is_superuser
            or self.request.user.has_permission("feature:system:user-manage")
        ):
            raise PermissionDenied(_("无用户管理权限"))

    def perform_create(self, serializer):
        self.check_user_manage_permission()
        serializer.save()

    def perform_update(self, instance):
        self.check_user_manage_permission()
        super().perform_update(instance)

    def perform_destroy(self, instance):
        self.check_user_manage_permission()
        instance.is_active = False
        instance.save()

    @action(detail=False, methods=["get"])
    def me(self, request):
        """当前用户信息。"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def permissions(self, request):
        """当前用户的权限编码列表。"""
        if request.user.is_superuser:
            from itsm.users.data.permissions import BUILTIN_PERMISSIONS

            codes = [code for code, _, _, _ in BUILTIN_PERMISSIONS]
        else:
            from itsm.users.models.role import Role

            codes = list(
                Role.objects.filter(
                    members=request.user, is_deleted=False
                )
                .values_list("permissions__code", flat=True)
                .distinct()
            )
        return Response({"permissions": codes})

    @action(detail=True, methods=["post"])
    def change_password(self, request, pk=None):
        """用户自助修改密码。"""
        user = self.get_object()
        # Only allow self or admin
        if request.user.pk != user.pk:
            self.check_user_manage_permission()
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data["new_password"]
        # Password history check
        _check_password_history(user, new_password)
        # Store old password in history
        PasswordHistory.objects.create(
            user=user, password_hash=user.password
        )
        user.set_password(new_password)
        user.save()
        return Response({"result": True, "message": _("密码修改成功")})

    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        """管理员重置密码。"""
        self.check_user_manage_permission()
        user = self.get_object()
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data["new_password"]
        # Password history check
        _check_password_history(user, new_password)
        PasswordHistory.objects.create(
            user=user, password_hash=user.password
        )
        user.set_password(new_password)
        user.save()
        return Response({"result": True, "message": _("密码重置成功")})


def _check_password_history(user, new_password):
    """检查新密码是否在最近 N 次历史中重复使用。"""
    from django.contrib.auth.hashers import check_password

    history_count = SecurityPolicy.get_value("password_history_count", 0)
    if history_count and history_count > 0:
        recent = PasswordHistory.objects.filter(user=user).order_by("-created_at")[
            :history_count
        ]
        for record in recent:
            if check_password(new_password, record.password_hash):
                from django.utils.translation import ngettext
                from rest_framework.exceptions import ValidationError

                msg = ngettext(
                    "不能使用最近 %(count)d 次使用过的密码",
                    "不能使用最近 %(count)d 次使用过的密码",
                    history_count,
                ) % {"count": history_count}
                raise ValidationError({"new_password": msg})
