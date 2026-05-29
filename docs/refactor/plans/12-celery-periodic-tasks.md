# Plan 12: 替换 periodic_task 装饰器 + Celery 引用清理

> 前置条件：Plan 01-03 已完成
> 目标：所有 task 文件不再依赖 blueapps Celery 工具

## 1. 替换 periodic_task 装饰器

### 旧用法

```python
from blueapps.contrib.celery_tools.periodic import periodic_task

@periodic_task(run_every=crontab(hour="*/1"))
def some_task():
    ...
```

### 新用法

```python
from celery import shared_task

@shared_task
def some_task():
    ...
```

周期调度改用 `django_celery_beat` 在数据迁移中注册。

### 需更新的 8 个文件

| 文件 | 旧 import |
|------|-----------|
| `itsm/workflow/tasks.py` | `from blueapps.contrib.celery_tools.periodic import periodic_task` |
| `pipeline/log/tasks.py` | 同上 |
| `pipeline/engine/tasks.py` | 同上 |
| `itsm/ticket/tasks.py` | 同上 |
| `itsm/component/tasks.py` | 同上 |
| `itsm/openapi/tasks.py` | 同上 |
| `itsm/task/tasks.py` | 同上 |
| `itsm/sla_engine/monitor.py` | 同上 |

对每个文件：
1. 将 `from blueapps.contrib.celery_tools.periodic import periodic_task` 替换为 `from celery import shared_task`
2. 将 `@periodic_task(run_every=crontab(...))` 替换为 `@shared_task`
3. 保留 `run_every` 参数信息为注释，供后续 `django_celery_beat` 配置参考

## 2. 替换 Celery app import

### 旧用法

```python
from blueapps.core.celery.celery import app
```

### 新用法

```python
from config import celery_app
```

### 需更新的文件

搜索：
```bash
grep -rn "from blueapps.core.celery" --include="*.py"
```

更新所有匹配文件。

## 3. 替换 blueapps logger

### 旧用法

```python
from blueapps.utils.logger import logger_celery as logger
```

### 新用法

```python
import logging
logger = logging.getLogger("celery")
```

涉及文件：`itsm/pipeline_plugins/components/collections/itsm_auto.py`

## 4. 注册周期任务到 django_celery_beat

创建数据迁移 `itsm/helper/migrations/xxxx_register_periodic_tasks.py`：

```python
from django.db import migrations
from django_celery_beat.models import PeriodicTask, CrontabSchedule


def register_periodic_tasks(apps, schema_editor):
    schedules = {
        "workflow-hourly": CrontabSchedule.objects.create(minute="0", hour="*/1"),
        "ticket-every-5min": CrontabSchedule.objects.create(minute="*/5"),
        # 按原 periodic_task 的 run_every 参数配置
    }
    for name, schedule in schedules.items():
        PeriodicTask.objects.get_or_create(
            name=name,
            defaults={
                "crontab": schedule,
                "task": f"itsm.{name.replace('-', '.')}",
                "enabled": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("helper", "previous_migration"),
    ]
    operations = [
        migrations.RunPython(register_periodic_tasks, migrations.RunPython.noop),
    ]
```

## 验证

```bash
grep -rn "blueapps.*celery\|from blueapps.contrib.celery_tools\|from blueapps.core.celery" --include="*.py"
# 应返回零匹配

grep -rn "periodic_task" --include="*.py" itsm/ pipeline/
# 应无 blueapps periodic_task 引用
```
