# -*- coding: utf-8 -*-
"""
Gateway 兼容视图：替代原 itsm/gateway/ 中的用户管理和登录 API。
保持原有 URL 路径和响应格式不变，数据源改为本地数据库。
"""
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response

from itsm.users.models import Department, DeptMembership, LoginAttempt, SecurityPolicy

User = get_user_model()

# ── /gateway/usermanage/* 兼容视图 ────────────────────────


@api_view(["GET"])
def get_first_level_departments(request):
    """根部门列表。"""
    departments = Department.objects.filter(parent__isnull=True, is_active=True)
    data = [
        {"id": d.id, "name": d.name, "order": d.order, "has_children": d.has_children}
        for d in departments
    ]
    return Response({"result": True, "data": data})


@api_view(["GET"])
def get_department_info(request):
    """部门详情 + 子部门懒加载。"""
    dept_id = request.query_params.get("id")
    if not dept_id:
        return Response({"result": False, "message": _("缺少部门 ID")}, status=400)
    try:
        dept = Department.objects.get(pk=dept_id)
    except Department.DoesNotExist:
        return Response({"result": False, "message": _("部门不存在")}, status=404)
    children = Department.objects.filter(parent=dept, is_active=True)
    data = {
        "id": dept.id,
        "name": dept.name,
        "full_name": dept.full_name,
        "order": dept.order,
        "parent_id": dept.parent_id,
        "has_children": dept.has_children,
        "children": [
            {
                "id": c.id,
                "name": c.name,
                "order": c.order,
                "has_children": c.has_children,
            }
            for c in children
        ],
    }
    return Response({"result": True, "data": data})


@api_view(["GET"])
def get_departments(request):
    """全量部门树。"""
    departments = Department.objects.filter(is_active=True)
    data = [
        {
            "id": d.id,
            "name": d.name,
            "full_name": d.full_name,
            "parent_id": d.parent_id,
            "order": d.order,
            "has_children": d.has_children,
        }
        for d in departments
    ]
    return Response({"result": True, "data": data})


@api_view(["GET"])
def get_department_users(request):
    """部门用户列表，支持 recursive。"""
    dept_id = request.query_params.get("id")
    recursive = request.query_params.get("recursive", "false").lower() == "true"
    if not dept_id:
        return Response({"result": False, "message": _("缺少部门 ID")}, status=400)
    try:
        dept = Department.objects.get(pk=dept_id)
    except Department.DoesNotExist:
        return Response({"result": False, "message": _("部门不存在")}, status=404)

    if recursive:
        dept_ids = dept.get_descendants(include_self=True).values_list("id", flat=True)
    else:
        dept_ids = [dept.id]

    memberships = DeptMembership.objects.filter(
        department_id__in=dept_ids
    ).select_related("user")
    data = [
        {
            "username": m.user.username,
            "chname": m.user.chname,
            "display_name": m.user.display_name,
            "email": m.user.email,
            "phone": m.user.phone,
            "department_id": m.department_id,
            "is_primary": m.is_primary,
        }
        for m in memberships
    ]
    return Response({"result": True, "data": data})


@api_view(["GET"])
def get_department_users_count(request):
    """部门用户计数。"""
    dept_id = request.query_params.get("id")
    if not dept_id:
        return Response({"result": False, "message": _("缺少部门 ID")}, status=400)
    try:
        dept = Department.objects.get(pk=dept_id)
    except Department.DoesNotExist:
        return Response({"result": False, "message": _("部门不存在")}, status=404)
    count = DeptMembership.objects.filter(department=dept).count()
    return Response({"result": True, "data": count})


@api_view(["GET"])
def get_user_info(request):
    """用户所属部门信息。"""
    username = request.query_params.get("username") or request.query_params.get("id")
    if not username:
        return Response({"result": False, "message": _("缺少用户名")}, status=400)
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"result": False, "message": _("用户不存在")}, status=404)

    memberships = DeptMembership.objects.filter(user=user).select_related("department")
    departments = [
        {
            "id": m.department_id,
            "name": m.department.name,
            "full_name": m.department.full_name,
            "is_primary": m.is_primary,
        }
        for m in memberships
    ]
    data = {
        "username": user.username,
        "chname": user.chname,
        "display_name": user.display_name,
        "email": user.email,
        "phone": user.phone,
        "departments": departments,
    }
    return Response({"result": True, "data": data})


# ── /gateway/bk_login/* 兼容视图 ──────────────────────────


@api_view(["GET"])
def bk_get_batch_users(request):
    """批量查询用户信息，兼容 JSONP。"""
    users_param = request.query_params.get("users", "")
    exact_lookup = request.query_params.get("exact_lookup", "1") == "1"
    user_list = [u.strip() for u in users_param.split(",") if u.strip()] if users_param else []

    if not user_list:
        return Response({"result": True, "data": []})

    if exact_lookup:
        qs = User.objects.filter(username__in=user_list)
    else:
        from django.db.models import Q
        import functools

        queries = [Q(username__icontains=u) for u in user_list]
        qs = User.objects.filter(functools.reduce(lambda a, b: a | b, queries))

    data = [
        {
            "username": u.username,
            "chname": u.chname,
            "display_name": u.display_name,
            "email": u.email,
            "phone": u.phone,
        }
        for u in qs
    ]
    return Response({"result": True, "data": data})


@api_view(["GET"])
def bk_get_all_users(request):
    """全量用户列表，30 分钟缓存。"""
    cache_key = "gateway_bk_login_all_users"
    data = cache.get(cache_key)
    if data is None:
        users = User.objects.all()
        data = [
            {
                "username": u.username,
                "chname": u.chname,
                "display_name": u.display_name,
                "email": u.email,
                "phone": u.phone,
            }
            for u in users
        ]
        cache.set(cache_key, data, 1800)  # 30 minutes
    return Response({"result": True, "data": data})


# ── /api/c/compapi/v2/usermanage/fs_list_users/ 兼容视图 ──


@api_view(["GET"])
def fs_list_users(request):
    """人员选择器 JSONP 兼容接口。"""
    callback = request.query_params.get("callback", "")
    search = request.query_params.get("search", "")
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("pageSize", 20))

    qs = User.objects.filter(is_active=True)
    if search:
        from django.db.models import Q

        qs = qs.filter(Q(username__icontains=search) | Q(chname__icontains=search))

    total = qs.count()
    start = (page - 1) * page_size
    users = qs[start : start + page_size]

    data = [
        {
            "id": u.username,
            "username": u.username,
            "display_name": u.display_name,
            "chname": u.chname,
            "email": u.email,
            "phone": u.phone,
            "department": u.department.name if u.department else "",
        }
        for u in users
    ]
    result = {"count": total, "results": data}

    # JSONP callback support
    if callback:
        from django.http import HttpResponse

        import json

        response = HttpResponse(
            f"{callback}({json.dumps(result)})",
            content_type="application/javascript",
        )
        return response

    return Response(result)
