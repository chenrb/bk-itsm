# Plan 06: 删除 ESB / blueking / adapter 通信层

> 前置条件：Plan 01-05 已完成
> 目标：移除所有外部蓝鲸服务通信代码

## 1. 删除目录

| 目录 | 文件数 | 说明 |
|------|--------|------|
| `blueking/` | ~50 | ESB SDK（含 tests） |
| `itsm/component/esb/` | 3 | ESB 封装（esbclient.py, backend_component.py, __init__.py） |
| `itsm/component/bkoauth/` | ~5 | OAuth 认证 |
| `itsm/component/auto_register/` | ~5 | 自动注册 |
| `itsm/plugin_service/` | ~10 | 插件服务 |
| `adapter/` | ~15 | 环境适配层 |

```bash
rm -rf blueking/
rm -rf itsm/component/esb/
rm -rf itsm/component/bkoauth/
rm -rf itsm/component/auto_register/
rm -rf itsm/plugin_service/
rm -rf adapter/
```

## 2. 处理 ESB 消费方

删除以上目录后，以下文件会因 import 失败报错，需要处理：

### `itsm/component/notify.py`

- 移除 `from itsm.component.esb.esbclient import client_backend`
- 通知发送逻辑暂时注释或 stub（Plan 09 会用新的 Notifier 接口替换）

### `itsm/gateway/views.py`

- 移除 `from adapter.config.sites.open.api import *` 等适配器 import
- 用 `user_adapter` 替代（Plan 07 创建）

### `itsm/sites/views.py`

- 移除 `from adapter.config.sites.open.api import get_batch_users` 等 import
- 用 `user_adapter` 替代

### `itsm/helper/tasks.py`

- 移除 `from adapter.config.sites.open.api import get_batch_users` 等 import
- 用 `user_adapter` 替代

### `itsm/component/tasks.py`

- 移除 adapter 相关 import
- 用 `user_adapter` 替代

### `itsm/openapi/apps.py`

- 移除 `from blueapps.utils import get_client_by_user` import
- 移除 ESB 公钥同步逻辑

### `celery_statsd.py`

- 移除 `from blueapps.core.celery import celery_app` → 改为 `from config import celery_app`

## 3. 处理 pipeline_plugins 蓝鲸组件

删除以下文件：
- `itsm/pipeline_plugins/components/collections/bk_sops.py`
- `itsm/pipeline_plugins/components/collections/bk_devops.py`
- `itsm/pipeline_plugins/components/collections/bk_plugin.py`

这些文件依赖 blueking ESB 和蓝鲸 SOPS/DevOps 服务。

同时更新组件注册，确保这三个组件不再被加载：
- 检查 `itsm/pipeline_plugins/components/collections/__init__.py` 中是否有显式注册
- 检查是否有 YAML 配置文件引用这些组件

## 验证

```bash
# 确认目录已删除
ls blueking/ adapter/ itsm/component/esb/ itsm/component/bkoauth/ itsm/component/auto_register/ itsm/plugin_service/ 2>&1
# 应全部显示 "No such file or directory"

# 确认无残留 import
grep -rn "from blueking\|from itsm.component.esb\|from adapter\|from itsm.component.bkoauth\|from itsm.plugin_service" --include="*.py"
# 应返回零匹配
```
