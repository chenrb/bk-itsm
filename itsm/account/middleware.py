# -*- coding: utf-8 -*-
"""
登录校验中间件：页面请求未登录 → JS 重定向到登录页（保留 hash 路由）；
API/AJAX 请求 → 放行，由 DRF 返回 401。
"""

from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

REDIRECT_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
  var next = encodeURIComponent(location.pathname + location.search + location.hash);
  location.replace({login_url} + "?next=" + next);
</script>
</body>
</html>"""


class LoginRequiredMiddleware(MiddlewareMixin):
    """页面请求未登录 → JS 重定向到登录页；API 请求放行由 DRF 返回 401。"""

    API_PREFIXES = (
        "/api/",
        "/init/",
        "/openapi/",
        "/gateway/",
        "/monitor/",
        "/admin/",
        "/static/",
    )

    def process_view(self, request, view, args, kwargs):
        # 已登录 → 放行
        if request.user.is_authenticated:
            return None

        # 视图标记 login_exempt → 放行
        if getattr(view, "login_exempt", False):
            return None

        # API/AJAX 请求 → 放行（由 DRF IsAuthenticated 返回 401）
        if self._is_api_request(request):
            return None

        # 页面请求 + 未登录 → 返回 JS 重定向页面
        # 使用 JS 而非 302，因为 hash 路由 (#/...) 不会发送到服务器
        # 只有浏览器端的 JS 才能读取 location.hash
        login_url = settings.LOGIN_URL
        html = REDIRECT_HTML.replace("{login_url}", "'" + login_url + "'")
        return HttpResponse(html, status=401)

    @staticmethod
    def _is_api_request(request):
        """判断是否为 API/AJAX 请求。"""
        # ajax.js 设置的 X-Requested-With header
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return True
        # DRF 等工具发送的 Accept header
        if "application/json" in request.headers.get("Accept", ""):
            return True
        # 已知 API 路径前缀
        if request.path.startswith(LoginRequiredMiddleware.API_PREFIXES):
            return True
        return False
