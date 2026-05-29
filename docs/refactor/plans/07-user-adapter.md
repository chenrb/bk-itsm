# Plan 07: 创建 user_adapter.py — 本地用户查询

> 前置条件：Plan 04（User 模型）、Plan 06（ESB/adapter 删除）已完成
> 目标：替代 adapter 中 `get_batch_users` / `get_all_users` 等用户查询接口

## 1. 新建 `itsm/component/utils/user_adapter.py`

```python
from django.contrib.auth import get_user_model

User = get_user_model()

USER_FIELDS = ("username", "nickname", "chname", "email", "phone")


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

    return list(qs.values(*USER_FIELDS))


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
    return list(qs.values(*USER_FIELDS))
```

## 2. 更新消费方文件

### `itsm/sites/views.py`

```python
# 旧
from adapter.config.sites.open.api import get_batch_users, get_all_users

# 新
from itsm.component.utils.user_adapter import get_batch_users, get_all_users
```

### `itsm/gateway/views.py`

```python
# 旧
from adapter.config.sites.open.api import get_batch_users

# 新
from itsm.component.utils.user_adapter import get_batch_users
```

### `itsm/helper/tasks.py`

```python
# 旧
from adapter.config.sites.open.api import get_batch_users

# 新
from itsm.component.utils.user_adapter import get_batch_users
```

### `itsm/component/tasks.py`

```python
# 旧
from adapter.config.sites.open.api import get_batch_users

# 新
from itsm.component.utils.user_adapter import get_batch_users
```

### 其他引用 `get_batch_users` 的文件

搜索所有引用：
```bash
grep -rn "get_batch_users\|get_all_users" --include="*.py" itsm/
```

逐个替换 import 来源。

## 3. 处理其他 adapter API

`adapter/config/sites/open/api.py` 可能还导出其他函数，如：
- `get_login_url` → 改为 `"/account/login/"`
- `get_title` → 直接读取 `settings.CUSTOM_TITLE`
- `get_footer` → 直接读取 `settings.FOOTER`

搜索所有 adapter import 确认：
```bash
grep -rn "from adapter" --include="*.py" itsm/
```

## 验证

```bash
grep -rn "from adapter" --include="*.py" itsm/
# 应返回零匹配

python -c "from itsm.component.utils.user_adapter import get_batch_users, get_all_users; print('OK')"
```
