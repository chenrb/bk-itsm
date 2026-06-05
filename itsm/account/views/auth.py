# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from itsm.component.decorators import login_exempt


@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
@login_exempt
def login_view(request):
    if request.method == "GET":
        return render_login_page(request, next_url=request.GET.get("next", "/"))

    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        next_url = request.POST.get("next", "/")
        return HttpResponseRedirect(next_url)

    return render_login_page(
        request,
        next_url=request.POST.get("next", "/"),
        error_message=_("用户名或密码错误"),
    )


@require_http_methods(["GET", "POST"])
@login_exempt
def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/account/login/")


def render_login_page(request, next_url="/", error_message=""):
    from django.shortcuts import render

    return render(
        request,
        "account/login.html",
        {
            "next": next_url,
            "error_message": error_message,
        },
    )
