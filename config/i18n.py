# -*- coding: utf-8 -*-
"""国际化配置"""
import os

from config import BASE_DIR  # noqa

LANGUAGE_CODE = os.environ.get("BKAPP_BACKEND_LANGUAGE", "zh-hans")
SITE_ID = 1
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)


def _(s):
    return s


LANGUAGES = (
    ("en", _("English")),
    ("zh-cn", _("简体中文")),
    ("ja", _("日本語")),
)

LANGUAGE_SESSION_KEY = "blueking_language"
LANGUAGE_COOKIE_NAME = "blueking_language"
