## Functional Overview

### Module Purpose

角色与权限模块建立本地 RBAC 权限体系，替代原有桩化的蓝鲸 IAM（永远返回 True）。核心解决三个问题：

1. **谁可以做什么**：通过 Role → Permission 映射控制用户对系统功能的访问
2. **权限如何被消费**：后端 DRF `permission_class` 检查 `feature:*` 权限；前端通过 `permissions` 数组驱动路由守卫和组件权限
3. **兼容旧系统**：保留 `is_itsm_superuser()`、`is_workflow_manager()`、`is_statics_manager()` 三个关键权限检查方法

### Permission Code Registry

权限编码格式：`{type}:{module}:{action}`。以下为系统内置的全部权限定义：

#### page 级（页面可见性，前端路由守卫消费）

| Code | 名称 | Category | 说明 |
|------|------|----------|------|
| `page:workflow` | 流程管理 | workflow | 可访问流程管理页面 |
| `page:ticket` | 工单管理 | ticket | 可访问工单列表页面 |
| `page:service` | 服务配置 | service | 可访问服务目录管理页面 |
| `page:sla` | SLA 管理 | sla | 可访问 SLA 策略页面 |
| `page:system` | 系统管理 | system | 可访问系统设置页面 |
| `page:project` | 项目管理 | project | 可访问项目管理页面 |
| `page:statistics` | 运营数据 | ticket | 可访问运营统计页面 |
| `page:task` | 任务管理 | task | 可访问任务管理页面 |

#### button 级（按钮/操作可见性，前端组件消费）

| Code | 名称 | Category | 说明 |
|------|------|----------|------|
| `btn:workflow:create` | 创建流程 | workflow | 流程设计器新建按钮 |
| `btn:workflow:edit` | 编辑流程 | workflow | 流程设计器编辑按钮 |
| `btn:workflow:delete` | 删除流程 | workflow | 流程删除按钮 |
| `btn:workflow:publish` | 发布流程 | workflow | 流程发布按钮 |
| `btn:ticket:create` | 创建工单 | ticket | 新建工单按钮 |
| `btn:ticket:withdraw` | 撤单 | ticket | 工单撤单按钮 |
| `btn:ticket:transfer` | 转单 | ticket | 工单转单按钮 |
| `btn:ticket:close` | 关单 | ticket | 手动关单按钮 |
| `btn:ticket:export` | 导出工单 | ticket | 工单导出按钮 |
| `btn:ticket:comment` | 评论 | ticket | 工单评论按钮 |
| `btn:service:create` | 创建服务 | service | 服务新建按钮 |
| `btn:service:edit` | 编辑服务 | service | 服务编辑按钮 |
| `btn:service:delete` | 删除服务 | service | 服务删除按钮 |
| `btn:sla:create` | 创建SLA | sla | SLA 策略新建按钮 |
| `btn:sla:edit` | 编辑SLA | sla | SLA 策略编辑按钮 |
| `btn:sla:delete` | 删除SLA | sla | SLA 策略删除按钮 |

#### feature 级（后端 API 鉴权，DRF permission_class 消费）

| Code | 名称 | Category | 说明 |
|------|------|----------|------|
| `feature:workflow:manage` | 流程管理权限 | workflow | 管理流程 CRUD API |
| `feature:ticket:operate` | 工单操作权限 | ticket | 处理工单操作 API |
| `feature:ticket:view-all` | 查看全部工单 | ticket | 绕过"仅看本部门"限制 |
| `feature:ticket:export` | 导出工单数据 | ticket | 工单数据导出 API |
| `feature:service:manage` | 服务管理权限 | service | 管理 CRUD API |
| `feature:sla:manage` | SLA 管理权限 | sla | 管理 CRUD API |
| `feature:system:role-manage` | 角色管理 | system | 管理角色 CRUD |
| `feature:system:user-manage` | 用户管理 | system | 管理用户 CRUD |
| `feature:system:group-manage` | 角色组管理 | system | 管理角色组 CRUD |
| `feature:system:department-manage` | 部门管理 | system | 管理部门 CRUD |
| `feature:system:security-manage` | 安全策略管理 | system | 管理安全策略 |
| `feature:system:global-settings` | 全局设置 | system | 修改系统全局配置 |
| `feature:project:manage` | 项目管理权限 | project | 管理项目 CRUD |
| `feature:task:manage` | 任务管理权限 | task | 管理任务 CRUD |

