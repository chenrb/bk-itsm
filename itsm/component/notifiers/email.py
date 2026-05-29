# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.core.mail import send_mail

from .base import BaseNotifier, NotifierRegistry

logger = logging.getLogger("app")


@NotifierRegistry.register
class EmailNotifier(BaseNotifier):
    channel = "email"

    def send(self, **kwargs):
        subject = self.title
        message = self.message
        recipient_list = kwargs.get("recipient_list")
        if not recipient_list:
            if isinstance(self.receivers, (list, tuple)):
                recipient_list = self.receivers
            else:
                recipient_list = [self.receivers]

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            logger.error("EmailNotifier send failed: %s", e)
            raise
