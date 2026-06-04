# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from itsm.users.models import Department, DeptMembership
from itsm.users.serializers import (
    DeptMembershipSerializer,
    DepartmentSerializer,
)


class DepartmentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def check_department_manage_permission(self):
        if not (
            self.request.user.is_superuser
            or self.request.user.has_permission("feature:system:department-manage")
        ):
            raise PermissionDenied(_("无部门管理权限"))

    def perform_create(self, serializer):
        self.check_department_manage_permission()
        serializer.save()

    def perform_update(self, instance):
        self.check_department_manage_permission()
        super().perform_update(instance)

    def perform_destroy(self, instance):
        self.check_department_manage_permission()
        if instance.has_children:
            raise ValidationError(_("该部门下有子部门，无法删除"))
        if instance.dept_memberships.exists():
            raise ValidationError(_("该部门下有成员，无法删除"))
        instance.delete()

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        """获取部门成员列表。"""
        department = self.get_object()
        memberships = DeptMembership.objects.filter(
            department=department
        ).select_related("user")
        page = self.paginate_queryset(memberships)
        if page is not None:
            serializer = DeptMembershipSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = DeptMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