### Built-in Role → Permission Matrix

| Permission Code | SUPERUSER | WORKFLOW_MANAGER | STATICS_MANAGER |
|----------------|-----------|-----------------|----------------|
| 全部 page:* | ✓ | ✓ | page:statistics |
| 全部 btn:* | ✓ | btn:workflow:* | |
| feature:workflow:manage | ✓ | ✓ | |
| feature:ticket:operate | ✓ | | |
| feature:ticket:view-all | ✓ | | ✓ |
| feature:ticket:export | ✓ | | ✓ |
| feature:service:manage | ✓ | | |
| feature:sla:manage | ✓ | | |
| feature:system:* | ✓ | | |
| feature:project:manage | ✓ | | |
| feature:task:manage | ✓ | | |

说明：SUPERUSER 拥有全部权限；WORKFLOW_MANAGER 拥有流程相关权限；STATICS_MANAGER 仅可查看运营数据和导出工单。`user.is_superuser=True` 的用户等同于 SUPERUSER 角色，无需显式分配。

### Permission Consumption Architecture

```
前端                                后端
─────────────────────              ─────────────────────
init/ → permissions[]              
  ↓                                
路由守卫 checkPagePermission()     
  ↓ page:* → 页面是否可见          
  ↓                                
组件内 v-if 判断                    
  ↓ btn:* → 按钮是否显示           
                                   DRF permission_class
                                     ↓ feature:* → API 是否允许
```

**当前前端现状**（需渐进式迁移）：
- `window.IS_ITSM_ADMIN` 和 `window.all_access` 已在前端中成为死代码，不再被任何组件读取
- 前端使用 `usePermission()` composable 消费 IAM actions（如 `operational_data_view`），此部分需逐步替换为读取 `permissions` 数组
- 403 响应通过 bus event 触发跳转到 `/limitAccess` 页面，此机制保持不变

**后端替换策略**：
- `UserRole.is_itsm_superuser()` → `Role.is_itsm_superuser()`，实现不变
- `UserRole.is_workflow_manager()` → `Role.is_workflow_manager()`
- `UserRole.is_statics_manager()` → `Role.is_statics_manager()`
- `IsAdmin` / `IsManager` DRF permission class 继续调用上述方法
- `IamAuthPermit` 及其子类改为基于 `User.has_permission()` 检查，替换 IAM stub

### Key Behaviors

- 权限为纯累加模型：用户拥有多个 Role 时，权限取并集，不冲突
- `user.is_superuser=True` 自动拥有全部权限，不依赖 Role 分配
- 内置 Role（`is_builtin=True`）不可删除，但可修改 members/owners
- 自定义 Role 可由拥有 `feature:system:role-manage` 权限的用户创建
- Role 的 `owners` 拥有该 Role 的编辑权（修改 members、permissions），不等同于拥有该 Role 的权限
- Role 的 `members` 才是"被授予该角色权限的人"

## ADDED Requirements

### Requirement: Permission model
The system SHALL provide a Permission model with fields: `code` (CharField, unique, e.g. `"feature:workflow:manage"`), `name` (CharField, display name), `category` (CharField, one of: workflow, ticket, system, project, role, user), `permission_type` (CharField, one of: page, button, feature), `description` (TextField, blank), `is_builtin` (BooleanField, default=False). Builtin permissions SHALL NOT be deletable through API.

#### Scenario: Create builtin permission
- **WHEN** `init_builtin_data` runs with `--app permission`
- **THEN** permissions like `feature:workflow:manage`, `page:workflow`, `btn:workflow:create` are created with `is_builtin=True`

#### Scenario: Delete builtin permission
- **WHEN** DELETE on a permission with `is_builtin=True`
- **THEN** returns 403 Forbidden

#### Scenario: Delete custom permission
- **WHEN** DELETE on a permission with `is_builtin=False`
- **THEN** permission is deleted

### Requirement: Role model for authorization
The system SHALL provide a Role model for permission authorization with fields: `name` (CharField), `role_key` (CharField, unique), `desc` (TextField, blank), `members` (M2M to User, related_name="auth_roles"), `owners` (M2M to User, related_name="owned_auth_roles"), `permissions` (M2M to Permission, related_name="roles"), `is_builtin` (BooleanField, default=False), plus standard audit fields (creator, create_at, update_at, updated_by, is_deleted). Soft delete SHALL be supported. The Role model SHALL provide `has_permission(code)` method checking if the role grants a specific permission code.

