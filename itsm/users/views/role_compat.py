# -*- coding: utf-8 -*-
"""
角色兼容 API：保持 /api/role/* 路径和响应格式不变。
前端流程设计器依赖这些端点。
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from itsm.users.models import Role, UserGroup

# 处理人类型列表（不含 CMDB / IAM）
PROCESSOR_TYPES = [
    {"key": "PERSON", "name": "个人"},
    {"key": "GENERAL", "name": "自定义角色"},
    {"key": "STARTER", "name": "提单人"},
    {"key": "STARTER_LEADER", "name": "提单人上级"},
    {"key": "ASSIGN_LEADER", "name": "派单人上级"},
    {"key": "ORGANIZATION", "name": "组织"},
    {"key": "BY_ASSIGNOR", "name": "派单人指定"},
    {"key": "EMPTY", "name": "无处理人"},
    {"key": "VARIABLE", "name": "变量"},
    {"key": "OPEN", "name": "不限"},
    {"key": "API", "name": "API 触发"},
]


@api_view(["GET"])
def role_types(request):
    """GET /api/role/types/ — 返回处理人类型列表。"""
    is_processor = request.query_params.get("is_processor", "").lower() == "true"
    if is_processor:
        return Response({"result": True, "data": PROCESSOR_TYPES})
    return Response({"result": True, "data": PROCESSOR_TYPES})


@api_view(["GET"])
def role_users(request):
    """
    GET /api/role/users/ — 兼容旧接口。
    role_type=GENERAL → 返回 UserGroup 列表
    role_type=ADMIN → 返回 Role 列表
    """
    role_type = request.query_params.get("role_type", "GENERAL")
    project_key = request.query_params.get("project_key", "0")

    if role_type == "GENERAL":
        groups = UserGroup.objects.filter(is_deleted=False, project_key=project_key)
        data = [
            {
                "id": g.id,
                "name": g.name,
                "count": g.members.count(),
                "is_builtin": g.is_builtin,
            }
            for g in groups
        ]
    elif role_type == "ADMIN":
        roles = Role.objects.filter(is_deleted=False)
        data = [
            {
                "id": r.id,
                "name": r.name,
                "count": r.members.count(),
                "role_key": r.role_key,
                "is_builtin": r.is_builtin,
            }
            for r in roles
        ]
    else:
        data = []

    return Response({"result": True, "data": data})


@api_view(["GET"])
def get_access_by_user(request):
    """GET /api/role/users/extra/get_access_by_user/"""
    username = request.query_params.get("username", "")
    if not username:
        return Response({"result": True, "data": []})
    access_list = Role.get_access_by_user(username)
    return Response({"result": True, "data": access_list})


@api_view(["GET"])
def get_global_choices(request):
    """GET /api/role/users/extra/get_global_choices/"""
    # 返回全局选项：处理人类型 + 角色组 + 角色
    groups = UserGroup.objects.filter(is_deleted=False, project_key="0")
    roles = Role.objects.filter(is_deleted=False)
    data = {
        "processor_types": PROCESSOR_TYPES,
        "general_roles": [
            {"id": g.id, "name": g.name, "count": g.members.count()}
            for g in groups
        ],
        "admin_roles": [
            {"id": r.id, "name": r.name, "role_key": r.role_key}
            for r in roles
        ],
    }
    return Response({"result": True, "data": data})
