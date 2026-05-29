# BK-ITSM 去蓝鲸依赖重构 — 技术规格文档

## 1. 概述

本文档定义去蓝鲸依赖重构的详细技术规格，包括每个模块的接口定义、数据模型、API 契约和具体实现约束。

---

## 2. 配置层重构

### 2.1 `config/base_settings.py` — 新建

替代 `from blueapps.conf.default_settings import *`，显式定义 Django 基础配置。

**必须包含的配置项**：

```python
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme-in-production")
DEBUG = False
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "itsm.component.middlewares.RequestProvider",  # 已有实现
]

ROOT_URLCONF = "urls"
WSGI_APPLICATION = "wsgi.application"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("BK_MYSQL_NAME", "bk_itsm"),
        "USER": os.environ.get("BK_MYSQL_USER", "root"),
        "PASSWORD": os.environ.get("BK_MYSQL_PASSWORD", ""),
        "HOST": os.environ.get("BK_MYSQL_HOST", "localhost"),
        "PORT": os.environ.get("BK_MYSQL_PORT", "3306"),
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "common.context_processors.mysetting",  # 已有实现
            ],
        },
    },
]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static_root/")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_URL = "/"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URL = "/"
```

### 2.2 `config/__init__.py` — 重写

```python
import os
import sys
from celery import Celery

celery_app = Celery("itsm")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# 项目路径
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT, PROJECT_MODULE_NAME = os.path.split(PROJECT_PATH)
BASE_DIR = PROJECT_ROOT
PYTHON_BIN = os.path.dirname(sys.executable)

# 应用标识（保留但不再绑定蓝鲸含义）
APP_CODE = os.environ.get("APP_CODE", "bk_itsm")
APP_TOKEN = os.environ.get("APP_TOKEN", "")
SECRET_KEY = APP_TOKEN

__all__ = ["celery_app", "APP_CODE", "SECRET_KEY", "BASE_DIR", "PROJECT_ROOT"]
```

移除的变量：`RUN_VER`、`OPEN_VER`、`APP_ID`、`BK_APP_CODE`、`BK_APP_SECRET`、`BK_URL`、`BK_PAAS_HOST`、`BK_PAAS_INNER_HOST`。

### 2.3 `config/default.py` — 修改要点

- 第 30 行 `from blueapps.conf.default_settings import *` → `from config.base_settings import *`
- 第 31 行 `from blueapps.conf.log import get_logging_config_dict` → 删除
- 第 32 行 `from blueapps.opentelemetry.utils import inject_logging_trace_info` → 删除
- LOGGING 改为标准 Django logging dict
- INSTALLED_APPS 中追加业务 apps（itsm.*），不再包含蓝鲸 apps
- MIDDLEWARE 中追加业务中间件（异常处理、CSRF 豁免等）
- 移除所有 `RUN_VER` 条件分支
- 移除 BKCRYPTO 配置
- 移除所有 BK_IAM_*、BK_PAAS_*、BK_CC_*、BK_JOB_* 等蓝鲸平台 host 配置

### 2.4 `config/dev.py` — 修改要点

```python
import importlib
from config import BASE_DIR

# 移除 from blueapps.patch.settings_open_saas import *
# 移除 RUN_VER 条件分支

RUN_MODE = "DEVELOP"
DEBUG = True

STATIC_URL = "/static/"
BROKER_URL = os.environ.get("BROKER_URL", "redis://localhost:6379/0")

# 加载本地覆盖配置
try:
    from .local_settings import *  # noqa
except ImportError:
    pass
```

`config/stag.py` 和 `config/prod.py` 同理，移除 blueapps patch import 和 RUN_VER 分支。

### 2.5 `wsgi.py` — 重写