#### Scenario: Role has permission
- **WHEN** a Role has `permissions` containing code `"feature:workflow:manage"`
- **THEN** `role.has_permission("feature:workflow:manage")` returns True

#### Scenario: Role does not have permission
- **WHEN** a Role does not have a permission with code `"feature:ticket:export"`
- **THEN** `role.has_permission("feature:ticket:export")` returns False

### Requirement: User permission check
The system SHALL provide `User.has_permission(code)` method that checks if the user belongs to any Role that grants the specified permission code. This SHALL also check `user.is_superuser` (superusers always have all permissions). The method SHALL NOT conflict with Django's built-in `has_perm()`.

#### Scenario: Superuser has all permissions
- **WHEN** `user.is_superuser` is True
- **THEN** `user.has_permission("any:permission:code")` returns True

#### Scenario: User has permission via role
- **WHEN** user is a member of a Role that has permission `"feature:workflow:manage"`
- **THEN** `user.has_permission("feature:workflow:manage")` returns True

#### Scenario: User lacks permission
- **WHEN** user is not in any Role granting `"feature:system:manage"`
- **THEN** `user.has_permission("feature:system:manage")` returns False

### Requirement: Role CRUD API
The system SHALL provide a DRF ViewSet for Role with list, retrieve, create, update, partial_update, destroy. Creation and modification SHALL be restricted to users with `feature:system:role-manage` permission. The list endpoint SHALL support filtering by `is_builtin`, `project_key` (via role scope). The serializer SHALL represent `members` and `owners` as lists of usernames, and `permissions` as list of permission codes.

#### Scenario: Create role with permissions
- **WHEN** POST `{name: "运维管理员", role_key: "OPS_ADMIN", permissions: ["feature:workflow:manage", "page:workflow"]}`
- **THEN** role is created with specified permissions, returns 201

#### Scenario: List roles
- **WHEN** GET `/api/roles/`
- **THEN** returns all roles with their permission codes and member counts

#### Scenario: Update role members
- **WHEN** PATCH `{members: ["zhangsan", "lisi"]}`
- **THEN** role members are replaced with specified users

### Requirement: Permission CRUD API
The system SHALL provide a DRF ReadOnlyModelViewSet for Permission (list, retrieve). Builtin permissions are read-only. Custom permissions (is_builtin=False) MAY be created by users with `feature:system:role-manage` via a create action.

#### Scenario: List permissions by category
- **WHEN** GET `/api/permissions/?category=workflow`
- **THEN** returns only permissions with category "workflow"

#### Scenario: List permissions by type
- **WHEN** GET `/api/permissions/?permission_type=button`
- **THEN** returns only button-level permissions

### Requirement: User permissions list API
The system SHALL provide `GET /api/users/me/permissions/` returning all permission codes the authenticated user has (aggregated from all their Roles). Response format: `{permissions: ["page:workflow", "btn:workflow:create", ...]}`.

#### Scenario: Get current user permissions
- **WHEN** authenticated user GET `/api/users/me/permissions/`
- **THEN** returns aggregated permission codes from all their Roles

### Requirement: Backward compatible access APIs
The system SHALL keep `UserRole.get_access_by_user(username)` returning list of role_keys the user has in ADMIN-type Roles. `UserRole.is_itsm_superuser(username)` SHALL check if user is in a Role with role_key="SUPERUSER". `UserRole.is_workflow_manager(username)` SHALL check role_key="WORKFLOW_MANAGER". These methods SHALL be reimplemented on the new Role model to maintain backward compatibility during migration.

#### Scenario: is_itsm_superuser backward compat
- **WHEN** `Role.is_itsm_superuser("zhangsan")` is called
- **THEN** returns True if zhangsan is a member of Role with role_key="SUPERUSER"

### Requirement: Role and Permission registered in Django admin
The system SHALL register Role and Permission models in Django admin with appropriate list displays and M2M editing.

#### Scenario: Admin role management
- **WHEN** admin visits `/admin/users/role/`
- **THEN** role list is displayed with inline permission and member editing
