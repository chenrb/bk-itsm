## Purpose

角色与权限模块建立本地 RBAC 权限体系，替代原有桩化的蓝鲸 IAM（永远返回 True）。核心解决谁可以做什么、权限如何被消费、以及兼容旧系统三个问题。

## Requirements

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
