# -*- coding: utf-8 -*-
import logging

from .base import BaseNotifier, NotifierRegistry

logger = logging.getLogger("app")


@NotifierRegistry.register
class SmsNotifier(BaseNotifier):
    """SMS notifier stub — override send() with your SMS gateway."""

    channel = "sms"

    def __init__(self, title, receivers, message, receiver_nums="", **kwargs):
        self.receiver_nums = receiver_nums
        super().__init__(title, receivers, message, **kwargs)

    def send(self, **kwargs):
        logger.warning(
            "SmsNotifier.send() is a stub — implement your SMS gateway integration. "
            "receivers=%s, title=%s",
            self.receivers,
            self.title,
        )
