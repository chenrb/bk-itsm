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
    LEN_XX_LONG,
    LEN_SHORT,
)
from itsm.component.drf.serializers import DynamicFieldsModelSerializer
from itsm.component.utils.basic import dotted_name, list_by_separator, normal_name
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
    members = serializers.CharField(
        required=True,
        max_length=LEN_XX_LONG,
        error_messages={"blank": _("请指定角色下的人员")},
    )
    owners = serializers.CharField(
        required=False, max_length=LEN_XX_LONG, allow_blank=True
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
        data["members"] = dotted_name(data["members"])

        if "owners" in data:
            data["owners"] = dotted_name(data["owners"])

        return data

    def to_representation(self, instance):
        data = super(UserRoleSerializer, self).to_representation(instance)

        data["owners"] = normal_name(data.get("owners"))
        data["name"] = _(data["name"])
        data["desc"] = _(data["desc"] or "")

        # 支持动态字段渲染
        if "members" in data:
            members = data.get("members")
            data["count"] = len(list_by_separator(members))
            data["members"] = normal_name(members)

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

    def update(self, instance, validated_data):
        instance = super(UserRoleSerializer, self).update(instance, validated_data)
        return instance