```python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

## 3. 用户认证模块

### 3.1 `itsm/component/users/models.py` — 新建

```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The username field must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField("用户名", max_length=128, unique=True, db_index=True)
    nickname = models.CharField("昵称", max_length=255, blank=True, default="")
    chname = models.CharField("中文名", max_length=255, blank=True, default="")
    phone = models.CharField("电话", max_length=32, blank=True, default="")
    email = models.EmailField("邮箱", blank=True, default="")
    is_staff = models.BooleanField("后台访问权限", default=False)
    is_active = models.BooleanField("启用", default=True)
    date_joined = models.DateTimeField("注册时间", auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users_user"
        verbose_name = "用户"

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        return self.nickname or self.chname or self.username


class UserProperty(models.Model):
    """兼容 blueapps UserProperty 的扩展属性模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    key = models.CharField(max_length=128)
    value = models.TextField(blank=True, default="")

    class Meta:
        db_table = "users_user_property"
        unique_together = ("user", "key")
```

### 3.2 `itsm/component/users/apps.py` — 新建

```python
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "itsm.component.users"
    label = "users"
    verbose_name = "用户管理"
```

**注意**：`label = "users"` 确保 `AUTH_USER_MODEL = "users.User"` 生效。

### 3.3 `itsm/component/users/urls.py` — 新建

```python
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
```

### 3.4 `itsm/component/users/views.py` — 新建

```python
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "registration/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "/")
        return context

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next", "/")
            return JsonResponse({"result": True, "data": {"redirect_url": next_url}})
        return JsonResponse(
            {"result": False, "message": "用户名或密码错误"}, status=401
        )


def logout_view(request):
    logout(request)
    return JsonResponse({"result": True})
```

### 3.5 `login_exempt` 装饰器

在现有 `itsm/component/decorators.py` 中追加：

```python
def login_exempt(view_func):
    """标记视图免登录检查，兼容 blueapps.account.decorators.login_exempt"""
    view_func.login_exempt = True
    return view_func
```

### 3.6 需更新 import 的文件（10 个）

| 文件 | 旧 import | 新 import |
|------|-----------|-----------|
| `itsm/sites/views.py` | `from blueapps.account.decorators import login_exempt` | `from itsm.component.decorators import login_exempt` |
| `itsm/auth_iam/urls.py` | 同上 | 同上 |
| `itsm/monitor/views.py` | 同上 | 同上 |
| `itsm/openapi/workflow/views.py` | 同上 | 同上 |
| `itsm/openapi/ticket/views.py` | 同上 | 同上 |
| `itsm/openapi/task/views.py` | 同上 | 同上 |
| `itsm/openapi/service/views.py` | 同上 | 同上 |
| `itsm/openapi/base_service/views/workflow_version.py` | 同上 | 同上 |
| `itsm/openapi/base_service/views/service.py` | 同上 | 同上 |
| `itsm/openapi/base_service/views/ticket.py` | 同上 | 同上 |

### 3.7 User 模型引用更新

| 文件 | 旧 import | 新 import |
|------|-----------|-----------|
| `itsm/iadmin/apps.py` | `from blueapps.account.models import User` | `from django.contrib.auth import get_user_model` |
| `itsm/component/utils/user_count.py` | 同上 | 同上 |

---

## 4. 权限系统重构

### 4.1 权限模型映射

蓝鲸 IAM 的权限模型基于 `system → action → resource` 的三层结构，django-guardian 基于 `user/group → permission → object`。映射关系：

| IAM 概念 | guardian 对应 |
|----------|---------------|
| System（itsm） | Django app label |
| Action（project_create, workflow_edit 等） | Django Permission（codename） |
| Resource（project:xxx, workflow:yyy） | guardian ObjectPermission |
| IAM policy query | `guardian.shortcuts.get_objects_for_user` |
| AuthFailedException（499） | `PermissionDenied`（403） |

### 4.2 权限 action 映射表

定义 `itsm/component/permissions/actions.py`：

```python
# 将 IAM 的 37 个 action 映射为 Django permission codename
ACTION_MAP = {
    "project_create": "add_project",
    "project_view": "view_project",
    "project_edit": "change_project",
    "project_delete": "delete_project",
    "workflow_create": "add_workflow",
    "workflow_edit": "change_workflow",
    "workflow_view": "view_workflow",
    "workflow_delete": "delete_workflow",
    "service_create": "add_service",
    "service_edit": "change_service",
    "service_view": "view_service",
    "service_delete": "delete_service",
    # ... 其余 action 按同模式映射
}
```

### 4.3 `itsm/component/drf/permissions.py` — 重写

**保留不变的类**：
- `IsAdmin` — 已用 `UserRole.is_itsm_superuser` 检查，无 IAM 依赖
- `IsManager` — 已用 `UserRole.is_workflow_manager` 检查，无 IAM 依赖

**重写的类**：

```python
from guardian.shortcuts import get_objects_for_user, get_user_perms
from rest_framework import permissions


class ObjectPermission(permissions.BasePermission):
    """
    替代 IamAuthPermit
    基于 django-guardian 的对象级权限检查
    """

    def has_permission(self, request, view):
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action in ["create", "imports"]:
            return self._check_create_permission(request, view)

        if getattr(view, "detail", False):
            return True

        return True  # 集合级写操作交给 has_object_permission

    def has_object_permission(self, request, view, obj):
        if view.action in getattr(view, "permission_free_actions", []):
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        required_perms = self._get_required_permissions(view, obj)
        if not required_perms:
            return True

        return all(request.user.has_perm(perm, obj) for perm in required_perms)

    def _check_create_permission(self, request, view):
        project_key = request.data.get("project_key")
        if not project_key:
            return True
        # 检查用户在项目下是否有创建权限
        from itsm.project.models import Project
        try:
            project = Project.objects.get(key=project_key)
        except Project.DoesNotExist:
            return False
        return request.user.has_perm("add_project", project)

    def _get_required_permissions(self, view, obj):
        action_map = getattr(view, "permission_action_mapping", {})
        action = view.action
        if action in action_map:
            perms = action_map[action]
            return [perms] if isinstance(perms, str) else perms
        default = getattr(view, "permission_action_default", None)
        if default:
            return [default] if isinstance(default, str) else default
        return []


class ResourcePermission(ObjectPermission):
    """替代 IamAuthWithoutResourcePermit"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS and not getattr(view, "detail", False):
            return True
        # 项目查看权限 + 资源类型管理权限
        return True

    def has_object_permission(self, request, view, obj):
        return True


class ProjectViewPermission(ObjectPermission):
    """替代 IamAuthProjectViewPermit"""

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "project_key"):
            return True
        from itsm.project.models import Project
        try:
            Project.objects.get(key=obj.project_key)
        except Project.DoesNotExist:
            return False
        return request.user.has_perm("view_project", obj)


