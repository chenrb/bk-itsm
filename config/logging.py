# -*- coding: utf-8 -*-
"""日志配置"""
import os

from config import BASE_DIR  # noqa

LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "itsm.log"),
            "maxBytes": 1024 * 1024 * 50,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "itsm": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
    },
}

ENABLE_OTEL_TRACE = os.getenv("BKAPP_ENABLE_OTEL_TRACE", "0") == "1"
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
