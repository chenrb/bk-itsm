# Plan 01: 基础设施 — base_settings.py / config/__init__.py / wsgi.py

> **状态：已完成**

## 实际改动

### 1. 新建 `config/base_settings.py`

替代 `from blueapps.conf.default_settings import *`，显式定义 Django 基础配置：
- `INSTALLED_APPS`（tuple，仅 Django 内置 6 个）
- `MIDDLEWARE`（Django 标准中间件 + whitenoise）
- `DATABASES`（从 env vars 读取）
- `TEMPLATES`（Django 模板后端）
- `USE_TZ = True`, `TIME_ZONE = "Asia/Shanghai"`
- `AUTHENTICATION_BACKENDS`, `ROOT_URLCONF`, `WSGI_APPLICATION`

### 2. 重写 `config/__init__.py`

- 原生 Celery 替代 `blueapps.core.celery`
- 移除 `RUN_VER`/`BK_URL`/`BK_PAAS_HOST`/`BK_PAAS_INNER_HOST`/`OPEN_VER`/`APP_ID`/`BK_APP_CODE`/`BK_APP_SECRET`
- 保留 `celery_app`/`APP_CODE`/`SECRET_KEY`/`BASE_DIR`/`PROJECT_ROOT`/`APP_TOKEN`

### 3. 重写 `wsgi.py`

标准 Django WSGI，移除 `blueapps.core.wsgi` 依赖。

### 4. 简化 `settings.py`

直接 `from config.default import *` + `local_settings.py` 覆盖。
移除 weixin/miniweixin/saas 动态 import 块。
移除 BKPAAS_ENVIRONMENT/BK_ENV 多环境检测逻辑。

### 5. 删除 `config/dev.py`/`config/stag.py`/`config/prod.py`

合并为 `config/default.py`，环境差异全部由 env vars 驱动。

### 6. 拆分 `config/default.py` 为子模块

从 1040 行拆为 13 个子模块（详见 Plan 02）。

### 7. 移除 RequestProvider 中间件

从 `base_settings.py` 和 `config/default.py` 的 MIDDLEWARE 中移除。

## 验证

```bash
python -c "from config.base_settings import INSTALLED_APPS; print(len(INSTALLED_APPS))"  # 6
python -c "from config import celery_app; print(type(celery_app).__name__)"  # Celery
python -c "import settings; print(getattr(settings, 'USE_TZ'))"  # True
```
