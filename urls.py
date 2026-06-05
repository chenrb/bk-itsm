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

from django.conf import settings
from django.urls import include, path, re_path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views import static

from itsm.users import urls as users_urls

# 公共URL配置
urlpatterns = [
    # Django后台数据库管理
    re_path(r"^admin/", admin.site.urls),
    # 用户登录鉴权
    path("account/", include("itsm.account.urls")),
    # 用户管理 API（users, departments, roles, permissions, etc.）
    re_path(r"^api/", include(users_urls.api_urlpatterns)),
    # 角色兼容 API（/api/role/*）
    re_path(r"^api/role/", include(users_urls.role_compat_urlpatterns)),
    # 网关兼容 API（/gateway/usermanage/*, /gateway/bk_login/*）
    re_path(r"^gateway/", include(users_urls.gateway_usermanage_urlpatterns)),
    re_path(r"^gateway/", include(users_urls.gateway_bk_login_urlpatterns)),
    # 人员选择器 JSONP（/api/c/compapi/v2/usermanage/*）
    re_path(
        r"^api/c/compapi/v2/usermanage/",
        include(users_urls.compapi_urlpatterns),
    ),
    # 接口版本管理
    re_path(r"^api/", include("itsm.api.v1")),
    # 对外开放的接口
    re_path(r"^openapi/", include("itsm.api.open_v1")),
    re_path(r"^openapi/v2/", include("itsm.api.open_v2")),
    # 监控，普罗米修斯相关的接口
    re_path(r"^monitor/", include("itsm.monitor.urls")),
    # 各种入口：微信/wiki/首页等
    re_path(r"^", include("itsm.sites.urls")),
    # eri admin
    re_path(r"^eri/admin/", include("pipeline.contrib.engine_admin.urls")),
]

# 本地生效：DEBUG=True
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 全局生效：不推荐生产环境使用
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$", static.serve, {"document_root": settings.MEDIA_ROOT}
    ),
]