class SystemPermission(permissions.BasePermission):
    """替代 IamAuthSystemPermit — 仅检查 is_staff"""

    def has_permission(self, request, view):
        return request.user.is_staff
```

### 4.4 `itsm/component/generics.py` — 修改

移除：
```python
from iam.exceptions import AuthFailedException
```

移除 `isinstance(exc, AuthFailedException): raise exc` 块。

保留 `IamPermissionDenied` 异常处理（此类是本地定义的），但将 HTTP 状态码从 499 改为 403：

```python
if isinstance(exc, IamPermissionDenied):
    data = {
        "result": False,
        "code": ResponseCodeStatus.PERMISSION_DENIED,
        "message": exc.detail,
        "data": [],
        "permission": exc.data,
    }
    return Response(data, status=status.HTTP_403_FORBIDDEN)
```

### 4.5 业务层权限更新

**`itsm/ticket/permissions.py`**：
- 移除 `from itsm.auth_iam.utils import IamRequest`
- 移除所有 `iam_client.batch_resource_multi_actions_allowed()` 调用
- 用 `UserRole` 直接检查替代（已有 fallback 逻辑）

**其他文件**：`itsm/workflow/views.py`、`itsm/service/permissions.py`、`itsm/project/views.py` 等移除 IAM SDK import。

---

## 5. 通知系统重构

### 5.1 `itsm/component/notifiers/base.py` — 新建

```python
from abc import ABC, abstractmethod
from django.conf import settings


