# -*- coding: utf-8 -*-
"""Celery 配置"""
import os

CELERY_IMPORTS = (
    "itsm.ticket.tasks",
    "itsm.service.tasks",
    "itsm.sla_engine.monitor",
    "itsm.trigger.tasks",
    "itsm.task.tasks",
)

CELERY_ACCEPT_CONTENT = ["pickle", "json"]
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"

CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_ENABLE_UTC = True
DJANGO_CELERY_BEAT_TZ_AWARE = True

BROKER_URL = os.environ.get("BROKER_URL", "redis://localhost:6379/0")

CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

from pipeline.celery.settings import *  # noqa
