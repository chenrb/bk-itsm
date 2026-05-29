# Plan 08: 删除 IAM SDK + auth_iam 模块

> 前置条件：Plan 01-07 已完成
> 目标：移除所有 IAM SDK 代码，为 django-guardian 替代做准备

## 1. 删除目录

| 目录 | 文件数 | 说明 |
|------|--------|------|
| `iam/` | ~71 | IAM SDK 完整库 |
| `itsm/auth_iam/` | ~28 | IAM 集成（utils, resources, signal_handler, urls） |

```bash
rm -rf iam/
rm -rf itsm/auth_iam/
```

## 2. 处理 import 失败的文件

删除后以下文件会因 import 报错，需要在此步骤中处理：

### `itsm/component/drf/permissions.py`

- 移除 `from iam.exceptions import AuthFailedException`
- 移除所有 IAM 相关 import（`from iam import Subject, Action, Resource` 等）
- **临时处理**：将 IAM 权限类（`IamAuthPermit` 等）改为始终返回 True 的 stub
- **最终处理**：Plan 09 用 django-guardian 重写

### `itsm/component/generics.py`

- 移除 `from iam.exceptions import AuthFailedException`
- 移除 `isinstance(exc, AuthFailedException)` 异常处理块
- **最终处理**：Plan 09 完整重写异常处理

### `itsm/component/constants/iam.py`

- 删除此文件
- 更新引用此文件的其他 constants 文件

### `itsm/ticket/permissions.py`

- 移除 `from itsm.auth_iam.utils import IamRequest`
- 移除所有 `iam_client.batch_resource_multi_actions_allowed()` 调用
- **临时处理**：用 `UserRole` 直接检查替代（已有 fallback 逻辑）

### `itsm/component/misc_middlewares.py`

- 移除 `from iam.contrib.django.middlewares import AuthFailedExceptionMiddleware` 相关逻辑
- 移除 Wiki IAM 中间件中的 `IamRequest` 引用

### `itsm/project/handler/utils.py`

- 移除 `from iam.apply.models import *` 等 import
- 移除 IAM 权限迁移相关函数

### 业务层文件（需逐个检查）

搜索所有 IAM import：
```bash
grep -rn "from iam\|from itsm.auth_iam" --include="*.py" itsm/
```

对每个文件：
1. 如果只是 import 但未使用 → 移除 import
2. 如果调用了 IAM API → 暂时用 stub 或 fallback 替代
3. 如果是权限检查 → 改用 `UserRole` 直接检查

### IAM 相关 URL

- `itsm/auth_iam/urls.py` 已随目录删除
- 检查 `urls.py` 中是否有 `include("itsm.auth_iam.urls")`，如有则移除

## 3. 移除 IAM 配置

在 `config/default.py` 中（Plan 02 应已移除大部分）：
- 确认 `USE_IAM` 条件块已移除
- 确认 `BK_IAM_*` 配置已移除
- 确认 INSTALLED_APPS 中无 `"iam"`, `"iam.contrib.iam_migration"`, `"itsm.auth_iam"`

## 4. 处理测试文件

删除 IAM 相关测试：
```bash
rm -rf itsm/tests/iam/
```

## 验证

```bash
grep -rn "from iam " --include="*.py" itsm/
grep -rn "from itsm.auth_iam" --include="*.py" itsm/
# 均应返回零匹配

ls iam/ itsm/auth_iam/ 2>&1
# 应显示 "No such file or directory"
```
