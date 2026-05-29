# -*- coding: utf-8 -*-
"""
Django settings 入口 — 按类别拆分，此文件仅做聚合。
各子模块见 config/*.py
"""
from config.base_settings import *  # noqa

from config.env import *  # noqa
from config.apps import *  # noqa
from config.celery import *  # noqa
from config.logging import *  # noqa
from config.database import *  # noqa
from config.api import *  # noqa
from config.i18n import *  # noqa
from config.wiki import *  # noqa
from config.pipeline import *  # noqa
from config.business import *  # noqa
from config.platform import *  # noqa
from config.monitoring import *  # noqa

# Celery beat scheduler + pipeline celery settings
if IS_USE_CELERY:  # noqa: F405
    INSTALLED_APPS += ("django_celery_beat", "django_celery_results")  # noqa: F405
    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
    from pipeline.celery.settings import *  # noqa
