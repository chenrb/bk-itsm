## Functional Overview

### Module Purpose

前端权限对接层负责将后端返回的 `permissions` 数组集成到前端权限检查体系中。包括：从 `/init/` 接口读取权限并存入 Vuex、路由守卫检查页面权限、组件内按钮/功能权限检查。

### Business Capabilities

1. **权限加载**：从 `/init/` 响应的 `permissions` 字段读取当前用户的权限编码列表
2. **权限存储**：将权限列表存入 Vuex Store，全局可访问
3. **路由守卫**：检查 `page:*` 权限决定页面是否可访问
4. **组件权限**：检查 `btn:*` 和 `feature:*` 权限决定按钮/操作是否显示
5. **兼容过渡**：支持旧 IAM action 字符串和新权限编码格式并存

### Integration Points

- **API**: `GET /init/` 响应中的 `permissions` 字段（由后端 `user-management-module` auth spec 定义）
- **Store**: 扩展现有 user store 或新增 `permission` store 模块
- **Composable**: 扩展 `usePermission` composable
- **Router**: 扩展路由守卫 `beforeEach`

### Key Behaviors

- `permissions` 数组在 `/init/` 调用时一次性加载，存入 Vuex
- `is_superuser=true` 的用户自动拥有全部权限（前端不依赖 permissions 数组做超管判断）
- 权限编码格式：`{type}:{module}:{action}`（如 `page:workflow`、`btn:ticket:create`、`feature:system:user-manage`）
- 旧格式 `user_create` 等在过渡期仍可使用，通过映射表转换

## ADDED Requirements

### Requirement: Load permissions from init endpoint
The system SHALL read the `permissions` array from the `/init/` API response and store it in the Vuex store under `state.user.permissions`. This SHALL happen during app initialization (same lifecycle as existing init data loading). If the `permissions` field is missing or empty, the store SHALL default to an empty array.

#### Scenario: Init with permissions
- **WHEN** app loads and calls `GET /init/` which returns `{permissions: ["page:workflow", "feature:system:user-manage", ...]}`
- **THEN** the permissions array is stored in `this.$store.state.user.permissions`

#### Scenario: Init without permissions
- **WHEN** `GET /init/` returns response without `permissions` field
- **THEN** `this.$store.state.user.permissions` is set to empty array `[]`

#### Scenario: Superuser handling
- **WHEN** `GET /init/` returns `{IS_ITSM_ADMIN: true}` for a superuser
- **THEN** frontend treats this user as having all permissions regardless of `permissions` array content

### Requirement: Extended usePermission composable
The system SHALL extend the existing `usePermission` composable (at `src/composables/usePermission.js`) with a new method `hasPermissionCode(code)` that checks if the current user's `permissions` array contains the specified permission code string. This SHALL work alongside the existing `hasPermission(required, current)` method for backward compatibility.

#### Scenario: Check feature permission
- **WHEN** `hasPermissionCode("feature:system:user-manage")` is called and user's permissions include `"feature:system:user-manage"`
- **THEN** returns `true`

#### Scenario: Check missing permission
- **WHEN** `hasPermissionCode("feature:system:user-manage")` is called and user's permissions do not include it
- **THEN** returns `false`

#### Scenario: Superuser has all permissions
- **WHEN** `hasPermissionCode("feature:system:user-manage")` is called for a superuser
- **THEN** returns `true` regardless of permissions array content

#### Scenario: Backward compatibility with old format
- **WHEN** existing code calls `hasPermission(['user_create'], currentActions)`
- **THEN** the old method continues to work unchanged

### Requirement: Route guard for page permissions
The system SHALL extend the Vue Router `beforeEach` guard to check `page:*` permissions. Each route MAY define a `meta.permission` field containing a page-level permission code (e.g., `page:workflow`). If the user does not have this permission, the route guard SHALL redirect to a "no access" page (existing `/limitAccess` route).

#### Scenario: Access page with permission
- **WHEN** user navigates to route with `meta: {permission: "page:workflow"}` and user has `"page:workflow"` in permissions
- **THEN** navigation proceeds normally

#### Scenario: Access page without permission
- **WHEN** user navigates to route with `meta: {permission: "page:system"}` and user does NOT have `"page:system"` in permissions
- **THEN** router redirects to `/limitAccess` page

#### Scenario: Route without permission meta
- **WHEN** user navigates to route without `meta.permission` defined
- **THEN** navigation proceeds normally (no permission check)

### Requirement: Component-level permission directive
The system SHALL provide a Vue directive `v-permission` that conditionally renders an element based on the current user's permissions. The directive SHALL accept a permission code string (e.g., `"feature:system:user-manage"`) and hide the element if the user lacks the permission.

#### Scenario: Button with feature permission
- **WHEN** a `<bk-button v-permission="'feature:system:user-manage'">新增用户</bk-button>` is rendered and user has the permission
- **THEN** the button is visible

#### Scenario: Button without permission
- **WHEN** the same button is rendered and user does NOT have `"feature:system:user-manage"`
- **THEN** the button is hidden (v-if behavior, not just disabled)

#### Scenario: Superuser sees all buttons
- **WHEN** superuser views the page
- **THEN** all `v-permission` elements are visible regardless of specific permission codes

### Requirement: User management pages route configuration
The system SHALL register the following routes in `src/router/modules/manage.js` with appropriate permission meta:

| Path | Component | Permission |
|------|-----------|------------|
| `/manage/user_management` | `views/manage/userManagement.vue` | `page:system` |
| `/manage/department` | `views/manage/department.vue` | `page:system` |
| `/manage/role` | `views/manage/role.vue` | `page:system` |
| `/manage/user_group` | `views/manage/userGroup.vue` | `page:system` |
| `/manage/security_policy` | `views/manage/securityPolicy.vue` | `page:system` |

All routes SHALL use lazy loading via dynamic imports.

#### Scenario: Navigate to user management
- **WHEN** user with `page:system` permission navigates to `/manage/user_management`
- **THEN** `views/manage/userManagement.vue` component is loaded and rendered

#### Scenario: Navigate without system permission
- **WHEN** user without `page:system` permission navigates to `/manage/user_management`
- **THEN** router redirects to `/limitAccess`

### Requirement: i18n for user management module
The system SHALL add i18n translation keys for all user management frontend text under namespace `m.userManagement`. Supported languages: zh-cn (Chinese), en (English). All user-visible text in the 5 management pages SHALL use `$t('m.userManagement["key"]')` pattern.

#### Scenario: Chinese label
- **WHEN** user language is zh-cn and page renders "新增用户" button
- **THEN** text comes from `$t('m.userManagement["createUser"]')` resolving to "新增用户"

#### Scenario: English label
- **WHEN** user language is en and page renders "新增用户" button
- **THEN** text resolves to "Create User" from the en translation file

#### Scenario: Permission name translations
- **WHEN** permission matrix displays "feature:workflow:manage"
- **THEN** display name uses i18n key, showing "流程管理权限" in zh-cn or "Workflow Management" in en
