# -*- coding: utf-8 -*-
"""Celery 配置"""
import os

IS_USE_CELERY = True
CELERYD_CONCURRENCY = os.getenv("BK_CELERYD_CONCURRENCY", 2)

CELERY_IMPORTS = (
    "itsm.helper.tasks",
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

STATSD_HOST = os.environ.get("STATSD_HOST", "localhost")
STATSD_PORT = os.environ.get("STATSD_PORT", 8125)
STATSD_PREFIX = os.environ.get("STATSD_PREFIX", None)
