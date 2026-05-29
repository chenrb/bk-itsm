# -*- coding: utf-8 -*-
"""
ESB client stub — 原蓝鲸 ESB SDK 已移除。

提供 client_backend / client / backend_client 存根对象，
调用时返回空结果并记录 warning 日志。
后续由 Plan 07 (user_adapter) / Plan 11 (notifier) / Plan 13 (openapi) 逐步替换。
"""
import logging

logger = logging.getLogger(__name__)


class _ServiceStub:
    """模拟 ESB 服务模块（如 usermanage, cc, sops, cmsi）"""

    def __getattr__(self, name):
        def _stub_method(*args, **kwargs):
            logger.warning(
                "ESB stub called: %s.%s(%s, %s) — returning empty result. "
                "This should be replaced by a local implementation.",
                self.__class__.__name__,
                name,
                args,
                kwargs,
            )
            return {"data": {}, "result": False, "message": "ESB stub — not implemented"}

        return _stub_method


class _ClientStub:
    """模拟 client_backend / client / backend_client"""

    def __getattr__(self, service_name):
        logger.warning("ESB client stub accessed: .%s", service_name)
        return _ServiceStub()


client_backend = _ClientStub()
client = _ClientStub()
backend_client = _ClientStub()
