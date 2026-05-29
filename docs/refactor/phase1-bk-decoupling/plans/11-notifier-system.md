# Plan 11: 通知系统 — 抽象 Notifier 接口

> 前置条件：Plan 06（ESB 删除）、Plan 10（weixin 删除）已完成
> 目标：通知不再依赖蓝鲸 CMSI，改用可插拔的 Notifier 接口

## 1. 新建 `itsm/component/notifiers/__init__.py`

```python
from .email import EmailNotifier
from .sms import SmsNotifier
from .webhook import WebhookNotifier

__all__ = ["EmailNotifier", "SmsNotifier", "WebhookNotifier"]
```

## 2. 新建 `itsm/component/notifiers/base.py`

```python
from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """通知接口抽象基类"""

    @abstractmethod
    def send(self, receivers, title, content, **kwargs):
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

## 3. 新建 `itsm/component/notifiers/email.py`

```python
from django.core.mail import send_mail
from django.conf import settings
from .base import BaseNotifier, NotifierRegistry


class EmailNotifier(BaseNotifier):
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

## 4. 新建 `itsm/component/notifiers/sms.py`

```python
from .base import BaseNotifier, NotifierRegistry


class SmsNotifier(BaseNotifier):
    def send(self, receivers, title, content, **kwargs):
        raise NotImplementedError("SMS backend not configured")


NotifierRegistry.register("sms", SmsNotifier)
```

## 5. 新建 `itsm/component/notifiers/webhook.py`

```python
import requests
from django.conf import settings
from .base import BaseNotifier, NotifierRegistry


class WebhookNotifier(BaseNotifier):
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

## 6. 重写 `itsm/component/notify.py`

**现有结构**：`BaseNotifier`（CMSI）、`WeixinNotifier`、`EmailNotifier`、`SmsNotifier` 四个类。

**重写要点**：
- 移除 `from itsm.component.esb.esbclient import client_backend`
- 移除 `from weixin.core.settings import WEIXIN_APP_EXTERNAL_HOST`
- 每个通知渠道改为调用 `NotifierRegistry.get(channel).send(...)`
- ticket 详情链接改为从 `settings.SITE_URL` 构建

### 具体改动

```python
from django.conf import settings
from itsm.component.notifiers.base import NotifierRegistry

# 替换所有 client_backend.cmsi.* 调用
# 替换所有 WeixinNotifier 调用为 WebhookNotifier

def send_notify(receivers, title, content, channel="email", **kwargs):
    """统一通知发送入口"""
    try:
        notifier = NotifierRegistry.get(channel)
        return notifier.send(receivers, title, content, **kwargs)
    except Exception:
        return False
```

保留业务层调用接口不变，只改底层实现。

## 7. 更新 `config/default.py`

添加邮件配置：
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 25))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "false").lower() == "true"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "itsm@localhost")
DEFAULT_WEBHOOK_URL = os.environ.get("DEFAULT_WEBHOOK_URL", "")
```

## 验证

```bash
python -c "from itsm.component.notifiers import NotifierRegistry; print(NotifierRegistry.list_channels())"
# 应输出 ['email', 'sms', 'webhook']

grep -rn "client_backend.cmsi\|from itsm.component.esb" --include="*.py" itsm/component/notify.py
# 应返回零匹配
```
