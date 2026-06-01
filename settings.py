# -*- coding: utf-8 -*-
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from config.default import *  # noqa

# 本地配置覆盖（不纳入版本管理）
try:
    from config.local_settings import *  # noqa
except ImportError:
    pass
