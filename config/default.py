# -*- coding: utf-8 -*-
"""
Django settings 入口 — 按类别拆分，此文件仅做聚合。
各子模块见 config/*.py
"""
from config.apps import *  # noqa
from config.celery import *  # noqa
from config.logging import *  # noqa
from config.database import *  # noqa
from config.web import *  # noqa
from config.i18n import *  # noqa
from config.pipeline import *  # noqa
from config.business import *  # noqa
from config.integrations import *  # noqa
from config.monitoring import *  # noqa
