# -*- coding: utf-8 -*-
import os

from celery import Celery

celery_app = Celery("itsm")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT, PROJECT_MODULE_NAME = os.path.split(PROJECT_PATH)
BASE_DIR = PROJECT_ROOT

APP_CODE = os.environ.get("APP_CODE", "bk_itsm")
SECRET_KEY = os.environ.get("SECRET_KEY", "")

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

__all__ = ["celery_app", "APP_CODE", "SECRET_KEY", "BASE_DIR", "PROJECT_ROOT", "DEBUG"]
