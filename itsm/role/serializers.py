# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers

from itsm.component.constants import (
    ACCESS_NAMES,
    LEN_MIDDLE,
    LEN_NORMAL,
    LEN_SHORT,
)
from itsm.component.drf.serializers import DynamicFieldsModelSerializer
from itsm.component.utils.basic import list_by_separator
from itsm.role.models import RoleType, UserRole

from .validators import UserRoleValidator

BKUser = get_user_model()


class RoleTypeSerializer(serializers.ModelSerializer):
    """角色类型序列化"""

    id = serializers.IntegerField(required=False)
    type = serializers.CharField(required=True, max_length=LEN_NORMAL)
    name = serializers.CharField(
        required=True,
        max_length=LEN_NORMAL,
        error_messages={"blank": _("请输入角色名！")},
    )
    desc = serializers.CharField(required=False, max_length=LEN_MIDDLE)

    class Meta:
        model = RoleType
        fields = ("id", "type", "name", "desc")

    def to_representation(self, instance):
        data = super(RoleTypeSerializer, self).to_representation(instance)
        data["name"] = _(data["name"])
        data["desc"] = _(data["desc"])
        return data


class UserRoleSerializer(DynamicFieldsModelSerializer):
    """用户角色序列化"""

    id = serializers.IntegerField(required=False)
    role_type = serializers.CharField(required=True, max_length=LEN_NORMAL)
    name = serializers.CharField(
        required=True,
        max_length=LEN_NORMAL,
        error_messages={"blank": _("请输入自定义角色名")},
    )
    members = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=False,
        error_messages={"empty": _("请指定角色下的人员")},
    )
    owners = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    access = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=LEN_MIDDLE
    )
    creator = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=LEN_NORMAL
    )
    role_key = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=LEN_MIDDLE
    )
    desc = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=LEN_MIDDLE
    )
    project_key = serializers.CharField(required=True, max_length=LEN_SHORT)

    class Meta:
        model = UserRole
        fields = (
            "id",
            "role_type",
            "name",
            "members",
            "project_key",
            "owners",
            "access",
            "desc",
            "role_key",
            "creator",
            "is_builtin",
        )
        create_only_fields = ("project_key", "is_builtin", "creator")

    def __init__(self, *args, **kwargs):
        super(UserRoleSerializer, self).__init__(*args, **kwargs)
        self.validators = [UserRoleValidator(self.instance)]

    def to_internal_value(self, data):
        data = super(UserRoleSerializer, self).to_internal_value(data)

        data["role_type"] = data.get("role_type", "").upper()

        return data

    def to_representation(self, instance):
        data = super(UserRoleSerializer, self).to_representation(instance)

        data["owners"] = list(
            instance.owners.values_list("username", flat=True)
        )
        data["name"] = _(data["name"])
        data["desc"] = _(data["desc"] or "")

        if "members" in data:
            member_list = list(
                instance.members.values_list("username", flat=True)
            )
            data["count"] = len(member_list)
            data["members"] = member_list

        if "access" in data:
            data["access_name"] = _(
                ",".join(
                    [
                        _(ACCESS_NAMES.get(key, ""))
                        for key in list_by_separator(data.get("access"), ",")
                    ]
                )
            )
        return self.update_auth_actions(instance, data)

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        owners = validated_data.pop("owners", [])
        instance = super(UserRoleSerializer, self).create(validated_data)
        User = get_user_model()
        if members:
            instance.members.set(User.objects.filter(username__in=members))
        if owners:
            instance.owners.set(User.objects.filter(username__in=owners))
        return instance

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        owners = validated_data.pop("owners", None)
        instance = super(UserRoleSerializer, self).update(instance, validated_data)
        User = get_user_model()
        if members is not None:
            instance.members.set(User.objects.filter(username__in=members))
        if owners is not None:
            instance.owners.set(User.objects.filter(username__in=owners))
        return instance
