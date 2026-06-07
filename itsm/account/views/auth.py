# -*- coding: utf-8 -*-
import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from itsm.component.decorators import login_exempt


@require_http_methods(["POST"])
@login_exempt
@csrf_exempt
def api_login(request):
    """SPA 登录接口 — 接收 JSON，返回 JSON + Set-Cookie session。"""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"result": False, "message": "无效请求"}, status=400)

    username = body.get("username", "")
    password = body.get("password", "")
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse(
            {
                "result": True,
                "data": {
                    "username": user.username,
                    "chname": user.chname,
                },
            }
        )

    return JsonResponse({"result": False, "message": str(_("用户名或密码错误"))}, status=401)


@require_http_methods(["POST"])
@login_exempt
@csrf_exempt
def api_logout(request):
    """SPA 登出接口。"""
    logout(request)
    return JsonResponse({"result": True})
