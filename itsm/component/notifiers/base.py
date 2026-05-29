# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """Abstract base class for notification channels."""

    channel = None

    def __init__(self, title, receivers, message, **kwargs):
        self.title = title
        self.receivers = receivers
        self.message = message

    @abstractmethod
    def send(self, **kwargs):
        raise NotImplementedError


class NotifierRegistry:
    """Registry of available notification channels."""

    _registry = {}

    @classmethod
    def register(cls, notifier_class):
        channel = notifier_class.channel
        if channel is None:
            raise ValueError("Notifier must define a `channel` attribute")
        cls._registry[channel] = notifier_class
        return notifier_class

    @classmethod
    def get(cls, channel):
        if channel not in cls._registry:
            raise KeyError(f"Unknown notification channel: {channel}")
        return cls._registry[channel]

    @classmethod
    def list_channels(cls):
        return list(cls._registry.keys())
