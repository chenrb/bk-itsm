# -*- coding: utf-8 -*-
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from itsm.users.models import LoginAttempt, SecurityPolicy
from itsm.users.serializers import (
    LoginAttemptSerializer,
    SecurityPolicySerializer,
    UnlockSerializer,
)


class SecurityPolicyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = SecurityPolicy.objects.all()
    serializer_class = SecurityPolicySerializer
    filterset_fields = ("category",)

    def check_security_manage_permission(self):
        if not (
            self.request.user.is_superuser
            or self.request.user.has_permission("feature:system:security-manage")
        ):
            raise PermissionDenied(_("无安全策略管理权限"))

    def perform_update(self, instance):
        self.check_security_manage_permission()
        super().perform_update(instance)

    @action(detail=False, methods=["post"])
    def unlock(self, request):
        """管理员解锁被锁定的账户。"""
        self.check_security_manage_permission()
        serializer = UnlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        deleted_count, _ = LoginAttempt.objects.filter(
            username=username
        ).delete()
        return Response(
            {"result": True, "message": _("已解锁用户 %(username)s") % {"username": username}}
        )

    @action(detail=False, methods=["get"])
    def locked_accounts(self, request):
        """查看当前被锁定的账户列表。"""
        self.check_security_manage_permission()
        locked = LoginAttempt.objects.filter(
            locked_until__gt=timezone.now()
        )
        serializer = LoginAttemptSerializer(locked, many=True)
        return Response(serializer.data)
