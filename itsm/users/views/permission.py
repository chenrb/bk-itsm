# -*- coding: utf-8 -*-
from rest_framework import mixins, viewsets

from itsm.users.models import Permission
from itsm.users.serializers import PermissionSerializer


class PermissionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filterset_fields = ("category", "permission_type", "is_builtin")
    search_fields = ("code", "name")
