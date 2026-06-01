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

from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.fields import empty

from itsm.component.constants import (
    EMPTY_STRING,
    LEN_LONG,
    LEN_NORMAL,
    ACTION_OPERATE,
    ACTION_CONFIRM,
    CREATE,
    SOPS_TEMPLATE_KEY,
    VERSION,
)
from itsm.component.drf.viewsets import ModelViewSet
from itsm.component.utils.basic import dotted_name, normal_name
from itsm.task.models import Task, TaskField, TaskLib, TaskLibTasks
from itsm.ticket.validators import regex_validate

from itsm.ticket.models.ticket import Ticket
from itsm.workflow.models import TaskSchema, TaskFieldSchema, TaskConfig
from itsm.task.validators import (
    TicketValidValidator,
    TaskOrdersValidator,
    TaskFieldBatchUpdateValidator,
    validate_task_fields,
)


class TaskFieldSerializer(serializers.ModelSerializer):
    """任务字段序列化"""

    meta = serializers.JSONField(required=False, initial={})
    choice = serializers.JSONField(required=False, initial=[])
    kv_relation = serializers.JSONField(required=False, initial={})
    related_fields = serializers.JSONField(required=False, initial={})
    show_conditions = serializers.JSONField(required=False, initial={})
    regex_config = serializers.JSONField(required=False, initial={})

    class Meta:
        model = TaskField
        fields = (
            "id",
            "key",
            "type",
            "choice",
            "name",
            "value",
            "display",
            "display_value",
            "show_result",
            "related_fields",
            "meta",
            "source_type",
            "source_uri",
            "kv_relation",
            "validate_type",
            "api_instance_id",
            "regex",
            "regex_config",
            "custom_regex",
            "default",
            "desc",
            "tips",
            "is_tips",
            "layout",
            "is_valid",
            "is_builtin",
            "show_conditions",
            "show_type",
            "is_readonly",
            "task_id",
            "stage",
            "sequence",
        )


class TaskSerializer(serializers.ModelSerializer):
    """任务序列化"""

    name = serializers.CharField(required=False, max_length=50, allow_blank=True)
    processors_type = serializers.CharField(
        required=False, allow_blank=True, max_length=LEN_LONG, default=EMPTY_STRING
    )
    processors = serializers.CharField(
        required=False, allow_blank=True, max_length=LEN_LONG, default=EMPTY_STRING
    )
    task_schema_id = serializers.IntegerField(required=True)
    state_id = serializers.IntegerField(required=True)
    order = serializers.IntegerField(required=False, default=1)
    component_type = serializers.CharField(
        required=False, max_length=LEN_LONG, default=EMPTY_STRING
    )
    fields = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = Task
        fields = (
            "id",
            "ticket_id",
            "state_id",
            "name",
            "start_at",
            "end_at",
            "executor",
            "confirmer",
            "processors_type",
            "processors",
            "processor_users",
            "order",
            "status",
            "task_schema_id",
            "component_type",
            "fields",
            "error_message",
        ) + model.DISPLAY_FIELDS
        read_only_fields = model.DISPLAY_FIELDS

    def validate(self, attrs):
        validated_data = super(TaskSerializer, self).validate(attrs)

        # 可选处理人
        if "processors" in validated_data:
            validated_data.update(processors=dotted_name(validated_data["processors"]))

        if self.partial:
            return validated_data

        try:
            schema_instance = TaskSchema.objects.get(
                id=validated_data["task_schema_id"]
            )
        except TaskSchema.DoesNotExist:
            raise ValidationError(detail=_("对应的任务模板配置不存在"))

        ticket = Ticket.objects.get(id=validated_data["ticket_id"])
        task_config = TaskConfig.objects.filter(
            workflow_id=ticket.flow_id,
            workflow_type=VERSION,
            create_task_state=validated_data["state_id"],
        ).first()
        if task_config:
            validated_data["execute_state_id"] = task_config.execute_task_state
        else:
            is_exist = TaskConfig.objects.filter(
                workflow_id=ticket.flow_id,
                workflow_type=VERSION,
                execute_task_state=validated_data["state_id"],
            ).exists()
            if is_exist:
                validated_data["execute_state_id"] = validated_data["state_id"]
            else:
                raise ValidationError(detail=_("对应的任务配置不存在"))
        # 更新component_type
        fields = validated_data.get("fields", {})
        validated_data["name"] = fields.get("task_name")
        validated_data["component_type"] = schema_instance.component_type

        return validated_data

    def to_representation(self, instance):
        data = super(TaskSerializer, self).to_representation(instance)
        # 首尾去掉逗号
        data.update(processors=normal_name(data["processors"]))
        if (
            isinstance(self.context.get("view"), ModelViewSet)
            and self.context["view"].detail
        ):
            create_fields = TaskFieldSerializer(instance.create_fields, many=True).data
            operate_fields = TaskFieldSerializer(
                instance.operate_fields, many=True
            ).data
            confirm_fields = TaskFieldSerializer(
                instance.confirm_fields, many=True
            ).data
            data["fields"] = {
                "create_fields": create_fields,
                "operate_fields": operate_fields,
                "confirm_fields": confirm_fields,
            }

        if isinstance(self.context.get("request"), Request):
            data["can_process"] = instance.can_process(
                self.context["request"].user.username
            )
        return data


