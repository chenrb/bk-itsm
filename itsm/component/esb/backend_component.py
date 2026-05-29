# -*- coding: utf-8 -*-
"""
Backend component stub — 原蓝鲸 backend_component 已移除。

提供 bk 存根对象。后续由 Plan 07/11/13 逐步替换。
"""
import logging

from itsm.component.esb.esbclient import _ServiceStub

logger = logging.getLogger(__name__)


class _BKStub:
    """模拟 bk 对象，支持 bk.http(config=...) 调用"""

    def __getattr__(self, name):
        logger.warning("backend_component stub accessed: .%s", name)
        return _ServiceStub()

    def http(self, *args, **kwargs):
        logger.warning("bk.http() stub called — returning empty response")
        return {"data": {}, "result": False, "message": "bk.http stub — not implemented"}


bk = _BKStub()
