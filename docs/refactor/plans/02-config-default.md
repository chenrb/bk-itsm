# Plan 02: 拆分 config/default.py 为子模块

> **状态：已完成**
> 原目标"重写 config/default.py"已调整为按配置类别拆分

## 文件结构

```
config/
  __init__.py          # celery_app, APP_CODE, BASE_DIR, PROJECT_ROOT
  base_settings.py     # Django 基础默认值（Django 内置 apps、中间件、数据库、模板）
  default.py           # 薄聚合（20行），from config.xxx import *
  env.py               # 环境变量 + 兼容垫片（BK_PAAS_HOST 等）+ 静态文件
  apps.py              # INSTALLED_APPS + MIDDLEWARE + AUTHENTICATION_BACKENDS
  celery.py            # Celery 配置 + 时区
  logging.py           # LOGGING 配置
  database.py          # CACHES + Redis + 数据后端 + DatabaseFeatures patch
  api.py               # REST_FRAMEWORK + TEMPLATES + CSRF/Session
  i18n.py              # 国际化配置
  wiki.py              # Wiki 配置
  pipeline.py          # Pipeline/RPC/Trigger/SLA 配置
  business.py          # 业务环境变量
  platform.py          # 蓝鲸平台兼容配置（TODO: 后续 plan 清理）
  monitoring.py        # 监控配置
```

## 关键改动

### Celery 时区配置

```python
# config/celery.py
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_ENABLE_UTC = True
DJANGO_CELERY_BEAT_TZ_AWARE = True
```

配合 `base_settings.py` 中的 `USE_TZ = True`：
- DB 存储统一 UTC
- Celery worker 内部消息用 UTC
- crontab 按 Asia/Shanghai 解释执行

### LOGGING 重写

移除 `get_logging_config_dict(locals())`（blueapps 依赖），替换为标准 Django logging dict。

### 兼容垫片

`config/env.py` 保留 `BK_PAAS_HOST`/`BK_URL`/`RUN_VER` 等变量（从 env vars 读取），
供 `config/platform.py` 等待清理模块引用。后续 plan 逐步移除。

## 验证

```bash
python -c "
import os; os.environ.setdefault('SECRET_KEY','test'); os.environ.setdefault('BK_MYSQL_NAME','test')
os.environ.setdefault('BK_MYSQL_USER','root'); os.environ.setdefault('BK_MYSQL_PASSWORD','')
os.environ.setdefault('BK_MYSQL_HOST','localhost'); os.environ.setdefault('BK_MYSQL_PORT','3306')
import pymysql; pymysql.install_as_MySQLdb()
import importlib; m = importlib.import_module('config.default')
d = {k:v for k,v in vars(m).items() if k.isupper()}
print(len(d), d.get('USE_TZ'), d.get('CELERY_TIMEZONE'))
"  # 应输出 223+ True Asia/Shanghai
```
