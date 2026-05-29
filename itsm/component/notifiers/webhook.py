# -*- coding: utf-8 -*-
import logging

import requests
from django.conf import settings

from .base import BaseNotifier, NotifierRegistry

logger = logging.getLogger("app")


@NotifierRegistry.register
class WebhookNotifier(BaseNotifier):
    """Generic webhook notifier — POSTs JSON to a configurable URL."""

    channel = "webhook"

    def send(self, **kwargs):
        url = kwargs.get("url") or getattr(settings, "DEFAULT_WEBHOOK_URL", "")
        if not url:
            logger.warning("WebhookNotifier: no DEFAULT_WEBHOOK_URL configured, skipping")
            return

        payload = {
            "title": self.title,
            "receivers": self.receivers,
            "message": self.message,
            **kwargs,
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logger.error("WebhookNotifier send failed: %s", e)
            raise
