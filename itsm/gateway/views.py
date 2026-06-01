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

import json

from django.core.cache import cache
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

from common.log import logger
from common.utils import filter_user_sensitive_info
from itsm.component.constants import CACHE_5MIN, PREFIX_KEY, CACHE_30MIN
from itsm.component.decorators import fbv_exception_handler
from itsm.component.platform_client.http import client_backend
from itsm.component.exceptions import ComponentCallError
from itsm.component.utils.basic import build_tree
from itsm.component.utils.client_backend_query import (
    get_list_departments,
    get_list_department_profiles,
)
from itsm.component.utils.response import Fail, Success

from django.conf import settings

adapter_api = settings.ADAPTER_API


@fbv_exception_handler
def get_batch_users(request):
    """批量获取用户信息"""
    users = (
        request.GET.get("users")
        or request.GET.get("exact_lookups")
        or request.GET.get("fuzzy_lookups")
    )
    properties = request.GET.get("properties", "")
    callback_func_name = request.GET.get("callback")

    page_params = {
        "page": int(request.GET.get("page", 1)),
        "page_size": int(request.GET.get("page_size", 20)),
    }

    # 是否启用精准匹配，默认为True
    is_exact = True
    if "fuzzy_lookups" in request.GET:
        is_exact = False

    if not users:
        return Fail(_("用户名列表不能为空"), "BK_LOGIN.GET_BATCH_USERS").json()
    if isinstance(users, str):
        users = users.split(",")

    try:
        res = filter_user_sensitive_info(adapter_api.get_batch_users(users, properties, is_exact, page_params))
        if callback_func_name:
            response = {
                "result": True,
                "message": "success",
                "data": {"results": res, "count": len(res)},
                "code": 0,
            }
            response = HttpResponse(
                "{}({})".format(callback_func_name, json.dumps(response))
            )
            response["Content-Type"] = "application/x-javascript; charset=utf-8"
            return response
        return Success(res).json()
    except Exception as error:
        logger.warning(_("批量获取用户信息出错，%s"), str(error))
        return Fail(
            _("批量获取用户信息出错，%s") % str(error), "BK_LOGIN.GET_BATCH_USERS"
        ).json()


@fbv_exception_handler
def get_all_users(request):
    """获取所有用户列表"""

    cache_key = "%sall_users" % PREFIX_KEY
    all_users = cache.get(cache_key)
    if all_users is not None:
        return Success(all_users).json()

    try:
        users = adapter_api.get_all_users()
    except ComponentCallError as e:
        return Fail(str(e), "BK_LOGIN.GET_ALL_USERS").json()

    cache.set(cache_key, users, CACHE_30MIN)

    return Success(users).json()


@cache_page(CACHE_5MIN, cache="default")
def get_departments(request):
    """获取部门列表信息"""
    try:
        res = get_list_departments({"fields": "id,name,parent,level,order"})
        res = build_tree(res, "parent", need_route=True)
    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_LIST").json()

    return Success(res).json()


@cache_page(CACHE_5MIN, cache="default")
def get_first_level_departments(request):
    try:
        params = {
            "lookup_field": "level",
            "exact_lookups": "0",
        }
        res = get_list_departments(params)
    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_LIST").json()

    return Success(res).json()


@cache_page(CACHE_5MIN, cache="default")
def get_department_users(request):
    """获取部门用户列表，支持递归查询"""
    try:
        department_id = request.GET.get("id")
        recursive = request.GET.get("recursive") == "true"

        res = filter_user_sensitive_info(get_list_department_profiles(
            {"id": department_id, "recursive": recursive, "detail": True}
        ))

    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_USERS").json()

    return Success(res).json()


@cache_page(CACHE_5MIN, cache="default")
def get_department_users_count(request):
    """获取某个部门下的人员数量"""
    try:
        department_id = request.GET.get("id")
        params = {
            "id": department_id,
            "recursive": "true",
            "detail": True,
            "page_size": 1,
        }
        res = client_backend.usermanage.list_department_profiles(params)
    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_USERS").json()
    return Success({"count": res["count"]}).json()


@cache_page(CACHE_5MIN, cache="default")
def get_department_info(request):
    """获取部门详情"""
    try:
        department_id = request.GET.get("id")
        res = client_backend.usermanage.retrieve_department(
            {
                "id": department_id,
            }
        )
    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_DEPARTMENT_INFO").json()

    return Success(res).json()


@cache_page(CACHE_5MIN, cache="default")
def get_user_info(request):
    """获取人员所属部门"""
    try:
        username = request.GET.get("username", request.user.username)
        res = client_backend.usermanage.list_profile_departments(
            {
                "id": username,
            }
        )
    except ComponentCallError as e:
        return Fail(str(e), "BK_USER_MANAGE.GET_USER_INFO").json()

    return Success(res).json()
