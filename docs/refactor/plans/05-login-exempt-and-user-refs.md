# Plan 05: 替换 login_exempt + User 模型引用

> 前置条件：Plan 04 已完成
> 目标：所有 `blueapps.account` 的 import 替换为本地实现

## 1. 添加 `login_exempt` 装饰器

在 `itsm/component/decorators.py` 中追加：

```python
def login_exempt(view_func):
    """标记视图免登录检查，兼容 blueapps.account.decorators.login_exempt"""
    view_func.login_exempt = True
    return view_func
```

## 2. 替换 `login_exempt` import（12 个文件）

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
| `itsm/component/drf/mixins.py` | 同上 | 同上 |
| `itsm/component/misc_middlewares.py` | 同上 | 同上 |

执行命令（逐个替换）：
```bash
# 验证需要替换的文件
grep -rn "from blueapps.account.decorators import login_exempt" --include="*.py"
```

## 3. 替换 User 模型引用（3 个文件）

| 文件 | 旧 import | 新 import |
|------|-----------|-----------|
| `itsm/iadmin/apps.py` | `from blueapps.account.models import User` | `from django.contrib.auth import get_user_model` |
| `itsm/component/utils/user_count.py` | 同上 | 同上 |
| `weixin/core/middlewares.py` | `from blueapps.account.models import UserProperty` | 此文件在 Plan 10 会随 weixin 一起删除，可暂不处理 |

### `itsm/iadmin/apps.py` 具体改动

```python
# 旧
from blueapps.account.models import User

# 新
from django.contrib.auth import get_user_model
User = get_user_model()
```

### `itsm/component/utils/user_count.py` 具体改动

```python
# 旧
from blueapps.account.models import User

# 新
from django.contrib.auth import get_user_model
User = get_user_model()
```

## 4. 替换其他 blueapps account import

### `itsm/component/esb/esbclient.py`

```python
# 旧
from blueapps.utils import get_client_by_user, get_request

# 暂时替换为 stub（Plan 06 会删除整个 ESB 模块）
# 或者直接注释掉，因为 ESB client 将被移除
```

### `itsm/auth_iam/utils.py`

```python
# 旧
from blueapps.utils import get_client_by_user

# 此文件在 Plan 07 会随 IAM 一起删除，可暂不处理
```

## 验证

```bash
grep -rn "from blueapps.account" --include="*.py" itsm/
# 应仅剩 weixin/ 目录下的引用（Plan 10 处理）

grep -rn "from blueapps.utils" --include="*.py" itsm/
# 应仅剩 ESB 相关文件（Plan 06 处理）
```
