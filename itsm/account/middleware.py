# -*- coding: utf-8 -*-
"""
登录校验中间件：页面请求未登录 → 返回 SPA 登录页 HTML；
API/AJAX 请求 → 放行，由 DRF 返回 401。
"""

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

LOGIN_REDIRECT_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
  location.hash = '#/login';
</script>
</body>
</html>"""


class LoginRequiredMiddleware(MiddlewareMixin):
    """页面请求未登录 → 返回 JS 重定向到 SPA 登录页；API 请求放行由 DRF 返回 401。"""

    API_PREFIXES = (
        "/api/",
        "/openapi/",
        "/gateway/",
        "/monitor/",
        "/admin/",
        "/static/",
    )

    def process_view(self, request, view, args, kwargs):
        if request.user.is_authenticated:
            return None

        if getattr(view, "login_exempt", False):
            return None

        if self._is_api_request(request):
            return None

        return HttpResponse(LOGIN_REDIRECT_HTML, status=401)

    @staticmethod
    def _is_api_request(request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return True
        if "application/json" in request.headers.get("Accept", ""):
            return True
        if request.path.startswith(LoginRequiredMiddleware.API_PREFIXES):
            return True
        return False
