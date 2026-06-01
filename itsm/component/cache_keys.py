# -*- coding: utf-8 -*-
from functools import wraps

from django.core.cache import cache
from django.http import HttpResponse

from itsm.component.constants import PREFIX_KEY


def cache_response(timeout, key_func, cache_errors=False):
    """缓存 DRF view action 的响应。

    与 drf-extensions 的 cache_response 行为等价：
    - 缓存 miss 时：执行 view → finalize_response → render，存储 (content, status, headers)
    - 缓存 hit 时：直接构造 HttpResponse 返回，跳过序列化和渲染
    - 默认不缓存错误响应（status >= 400）
    """

    def decorator(func):
        @wraps(func)
        def inner(self, request, *args, **kwargs):
            key = key_func(
                view_instance=self,
                view_method=func,
                request=request,
                args=args,
                kwargs=kwargs,
            )
            cached = cache.get(key)
            if cached is not None:
                content, status_code, headers = cached
                response = HttpResponse(content=content, status=status_code)
                for k, v in headers.values():
                    response[k] = v
                if not hasattr(response, "_closable_objects"):
                    response._closable_objects = []
                return response

            response = func(self, request, *args, **kwargs)
            response = self.finalize_response(request, response, *args, **kwargs)
            response.render()

            if not response.status_code >= 400 or cache_errors:
                if hasattr(response, "_headers"):
                    hdrs = response._headers.copy()
                else:
                    hdrs = {k: (k, v) for k, v in response.items()}
                cache.set(
                    key,
                    (response.rendered_content, response.status_code, hdrs),
                    timeout,
                )
            return response

        return inner

    return decorator


def ticket_cache_key(view_instance, view_method, request, args, kwargs):
    """缓存关键字"""

    view_method_name = view_method.__name__

    cache_key = view_method_name

    if view_method_name == "get_my_deal_tickets":
        cache_key = "{}ticket:{}:{}:{}".format(
            PREFIX_KEY,
            view_method_name,
            request.user.username,
            request.query_params.get("days"),
        )

    if view_method_name == "get_my_ticket_status":
        cache_key = "{}ticket:{}:{}:{}".format(
            PREFIX_KEY,
            view_method_name,
            request.user.username,
            request.query_params.get("service_type"),
        )

    return cache_key
