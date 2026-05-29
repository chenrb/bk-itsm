# -*- coding: utf-8 -*-
"""
本地用户查询接口，替代原 adapter/config/sites/open/api.py。

提供与原 adapter API 兼容的接口签名，数据源从蓝鲸 ESB 切换为本地 User 模型。
"""
from functools import reduce

from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

USER_FIELDS = ("username", "nickname", "chname", "email", "phone")


def get_batch_users(users, properties="all", is_exact=True, page_params=None, name_type=None):
    """批量查询用户信息"""
    if not users:
        return []

    if is_exact:
        qs = User.objects.filter(username__in=users)
    else:
        queries = [Q(username__icontains=u) for u in users]
        qs = User.objects.filter(reduce(lambda a, b: a | b, queries))

    if page_params:
        page = page_params.get("page", 1)
        per_page = page_params.get("per_page", 20)
        start = (page - 1) * per_page
        qs = qs[start : start + per_page]

    return _format_users(qs)


def get_all_users(users=None):
    """查询所有用户或指定用户列表"""
    qs = User.objects.all()
    if users:
        qs = qs.filter(username__in=users)
    return _format_users(qs)


def _format_users(qs):
    """将 QuerySet 格式化为兼容原 adapter 的字典列表"""
    result = []
    for u in qs.values(*USER_FIELDS):
        item = {
            "username": u["username"],
            "display_name": u["nickname"] or u["chname"] or u["username"],
            "chname": u["chname"],
            "email": u["email"],
            "phone": u["phone"],
        }
        result.append(item)
    return result
