# Plan 03: 简化 settings.py + 环境配置

> **状态：已完成**
> 原 Plan 03 内容已合并到 Plan 01/02 中执行

## 实际改动

### 1. `settings.py` 简化

从动态环境检测 + 多模块加载 → 直接加载：

```python
import pymysql
pymysql.install_as_MySQLdb()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from config.default import *  # noqa
try:
    from config.local_settings import *  # noqa
except ImportError:
    pass
```

移除了：
- BKPAAS_ENVIRONMENT / BK_ENV 环境检测
- saas_conf_module 动态 import
- weixin_conf_module 动态 import
- miniweixin_conf_module 动态 import

### 2. 删除 dev/stag/prod 多环境配置

- 删除 `config/dev.py`、`config/stag.py`、`config/prod.py`
- 环境差异全部由 env vars 驱动（`DEBUG`、`BROKER_URL`、`DATABASES` 等）
- 本地开发通过 `config/local_settings.py` 覆盖

### 3. requirements.txt 更新

已在前期完成：Python 3.13 + Django 6.0 依赖版本更新。
