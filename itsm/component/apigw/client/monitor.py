# -*- coding: utf-8 -*-
"""Monitor push data stub."""
import logging

logger = logging.getLogger("app")


class PushData:
    def __call__(self, data):
        logger.warning("PushData stub called — monitor push decoupled from BlueKing")
        return {}