class BaseNotifier(ABC):
    """通知接口抽象基类"""

    @abstractmethod
    def send(self, receivers, title, content, **kwargs):
        """
        发送通知

        Args:
            receivers: 接收人，逗号分隔的用户名或邮箱
            title: 通知标题
            content: 通知内容
            **kwargs: 渠道特定参数
        Returns:
            bool: 是否发送成功
        """
        raise NotImplementedError


class NotifierRegistry:
    """通知渠道注册表"""

    _registry = {}

    @classmethod
    def register(cls, name, notifier_class):
        cls._registry[name] = notifier_class

    @classmethod
    def get(cls, name):
        notifier_class = cls._registry.get(name)
        if notifier_class is None:
            raise KeyError(f"Notifier '{name}' not registered")
        return notifier_class()

    @classmethod
    def list_channels(cls):
        return list(cls._registry.keys())
```

### 5.2 `itsm/component/notifiers/email.py` — 新建

```python
from django.core.mail import send_mail
from django.conf import settings
from .base import BaseNotifier, NotifierRegistry


class EmailNotifier(BaseNotifier):
    """邮件通知渠道"""

    def send(self, receivers, title, content, **kwargs):
        recipient_list = [r.strip() for r in receivers.split(",") if r.strip()]
        try:
            send_mail(
                subject=title,
                message=content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return True
        except Exception:
            return False


NotifierRegistry.register("email", EmailNotifier)
```

### 5.3 `itsm/component/notifiers/sms.py` — 新建

```python
from .base import BaseNotifier, NotifierRegistry


class SmsNotifier(BaseNotifier):
    """短信通知渠道 — 需配置 SMS_BACKEND"""

    def send(self, receivers, title, content, **kwargs):
        # 预留接口，可接入 Twilio / 阿里云 SMS 等
        raise NotImplementedError("SMS backend not configured")


NotifierRegistry.register("sms", SmsNotifier)
```

### 5.4 `itsm/component/notifiers/webhook.py` — 新建

```python
import requests
from django.conf import settings
from .base import BaseNotifier, NotifierRegistry


class WebhookNotifier(BaseNotifier):
    """Webhook 通知渠道 — 支持企业微信/钉钉/飞书机器人"""

    def send(self, receivers, title, content, **kwargs):
        webhook_url = kwargs.get("webhook_url") or getattr(settings, "DEFAULT_WEBHOOK_URL", "")
        if not webhook_url:
            return False

        payload = kwargs.get("payload", {
            "msgtype": "text",
            "text": {"content": f"{title}\n{content}"},
        })
        try:
            resp = requests.post(webhook_url, json=payload, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False


NotifierRegistry.register("webhook", WebhookNotifier)
```

### 5.5 `itsm/component/notifiers/__init__.py` — 新建

```python
# 自动注册所有内置通知渠道
from .email import EmailNotifier      # noqa: F401
from .sms import SmsNotifier          # noqa: F401
from .webhook import WebhookNotifier  # noqa: F401

__all__ = ["EmailNotifier", "SmsNotifier", "WebhookNotifier"]
```

### 5.6 `itsm/component/notify.py` — 重写策略

**现有结构**：`BaseNotifier`（CMSI）、`WeixinNotifier`、`EmailNotifier`、`SmsNotifier` 四个类。

**重写要点**：
- 移除 `from itsm.component.esb.esbclient import client_backend`
- 移除 `from weixin.core.settings import WEIXIN_APP_EXTERNAL_HOST`
- 每个通知渠道改为调用 `NotifierRegistry.get(channel).send(...)`
- ticket 详情链接改为从 `settings.SITE_URL` 构建

---

## 6. 用户查询适配

### 6.1 `itsm/component/utils/user_adapter.py` — 新建

替代 `adapter/config/sites/*/api.py` 中的 `get_batch_users` 和 `get_all_users`。

```python
from django.contrib.auth import get_user_model

User = get_user_model()


def get_batch_users(users, properties="all", is_exact=True, page_params=None, name_type=None):
    """
    批量查询用户信息

    Args:
        users: 用户名列表
        properties: 返回字段（"all" 返回全部）
        is_exact: 精确匹配
        page_params: 分页参数（page, per_page）
        name_type: 名称类型
    Returns:
        list[dict]: 用户信息列表
    """
    if not users:
        return []

    if is_exact:
        qs = User.objects.filter(username__in=users)
    else:
        from functools import reduce
        from django.db.models import Q
        queries = [Q(username__icontains=u) for u in users]
        qs = User.objects.filter(reduce(lambda a, b: a | b, queries))

    if page_params:
        page = page_params.get("page", 1)
        per_page = page_params.get("per_page", 20)
        start = (page - 1) * per_page
        qs = qs[start:start + per_page]

    fields = None if properties == "all" else properties
    if fields:
        qs = qs.values(*fields)
    else:
        qs = qs.values("username", "nickname", "chname", "email", "phone")

    return list(qs)


def get_all_users(users=None):
    """
    查询所有用户或指定用户列表

    Args:
        users: 可选用户名列表，为 None 时返回全部
    Returns:
        list[dict]: 用户信息列表
    """
    qs = User.objects.all()
    if users:
        qs = qs.filter(username__in=users)
    return list(qs.values("username", "nickname", "chname", "email", "phone"))
```

---

## 7. Celery 任务系统

### 7.1 `periodic_task` 替换策略

**旧用法**（8 个文件）：
```python
from blueapps.contrib.celery_tools.periodic import periodic_task

@periodic_task(run_every=crontab(hour="*/1"))
def some_task():
    ...
```

**新用法**：
```python
from celery import shared_task
from celery.schedules import crontab

@shared_task
def some_task():
    ...
```

周期调度通过 `django_celery_beat` 的 `PeriodicTask` 模型在数据迁移中注册。

### 7.2 需更新的 task 文件

| 文件 | 任务功能 |
|------|----------|
| `itsm/workflow/tasks.py` | 流程相关定时任务 |
| `pipeline/log/tasks.py` | Pipeline 日志清理 |
| `pipeline/engine/tasks.py` | Pipeline 引擎任务 |
| `itsm/ticket/tasks.py` | 工单定时任务 |
| `itsm/component/tasks.py` | 通用定时任务 |
| `itsm/openapi/tasks.py` | OpenAPI 定时任务 |
| `itsm/task/tasks.py` | 任务执行定时任务 |
| `itsm/sla_engine/monitor.py` | SLA 监控定时任务 |

---

## 8. 测试文件更新

### 8.1 Celery app import 替换

所有测试文件中的 `from blueapps.core.celery.celery import app` 替换为 `from config import celery_app`。

涉及文件：
- `itsm/tests/workflow/test_base_service.py`
- `itsm/tests/workflow/test_bk_sops.py`
- `itsm/tests/workflow/test_bk_devops.py`
- `itsm/tests/workflow/test_itsm_approve.py`
- `itsm/tests/workflow/test_itsm_auto.py`
- `itsm/tests/workflow/test_webhook.py`
- `itsm/tests/ticket/test_ticket_view.py`
- `itsm/tests/ticket/test_ticket_remark.py`
- `itsm/tests/components/test_utils.py`
- `itsm/tests/helper/test_helper.py`

### 8.2 IAM 测试文件处理

- `itsm/tests/iam/` 目录下所有测试文件 — 删除（IAM 不再存在）
- `itsm/tests/adapter/` 目录下测试文件 — 删除（adapter 不再存在）

---

## 9. 存储系统

### 9.1 替换 bkstorages

**旧实现**（`adapter/utils/storage.py`）：
```python
from bkstorages.backends.rgw import RGWBoto3Storage     # CephStorage
from bkstorages.backends.bkrepo import BKRepoStorage     # RepoStorage
```

**新实现**：
```python
from django.core.files.storage import FileSystemStorage

# 开发环境直接用文件系统
# 生产环境可用 django-storages + boto3 接 S3/MinIO
```

在 `config/default.py` 中：
```python
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
# 或生产环境：
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
```

---

## 10. OpenAPI 认证

### 10.1 `itsm/openapi/authentication/backend.py` — 重写

移除 `apigw_manager.apigw.authentication.UserModelBackend`，用 PyJWT 直接实现：

```python
import jwt
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """替代 apigw_manager 的 JWT 认证"""

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        try:
            user = User.objects.get(username=payload.get("sub"))
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, None)
```

---

## 11. Pipeline 插件处理

### 11.1 需移除的蓝鲸集成组件

| 文件 | 依赖服务 | 处理方式 |
|------|----------|----------|
| `itsm/pipeline_plugins/components/collections/bk_sops.py` | 蓝鲸 SOPS | 移除 |
| `itsm/pipeline_plugins/components/collections/bk_devops.py` | 蓝鲸 DevOps | 移除 |
| `itsm/pipeline_plugins/components/collections/bk_plugin.py` | 蓝鲸插件服务 | 移除 |

### 11.2 保留的组件

- `itsm_approve.py` — 审批节点（纯业务逻辑）
- `itsm_sign.py` — 签节点
- `itsm_auto.py` — 自动节点
- `itsm_migrate.py` — 迁移节点
- `itsm_create.py` — 创建节点
- `webhook.py` — Webhook 节点

---

## 12. 需删除的配置文件

| 文件 | 说明 |
|------|------|
| `app.yml` | 蓝鲸 SaaS 应用描述 |
| `app_desc.yaml` | 蓝鲸容器化应用描述 |
| `Procfile` | 蓝鲸 PaaS 进程配置 |
| `Aptfile` | 蓝鲸 PaaS 系统包 |
| `platform_config/` | 蓝鲸平台配置（MOA 等） |

---

## 13. 环境变量变更

### 13.1 移除的环境变量

- `RUN_VER`、`RUN_ENV`
- `BKPAAS_APP_ID`、`BKPAAS_APP_SECRET`、`BKPAAS_ENVIRONMENT`、`BKPAAS_ENGINE_REGION`
- `BK_PAAS_HOST`、`BK_PAAS_INNER_HOST`
- `BK_IAM_V3_INNER_HOST`、`BK_IAM_INNER_HOST`
- `BK_CC_HOST`、`BK_JOB_HOST`
- `BK_COMPONENT_API_URL`
- `BK_USER_MANAGE_HOST`、`BK_USER_MANAGE_WEIXIN_HOST`
- `BKREPO_ENDPOINT_URL`、`BKREPO_USERNAME`、`BKREPO_PASSWORD`、`BKREPO_PROJECT`、`BKREPO_BUCKET`
- `BKAPP_USE_WEIXIN`、`BKAPP_IS_QY_WEIXIN`、`BKAPP_WEIXIN_APP_ID`
- `USE_IAM`、`IAM_SKIP_AUTH`
- `ENABLE_SYNC_API_GATEWAY`
- `BKCHAT_URL`、`USE_BKCHAT`
- `ITSM_TAPD_APIGW`、`TAPD_OAUTH_URL`

### 13.2 保留/新增的环境变量

- `SECRET_KEY` — Django secret key
- `BK_MYSQL_NAME`、`BK_MYSQL_USER`、`BK_MYSQL_PASSWORD`、`BK_MYSQL_HOST`、`BK_MYSQL_PORT`
- `BROKER_URL` — Celery broker（Redis）
- `BKAPP_REDIS_HOST`、`BKAPP_REDIS_PORT`、`BKAPP_REDIS_PASSWORD`
- `DEBUG` — 调试模式
- `DEFAULT_FROM_EMAIL` — 邮件发送地址
- `DEFAULT_WEBHOOK_URL` — 默认 webhook 地址（新增）
