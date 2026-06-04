# -*- coding: utf-8 -*-
import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
def login_view(request):
    if request.method == "GET":
        return JsonResponse({"result": True})

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"result": False, "message": "无效请求"}, status=400)

    username = body.get("username", "")
    password = body.get("password", "")
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({"result": True, "data": {"username": user.username}})
    return JsonResponse({"result": False, "message": "用户名或密码错误"}, status=401)


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({"result": True})
