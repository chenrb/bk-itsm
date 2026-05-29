# -*- coding: utf-8 -*-
"""Generic HTTP client for platform API calls.

Replaces the old `bk.http(config=...)` ESB proxy with direct `requests` calls.
The config dict format is preserved for backward compatibility:
  {
      "path": "/api/...",
      "method": "get" | "post" | "put" | "delete" | "patch",
      "query_params": {...},
      "body": {...},           # optional
      "headers": {...},        # optional
      "timeout": 30,           # optional
      "base_url": "...",       # optional, defaults to settings.PLATFORM_API_BASE_URL
  }
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


def http_call(config):
    """Execute an HTTP call based on a config dict.

    This replaces `bk.http(config=...)`.
    """
    base_url = config.get("base_url", getattr(settings, "PLATFORM_API_BASE_URL", ""))
    path = config.get("path", "")
    method = config.get("method", "get").lower()
    query_params = config.get("query_params", {})
    body = config.get("body") or config.get("data")
    headers = config.get("headers", {})
    timeout = config.get("timeout", DEFAULT_TIMEOUT)

    url = f"{base_url}{path}" if base_url else path

    try:
        resp = requests.request(
            method=method,
            url=url,
            params=query_params,
            json=body if body else None,
            headers=headers,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.warning("platform_client.http_call failed: %s %s — %s", method.upper(), url, e)
        return {
            "result": False,
            "data": {},
            "message": str(e),
        }


class PlatformClient:
    """HTTP client for platform service APIs (user management, CMDB, etc.).

    Replaces `client_backend` from the old ESB SDK.
    Each service (e.g. `usermanage`, `cc`) is accessed as an attribute
    that returns a ServiceProxy for method calls.
    """

    def __init__(self, base_url=None):
        self._base_url = base_url or getattr(settings, "PLATFORM_API_BASE_URL", "")

    def __getattr__(self, service_name):
        return ServiceProxy(self._base_url, service_name)


class ServiceProxy:
    """Proxies method calls to HTTP requests against a platform service."""

    def __init__(self, base_url, service_name):
        self._base_url = base_url
        self._service = service_name

    def __getattr__(self, method_name):
        def _call(*args, **kwargs):
            # Build URL from service + method convention
            path = f"/api/c/compapi/v2/{self._service}/{method_name}/"
            return http_call({
                "base_url": self._base_url,
                "path": path,
                "method": kwargs.pop("_method", "get"),
                "query_params": kwargs,
            })
        return _call


# Module-level instances (backward compatible with old imports)
client_backend = PlatformClient()
client = PlatformClient()
backend_client = PlatformClient()
bk = type("BKClient", (), {"http": staticmethod(http_call)})()
