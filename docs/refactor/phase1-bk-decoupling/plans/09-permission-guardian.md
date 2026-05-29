# Plan 09: 权限系统 — 用 django-guardian 替代 IAM

> 前置条件：Plan 08（IAM SDK 已删除）已完成
> 目标：所有 API 权限检查走 django-guardian + Django 内置权限

## 1. 安装和配置 django-guardian

### `requirements.txt`

确认已添加 `django-guardian==2.4.0`。

### `config/default.py`

```python
INSTALLED_APPS += ("guardian",)

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
]
```

### 运行迁移

```bash
python manage.py migrate
```

## 2. 重写 `itsm/component/drf/permissions.py`

### 保留不变的类

- `IsAdmin` — 已用 `UserRole.is_itsm_superuser` 检查，无 IAM 依赖
- `IsManager` — 已用 `UserRole.is_workflow_manager` 检查，无 IAM 依赖

### 新增 guardian 权限类

```python
from guardian.shortcuts import get_objects_for_user, get_user_perms
from rest_framework import permissions


class ObjectPermission(permissions.BasePermission):
    """替代 IamAuthPermit — 基于 django-guardian 的对象级权限"""

    def has_permission(self, request, view):
        if view.action in getattr(view, "permission_free_actions", []):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action in ["create", "imports"]:
            return self._check_create_permission(request, view)
        return True

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

### 删除的类

- `IamAuthPermit` → 用 `ObjectPermission` 替代
- `IamAuthWithoutResourcePermit` → 用 `ResourcePermission` 替代
- `IamAuthProjectViewPermit` → 用 `ProjectViewPermission` 替代
- `IamAuthSystemPermit` → 用 `SystemPermission` 替代

## 3. 重写 `itsm/component/generics.py` 异常处理

### 移除

```python
from iam.exceptions import AuthFailedException
```

### 修改

将 `IamPermissionDenied` 异常的 HTTP 状态码从 499 改为 403：

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

移除 `isinstance(exc, AuthFailedException): raise exc` 块。

## 4. 更新业务层权限调用

### `itsm/ticket/permissions.py`

- 已在 Plan 08 移除 `IamRequest` import
- 确认用 `UserRole` 直接检查的 fallback 逻辑完整

### `itsm/service/permissions.py`

- 移除 IAM 相关 import 和调用
- 用 guardian `get_objects_for_user` 替代

### `itsm/workflow/views.py`

- 移除 IAM 权限检查
- 确认用新的 guardian 权限类保护

### `itsm/project/views.py`

- 移除 IAM 权限检查
- 确认用新的 guardian 权限类保护

### 搜索所有残留 IAM 权限调用

```bash
grep -rn "IamRequest\|iam_client\|AuthFailedException" --include="*.py" itsm/
```

## 5. 权限 action 映射

新建 `itsm/component/permissions/actions.py`（可选，如业务需要）：

```python
ACTION_MAP = {
    "project_create": "add_project",
    "project_view": "view_project",
    "project_edit": "change_project",
    "project_delete": "delete_project",
    "workflow_create": "add_workflow",
    "workflow_edit": "change_workflow",
    "workflow_view": "view_workflow",
    "workflow_delete": "delete_workflow",
    # ... 按业务需求补充
}
```

## 验证

```bash
python manage.py check
grep -rn "IamAuth\|IamRequest\|iam_client\|AuthFailedException" --include="*.py" itsm/
# 应返回零匹配
```
