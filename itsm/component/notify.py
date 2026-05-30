# -*- coding: utf-8 -*-
from datetime import datetime

from django.conf import settings
from django.utils.translation import gettext as _

from common.log import logger
from itsm.component.constants import GENERAL_NOTICE
from itsm.component.notifiers import NotifierRegistry
from itsm.component.utils.basic import merge_dict_list
from itsm.meta.services.notice_filter import notice_filter_service


class BaseNotifier:
    def __init__(self, title, receivers, message, notify_type=GENERAL_NOTICE):
        self.title = title
        self.receivers = notice_filter_service.notice_receiver_filter(receivers)
        self.message = message
        self.notify_type = notify_type

    def get_notify_class(self, notify_type, **kwargs):
        if notify_type == "email":
            return EmailNotifier(self.title, self.receivers, self.message)
        if notify_type == "sms":
            return SmsNotifier(
                self.title,
                self.receivers,
                self.message,
                receiver_nums=kwargs.get("receiver_nums"),
            )
        return BaseNotifier(self.title, self.receivers, self.message, notify_type)

    def send(self, **kwargs):
        """Send notification via the registered channel."""
        channel = self.notify_type.lower()
        try:
            notifier_cls = NotifierRegistry.get(channel)
        except KeyError:
            logger.info("Unsupported notification channel: %s", channel)
            return

        notifier = notifier_cls(self.title, self.receivers, self.message)
        try:
            return notifier.send(**kwargs)
        except Exception as e:
            logger.error("Notification send failed, channel=%s, error=%s", channel, e)
            raise

    @property
    def params(self):
        return {
            "receiver__username": self.receivers,
            "title": self.title,
            "content": self.message,
        }


class EmailNotifier(BaseNotifier):
    def send(self, **kwargs):
        params = merge_dict_list([self.params, kwargs])
        notifier = NotifierRegistry.get("email")(
            self.title, self.receivers, self.message
        )
        try:
            return notifier.send(
                recipient_list=params.get("receiver__username", []),
            )
        except Exception as e:
            logger.error("Email notification failed: %s", e)


class SmsNotifier(BaseNotifier):
    def __init__(self, title, receivers, message, receiver_nums=""):
        self.receiver_nums = receiver_nums
        super(SmsNotifier, self).__init__(title, receivers, message)

    def send(self, **kwargs):
        notifier = NotifierRegistry.get("sms")(
            self.title,
            self.receivers,
            self.title + self.message,
            receiver_nums=self.receiver_nums,
        )
        try:
            return notifier.send(**kwargs)
        except Exception as e:
            logger.error("SMS notification failed: %s", e)

    @property
    def params(self):
        self.message = self.title + self.message
        if self.receiver_nums:
            return {"receiver": self.receiver_nums, "content": self.message}
        return {"receiver__username": self.receivers, "content": self.message}
