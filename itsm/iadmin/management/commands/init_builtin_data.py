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

import traceback

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "初始化内置数据（角色、工作流、服务目录、SLA 等）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            type=str,
            default="",
            help="仅初始化指定模块（逗号分隔），如 --app role,service",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="列出可用的初始化模块",
        )
        parser.add_argument(
            "--skip",
            type=str,
            default="",
            help="跳过指定模块（逗号分隔），如 --skip version_log",
        )

    def handle(self, *args, **kwargs):
        modules = self._get_modules()

        if kwargs["list"]:
            self.stdout.write("可用的初始化模块（按依赖顺序）：")
            for name, desc, _ in modules:
                self.stdout.write(f"  {name:16s} {desc}")
            return

        # 确定要执行的模块
        app_filter = [s.strip() for s in kwargs["app"].split(",") if s.strip()]
        skip_filter = set(s.strip() for s in kwargs["skip"].split(",") if s.strip())

        targets = []
        for name, desc, func in modules:
            if name in skip_filter:
                continue
            if app_filter and name not in app_filter:
                continue
            targets.append((name, desc, func))

        if not targets:
            self.stdout.write(self.style.WARNING("没有匹配的模块"))
            return

        self.stdout.write(self.style.SUCCESS("开始初始化内置数据..."))

        for name, desc, func in targets:
            self.stdout.write(f"  [{name}] {desc}...", ending="")
            try:
                func()
                self.stdout.write(self.style.SUCCESS(" OK"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f" FAILED"))
                self.stderr.write(traceback.format_exc())

        self.stdout.write(self.style.SUCCESS("初始化完成"))

    def _get_modules(self):
        return [
            ("permission", "内置权限", self._init_permission),
            ("role", "角色类型与用户角色", self._init_role),
            ("user_group", "内置角色组", self._init_user_group),
            ("security_policy", "安全策略默认值", self._init_security_policy),
            ("project", "默认项目", self._init_project),
            ("iadmin", "通知/系统设置/模板字段/表格", self._init_iadmin),
            ("workflow", "内置工作流与任务模板", self._init_workflow),
            ("service", "服务分类/目录/内置服务", self._init_service),
            ("ticket_status", "工单状态与流转", self._init_ticket_status),
            ("sla", "SLA 策略与计时规则", self._init_sla),
            ("superuser", "超级用户", self._init_superuser),
            ("version_log", "版本日志", self._init_version_log),
        ]

    def _init_permission(self):
        """初始化内置权限 + 角色 + 角色权限分配。"""
        from itsm.users.data.permissions import (
            BUILTIN_PERMISSIONS,
            STATICS_MANAGER_PERMISSIONS,
            SUPERUSER_PERMISSIONS,
            WORKFLOW_MANAGER_PERMISSIONS,
        )
        from itsm.users.models import Permission, Role

        # 创建内置权限
        for code, name, category, perm_type in BUILTIN_PERMISSIONS:
            Permission.objects.update_or_create(
                code=code,
                defaults={
                    "name": str(name),
                    "category": category,
                    "permission_type": perm_type,
                    "is_builtin": True,
                },
            )

        # 创建内置角色
        builtin_roles = [
            ("SUPERUSER", "超级管理员", SUPERUSER_PERMISSIONS),
            ("WORKFLOW_MANAGER", "流程管理员", WORKFLOW_MANAGER_PERMISSIONS),
            ("STATICS_MANAGER", "统计查看员", STATICS_MANAGER_PERMISSIONS),
        ]
        for role_key, role_name, perm_codes in builtin_roles:
            role, _ = Role.objects.update_or_create(
                role_key=role_key,
                defaults={
                    "name": role_name,
                    "is_builtin": True,
                },
            )
            perm_ids = list(
                Permission.objects.filter(code__in=perm_codes).values_list(
                    "id", flat=True
                )
            )
            role.permissions.set(perm_ids)

    def _init_role(self):
        from itsm.role.models import RoleType, UserRole

        RoleType.migrate_general_role_type()
        RoleType.init_builtin_roles()
        UserRole.init_builtin_user_roles()

    def _init_user_group(self):
        """初始化内置角色组。"""
        from itsm.users.data.user_groups import BUILTIN_USER_GROUPS
        from itsm.users.models import UserGroup

        for group_key, name in BUILTIN_USER_GROUPS:
            UserGroup.objects.update_or_create(
                group_key=group_key,
                defaults={
                    "name": str(name),
                    "is_builtin": True,
                    "project_key": "0",
                },
            )

    def _init_security_policy(self):
        """初始化安全策略默认值。"""
        from itsm.users.models import SecurityPolicy

        defaults = [
            # Password policies
            ("password_min_length", 8, "password", "密码最小长度"),
            ("password_require_uppercase", True, "password", "是否要求包含大写字母"),
            ("password_require_lowercase", True, "password", "是否要求包含小写字母"),
            ("password_require_digit", True, "password", "是否要求包含数字"),
            ("password_require_special", False, "password", "是否要求包含特殊字符"),
            ("password_history_count", 0, "password", "禁止重复使用最近 N 次密码"),
            ("password_max_age_days", 0, "password", "密码过期天数（0=永不过期）"),
            # Login policies
            ("login_max_attempts", 5, "login", "连续失败锁定阈值"),
            ("login_lockout_minutes", 30, "login", "锁定持续时间（分钟）"),
            # Session policies
            ("session_timeout_minutes", 480, "session", "Session 空闲超时时间（分钟）"),
        ]
        for key, value, category, description in defaults:
            SecurityPolicy.objects.update_or_create(
                key=key,
                defaults={
                    "value": value,
                    "category": category,
                    "description": description,
                    "is_builtin": True,
                },
            )

    def _init_project(self):
        from itsm.project.models import Project

        Project.init_default_project()

    def _init_iadmin(self):
        from itsm.iadmin.models import CustomNotice, SystemSettings
        from itsm.workflow.models import Notify, TemplateField, Table
        from itsm.component.constants import DEFAULT_TEMPLATE_FIELDS, DEFAULT_TABLE

        Notify.init_builtin_notify()
        CustomNotice.init_default_template()
        SystemSettings.init_default_settings()
        TemplateField.objects.create_default_template_field(DEFAULT_TEMPLATE_FIELDS)
        Table.objects.init_table(DEFAULT_TABLE)

    def _init_workflow(self):
        from itsm.workflow.models import Workflow, TaskSchema

        Workflow.objects.init_builtin_workflow()
        if not TaskSchema.objects.filter(
            component_type="SOPS", is_deleted=False
        ).exists():
            TaskSchema.objects.create(
                component_type="SOPS",
                name="标准运维任务模板",
                is_builtin=True,
                is_draft=False,
                is_enabled=True,
            )

    def _init_service(self):
        from itsm.service.models import Service, ServiceCatalog, ServiceCategory, SysDict
        from itsm.component.constants import CATALOG
        from itsm.service.signals.handlers import (
            init_builtin_approve_service,
            init_builtin_services_from_files,
        )

        ServiceCategory.init_service_data()
        SysDict.objects.init_builtin_dicts()
        ServiceCatalog.objects.init_default_catalog(CATALOG)
        Service.objects.init_builtin_services()
        init_builtin_approve_service()
        init_builtin_services_from_files()

    def _init_ticket_status(self):
        from itsm.ticket_status.models import (
            TicketStatus,
            StatusTransit,
            TicketStatusConfig,
        )

        TicketStatus.init_ticket_status()
        StatusTransit.init_status_transit()
        TicketStatusConfig.init_ticket_status_config()

    def _init_sla(self):
        from itsm.sla.models import (
            PriorityMatrix,
            Sla,
            Schedule,
            SlaTimerRule,
            SlaTicketHighlight,
        )

        PriorityMatrix.objects.init_matrix()
        Sla.init_sla(Schedule.init_schedule())
        SlaTimerRule.init_sla_timer_rule()
        SlaTicketHighlight.init_sla_ticket_hightlight()

    def _init_superuser(self):
        from django.conf import settings
        from django.contrib.auth import get_user_model

        User = get_user_model()
        for name in settings.INIT_SUPERUSER:
            try:
                User.objects.update_or_create(
                    username=name,
                    defaults={
                        "is_staff": True,
                        "is_active": True,
                        "is_superuser": True,
                    },
                )
            except BaseException as e:
                self.stderr.write(f"init superuser {name} error: {e}")

    def _init_version_log(self):
        from itsm.iadmin.models import ReleaseVersionLog

        ReleaseVersionLog.objects.init_version_log_info("zh-cn")
        ReleaseVersionLog.objects.init_version_log_info("en")