class TaskListSerializer(serializers.ModelSerializer):
    """任务列表序列化"""

    class Meta:
        model = Task
        fields = (
            "id",
            "ticket_id",
            "state_id",
            "name",
            "processors_type",
            "processors",
            "processor_users",
            "order",
            "status",
            "create_at",
            "task_schema_id",
            "component_type",
            "error_message",
            "execute_state_id",
        )

    def __init__(self, instance=None, data=empty, **kwargs):
        super(TaskListSerializer, self).__init__(instance, data, **kwargs)

    def to_representation(self, instance):
        data = super(TaskListSerializer, self).to_representation(instance)
        # 首尾去掉逗号
        data.update(processors=normal_name(data["processors"]))
        if isinstance(self.context.get("request"), Request):
            data["can_process"] = instance.can_process(
                self.context["request"].user.username
            )
        return data


class TaskFilterSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class TaskOrderSerializer(serializers.Serializer):
    task_orders = serializers.ListField(
        required=True, allow_empty=True, validators=[TaskOrdersValidator()]
    )
    ticket_id = serializers.IntegerField(
        required=True, validators=[TicketValidValidator()]
    )

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class TaskFieldBatchUpdateSerializer(serializers.Serializer):
    fields = serializers.ListField(
        required=True, allow_empty=True, validators=[TaskFieldBatchUpdateValidator()]
    )

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class TaskCreateSerializer(TaskSerializer):
    def validate(self, attrs):
        validated_data = super(TaskCreateSerializer, self).validate(attrs)
        # 创建任务阶段的字段校验
        fields = validated_data.get("fields", {})
        validated_data["name"] = fields.get("task_name")
        task_fields_schema = TaskFieldSchema.objects.filter(
            task_schema_id=validated_data["task_schema_id"], stage=CREATE
        )

        for field in task_fields_schema:
            field_data = field.tag_data(exclude=["task_schema", "id"])
            field_data.update(value=fields.get(field_data["key"], ""))
            regex_validate(field_data, field)

        return validated_data


class TaskProceedSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=[(ACTION_OPERATE, _("处理")), (ACTION_CONFIRM, _("总结"))],
        required=True,
    )
    fields = serializers.ListField(required=True, allow_empty=True)

    def validate(self, attrs):
        validated_data = super(TaskProceedSerializer, self).validate(attrs)

        # 校验fields
        fields = validated_data.get("fields", {})
        action = attrs.get("action")
        task = self.context["task"]

        # 检验字段合法性：必填校验（未考虑隐藏字段）
        task_fields = (
            task.operate_fields if action == ACTION_OPERATE else task.confirm_fields
        )
        validate_task_fields(task_fields, fields)

        return validated_data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class TaskRetrySerializer(serializers.Serializer):
    """任务重试序列化"""

    fields = serializers.ListField(required=True, allow_empty=True)
    sops_templates = serializers.JSONField(required=True)

    def validate(self, attrs):
        validated_data = super(TaskRetrySerializer, self).validate(attrs)

        # 校验fields
        fields = validated_data.get("fields", {})

        # 检验字段合法性：必填校验（未考虑隐藏字段）
        task_fields = self.context["task"].operate_fields
        validate_task_fields(task_fields, fields)

        return validated_data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class TaskLibTasksSerializer(serializers.ModelSerializer):
    """任务库任务列表"""

    task_lib_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True, max_length=LEN_NORMAL)
    task_schema_id = serializers.CharField(required=True, max_length=LEN_NORMAL)
    component_type = serializers.CharField(required=True, max_length=LEN_NORMAL)
    processors_type = serializers.CharField(required=True, max_length=LEN_NORMAL)
    processors = serializers.CharField(required=True, max_length=LEN_LONG)
    fields = serializers.JSONField(required=True)
    sub_template_id = serializers.CharField(
        required=False, default="", max_length=LEN_NORMAL, allow_blank=True
    )
    project_id = serializers.CharField(
        required=False, default="", max_length=LEN_NORMAL, allow_blank=True
    )
    exclude_task_nodes = serializers.JSONField(required=True)

    class Meta:
        model = TaskLibTasks
        fields = (
            "name",
            "task_schema_id",
            "component_type",
            "processors_type",
            "processors",
            "fields",
            "sub_template_id",
            "project_id",
            "task_lib_id",
            "exclude_task_nodes",
        )


class TaskLibSerializer(serializers.ModelSerializer):
    """任务库序列化"""

    service_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True, max_length=LEN_NORMAL)
    creator = serializers.CharField(required=True, max_length=LEN_NORMAL)

    def validate(self, attrs):
        """参数校验："""
        # 创建不可重名
        if (
            self.instance is None
            and TaskLib.objects.filter(
                service_id=attrs["service_id"],
                name=attrs["name"],
                creator=attrs["creator"],
            ).exists()
        ):
            raise serializers.ValidationError(
                {str(_("参数校验失败")): _("您名下已经有同名任务库，请尝试换个名称")}
            )

        return attrs

    class Meta:
        model = TaskLib
        fields = ("id", "service_id", "name", "creator")


class TaskLibListSerializer(serializers.ModelSerializer):
    """任务库序列化"""

    class Meta:
        model = TaskLib
        fields = ("id", "service_id", "name", "creator")
        read_only_fields = ("id", "service_id", "name", "creator")
