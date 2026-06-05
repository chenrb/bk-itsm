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

import base64

from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

from common.mymako import render_mako_context
from itsm.iadmin.contants import SERVICE_SWITCH
from itsm.iadmin.models import SystemSettings

User = get_user_model()


class ServiceSwitchCheck(MiddlewareMixin):
    """
    手动关闭服务中间件，需要到admin里设置key='SERVICE_SWITCH'这条数据的value
    'on' 为开启服务
    'off' 为关闭服务
    """

    def process_view(self, request, view, args, kwargs):
        """process_view."""

        try:
            if SystemSettings.objects.get(key=SERVICE_SWITCH).value != "on":
                return render_mako_context(request, "close_service.html", {})
        except SystemSettings.DoesNotExist:
            return None

        return None


class NginxAuthProxy(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """process_view."""

        forwarded_user = request.META.get("HTTP_X_FORWARDED_USER")
        forwarded_auth = request.META.get("HTTP_AUTHORIZATION")

        if forwarded_user and forwarded_auth:
            try:
                auth_infos = forwarded_auth.split()
                if auth_infos[0] != "Basic":
                    return None

                username, password = base64.b64decode(auth_infos[1]).decode().split(":")

                # simple validate
                user = User.objects.get(username=forwarded_user)
                if user.username == username:
                    setattr(request, "user", user)
                    setattr(view, "login_exempt", True)
            except BaseException:
                return None

        return None
