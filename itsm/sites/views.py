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

import os
import datetime

from itsm.component.decorators import login_exempt
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _, get_language
from django.views.decorators.http import require_GET

from common.template.template import Template
from itsm.iadmin.contants import NOTICE_CENTER_SWITCH
from itsm.iadmin.models import SystemSettings
from itsm.project.models import UserProjectAccessRecord
from itsm.users.models.role import Role


def _get_title():
    return "{} | {}".format(_("流程服务"), _("ITSM"))


def _get_footer():
    default_footer = """
            <div class="copyright">
                <ul class="link-list">
                    <a href="https://wpa1.qq.com/KziXGWJs?_type=wpa&qidian=true" class="link-item">{}</a>
                    <a href="http://bk.tencent.com/s-mart/community/" class="link-item" target="_blank">{}</a>
                    <a href="http://bk.tencent.com/" class="link-item" target="_blank">{}</a>
                </ul>
                <div class="desc">Copyright &copy; 2012-${{year}} Tencent BlueKing. All Rights Reserved.V2.6.8</div>
            </div>
            """.format(
        _("技术支持"), _("社区论坛"), _("产品官网")
    )
    return getattr(settings, "FOOTER", None) or default_footer


def init(request):
    try:
        DEFAULT_PROJECT = UserProjectAccessRecord.objects.get(
            username=request.user.username
        ).project_key
    except Exception:
        DEFAULT_PROJECT = ""

    # Get user permissions from local Role model
    if request.user.is_superuser:
        from itsm.users.data.permissions import BUILTIN_PERMISSIONS

        permissions = [code for code, _, _, _ in BUILTIN_PERMISSIONS]
    else:
        permissions = list(
            Role.objects.filter(members=request.user, is_deleted=False)
            .values_list("permissions__code", flat=True)
            .distinct()
        )

    return JsonResponse(
        {
            "code": 0,
            "result": True,
            "data": {
                "DEFAULT_PROJECT": DEFAULT_PROJECT,
                "chname": request.user.chname,
                "username": request.user.username,
                "all_access": Role.get_access_by_user(request.user.username),
                "IS_ITSM_ADMIN": (
                    1 if Role.is_itsm_superuser(request.user.username) else 0
                ),
                "need_target": False,
                "location": "",
                "permissions": permissions,
            },
            "message": "",
        }
    )


@login_exempt
def index(request):
    """首页"""
    TITLE = _get_title()
    LOGIN_URL = settings.LOGIN_URL

    BK_USER_MANAGE_HOST = settings.USER_MANAGE_HOST

    try:
        notice_center_switch_value = SystemSettings.objects.get(
            key=NOTICE_CENTER_SWITCH
        ).value
    except SystemSettings.DoesNotExist:
        notice_center_switch_value = "off"

    # 文档地址转换
    doc_lang = "EN"
    lang = get_language()
    if lang in ["zh-cn", "zh-hans"]:
        doc_lang = "ZH"

    version = get_version()
    doc_url = settings.DOC_URL.format(
        lang=doc_lang, version=get_major_minor_version(version)
    )

    return render(
        request,
        "index.html",
        {
            "is_vip": "true",
            "CUSTOM_TITLE": TITLE,
            "USE_LOG": "true",
            "LOGIN_URL": LOGIN_URL,
            "LOG_NAME": _("流程服务"),
            "USER_MANAGE_HOST": BK_USER_MANAGE_HOST,
            "PLATFORM_API_URL": settings.PLATFORM_API_URL,
            "TAM_PROJECT_ID": settings.TAM_PROJECT_ID,
            "DOC_URL": doc_url,
            "DOC_CENTER_HOST": settings.DOC_CENTER_HOST,
            "NOTICE_CENTER_SWITCH": notice_center_switch_value,
            "SHARED_RES_URL": settings.SHARED_RES_URL,
            "PLATFORM_NAME": settings.PLATFORM_NAME,
            "VERSION": version,
            "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
        },
    )


@require_GET
def get_footer(request):
    """
    @summary: 获取当前环境的页面 footer
    @param request:
    @return:
    """
    FOOTER = _get_footer()

    return JsonResponse(
        {
            "result": True,
            "data": Template(FOOTER()).render(year=datetime.datetime.now().year),
            "code": "OK",
            "message": "success",
        }
    )


def get_version():
    """
    @summary: 获取版本信息
    """
    # 读取文件内容
    app_desc = os.path.join(settings.PROJECT_ROOT, "VERSION")
    with open(app_desc, "r") as file:
        content = file.read()
    return content.strip()


def get_major_minor_version(version_string):
    # 使用 split() 方法分割字符串
    parts = version_string.split(".")
    # 取前两个部分并用 '.' 连接
    major_minor = ".".join(parts[:2])
    return major_minor
