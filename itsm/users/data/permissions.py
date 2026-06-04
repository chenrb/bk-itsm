# -*- coding: utf-8 -*-
"""
内置权限声明式定义。
格式: (code, name, category, permission_type)
name 使用 gettext 支持多语言。
"""
from django.utils.translation import gettext_lazy as _

BUILTIN_PERMISSIONS = [
    # ── page 级（页面可见性） ─────────────────────────────
    ("page:workflow", _("流程管理"), "workflow", "page"),
    ("page:ticket", _("工单管理"), "ticket", "page"),
    ("page:service", _("服务配置"), "service", "page"),
    ("page:sla", _("SLA 管理"), "sla", "page"),
    ("page:system", _("系统管理"), "system", "page"),
    ("page:project", _("项目管理"), "project", "page"),
    ("page:statistics", _("运营数据"), "ticket", "page"),
    ("page:task", _("任务管理"), "task", "page"),
    # ── button 级（按钮/操作可见性） ──────────────────────
    ("btn:workflow:create", _("创建流程"), "workflow", "button"),
    ("btn:workflow:edit", _("编辑流程"), "workflow", "button"),
    ("btn:workflow:delete", _("删除流程"), "workflow", "button"),
    ("btn:workflow:publish", _("发布流程"), "workflow", "button"),
    ("btn:ticket:create", _("创建工单"), "ticket", "button"),
    ("btn:ticket:withdraw", _("撤单"), "ticket", "button"),
    ("btn:ticket:transfer", _("转单"), "ticket", "button"),
    ("btn:ticket:close", _("关单"), "ticket", "button"),
    ("btn:ticket:export", _("导出工单"), "ticket", "button"),
    ("btn:ticket:comment", _("评论"), "ticket", "button"),
    ("btn:service:create", _("创建服务"), "service", "button"),
    ("btn:service:edit", _("编辑服务"), "service", "button"),
    ("btn:service:delete", _("删除服务"), "service", "button"),
    ("btn:sla:create", _("创建SLA"), "sla", "button"),
    ("btn:sla:edit", _("编辑SLA"), "sla", "button"),
    ("btn:sla:delete", _("删除SLA"), "sla", "button"),
    # ── feature 级（后端 API 鉴权） ──────────────────────
    ("feature:workflow:manage", _("流程管理权限"), "workflow", "feature"),
    ("feature:ticket:operate", _("工单操作权限"), "ticket", "feature"),
    ("feature:ticket:view-all", _("查看全部工单"), "ticket", "feature"),
    ("feature:ticket:export", _("导出工单数据"), "ticket", "feature"),
    ("feature:service:manage", _("服务管理权限"), "service", "feature"),
    ("feature:sla:manage", _("SLA 管理权限"), "sla", "feature"),
    ("feature:system:role-manage", _("角色管理"), "system", "feature"),
    ("feature:system:user-manage", _("用户管理"), "system", "feature"),
    ("feature:system:group-manage", _("角色组管理"), "system", "feature"),
    ("feature:system:department-manage", _("部门管理"), "system", "feature"),
    ("feature:system:security-manage", _("安全策略管理"), "system", "feature"),
    ("feature:system:global-settings", _("全局设置"), "system", "feature"),
    ("feature:project:manage", _("项目管理权限"), "project", "feature"),
    ("feature:task:manage", _("任务管理权限"), "task", "feature"),
]

# ── Built-in Role → Permission Matrix ─────────────────────────

# SUPERUSER: 全部权限
SUPERUSER_PERMISSIONS = [code for code, _, _, _ in BUILTIN_PERMISSIONS]

# WORKFLOW_MANAGER: 流程相关权限
WORKFLOW_MANAGER_PERMISSIONS = [
    # 全部 page
    "page:workflow",
    "page:ticket",
    "page:service",
    "page:sla",
    "page:project",
    "page:task",
    # 流程 button
    "btn:workflow:create",
    "btn:workflow:edit",
    "btn:workflow:delete",
    "btn:workflow:publish",
    # 流程 feature
    "feature:workflow:manage",
    "feature:ticket:operate",
    "feature:service:manage",
    "feature:sla:manage",
    "feature:project:manage",
    "feature:task:manage",
]

# STATICS_MANAGER: 运营数据 + 导出
STATICS_MANAGER_PERMISSIONS = [
    "page:statistics",
    "page:ticket",
    "feature:ticket:view-all",
    "feature:ticket:export",
]
