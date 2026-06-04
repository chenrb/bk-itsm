# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError

from itsm.users.models import UserGroup
from itsm.users.serializers import UserGroupSerializer


class UserGroupViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserGroup.objects.filter(is_deleted=False)
    serializer_class = UserGroupSerializer
    filterset_fields = ("is_builtin", "project_key")
    search_fields = ("name", "group_key")

    def check_group_permission(self, instance=None):
        """Owner 或有 feature:system:group-manage 权限可编辑。"""
        user = self.request.user
        if user.is_superuser or user.has_permission("feature:system:group-manage"):
            return True
        if instance and instance.owners.filter(pk=user.pk).exists():
            return True
        raise PermissionDenied(_("无角色组编辑权限"))

    def perform_create(self, serializer):
        if not (
            self.request.user.is_superuser
            or self.request.user.has_permission("feature:system:group-manage")
        ):
            raise PermissionDenied(_("无角色组创建权限"))
        serializer.save(creator=self.request.user.username)

    def perform_update(self, instance):
        self.check_group_permission(instance)
        super().perform_update(instance)

    def perform_destroy(self, instance):
        if not (
            self.request.user.is_superuser
            or self.request.user.has_permission("feature:system:group-manage")
        ):
            raise PermissionDenied(_("无角色组删除权限"))
        if instance.is_builtin:
            raise ValidationError(_("内置角色组不可删除"))
        instance.soft_delete()
