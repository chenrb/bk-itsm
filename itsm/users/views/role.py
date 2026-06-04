# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from itsm.users.models import Role
from itsm.users.serializers import RoleSerializer


class RoleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Role.objects.filter(is_deleted=False)
    serializer_class = RoleSerializer
    filterset_fields = ("is_builtin",)
    search_fields = ("name", "role_key")

    def check_role_manage_permission(self):
        if not (
            self.request.user.is_superuser
            or self.request.user.has_permission("feature:system:role-manage")
        ):
            raise PermissionDenied(_("无角色管理权限"))

    def perform_create(self, serializer):
        self.check_role_manage_permission()
        serializer.save(creator=self.request.user.username)

    def perform_update(self, instance):
        self.check_role_manage_permission()
        super().perform_update(instance)

    def perform_destroy(self, instance):
        self.check_role_manage_permission()
        if instance.is_builtin:
            raise ValidationError(_("内置角色不可删除"))
        instance.soft_delete()
