## Purpose

Frontend role and permission management page providing RBAC administration interface. Enables administrators to create/edit roles, assign permissions via a matrix UI, and manage role members. Displays the full system permission registry (38 built-in permissions).

## Requirements

### Requirement: Role list page
The system SHALL provide a role list page at `/manage/role` displaying a `<bk-table>` with columns: name (角色名称), role_key (标识), is_builtin (类型: 内置/自定义, shown as tag), member_count (成员数), permission_count (权限数), actions (操作). The page SHALL support text search by name. Pagination SHALL follow project defaults.

#### Scenario: Load role list
- **WHEN** user navigates to `/manage/role`
- **THEN** page loads roles from `GET /api/roles/` and displays in table

#### Scenario: Search role by name
- **WHEN** user types "管理员" in search input
- **THEN** table filters to show roles whose name contains "管理员"

### Requirement: Create role SideSlider
The system SHALL provide a `<bk-sideslider>` for creating new roles with form fields: name (required), role_key (required, alphanumeric + underscore only), desc (optional). The submit button SHALL call `POST /api/roles/`. Only users with `feature:system:role-manage` permission SHALL see the create button.

#### Scenario: Open create slider
- **WHEN** admin clicks "新增角色"
- **THEN** SideSlider opens with empty form

#### Scenario: Submit create role
- **WHEN** admin fills name="运维管理员", role_key="OPS_ADMIN" and clicks submit
- **THEN** `POST /api/roles/` is called, slider closes, table refreshes

#### Scenario: Duplicate role_key
- **WHEN** admin submits with role_key="SUPERUSER" which already exists
- **THEN** error message "角色标识已存在" is shown

### Requirement: Edit role SideSlider with permission matrix
The system SHALL provide a `<bk-sideslider>` for editing roles containing three sections: (1) Basic info (name, desc — role_key read-only), (2) Permission assignment (checkbox matrix grouped by category, each showing permission code and display name), (3) Member management (member-select for members and owners). The permission matrix SHALL load all permissions from `GET /api/permissions/` and pre-check the role's current permissions. The submit button SHALL call `PATCH /api/roles/{id}/`.

#### Scenario: Open edit slider
- **WHEN** admin clicks "编辑" on role row
- **THEN** SideSlider opens with three tabs/sections: basic info, permissions, members

#### Scenario: Permission matrix loads all permissions
- **WHEN** edit slider opens
- **THEN** `GET /api/permissions/` is called to load all available permissions, grouped by category in collapsible panels

#### Scenario: Toggle permission checkbox
- **WHEN** admin checks "feature:ticket:view-all" checkbox
- **THEN** the permission code is added to the selected permissions set

#### Scenario: Save role changes
- **WHEN** admin clicks "保存" after modifying permissions and members
- **THEN** `PATCH /api/roles/{id}/` is called with `{permissions: [...], members: [...], owners: [...]}`

#### Scenario: Builtin role_key is read-only
- **WHEN** admin opens edit for builtin role "SUPERUSER"
- **THEN** the role_key field shows "SUPERUSER" and is disabled

### Requirement: Delete custom role
The system SHALL provide a delete action on custom roles (is_builtin=false). Clicking delete SHALL show a confirmation dialog. On confirm, `DELETE /api/roles/{id}/` SHALL be called. Builtin roles SHALL NOT show the delete button.

#### Scenario: Delete custom role
- **WHEN** admin clicks "删除" on custom role "运维管理员"
- **THEN** confirmation dialog "确定删除角色 '运维管理员'？" appears, on confirm `DELETE /api/roles/{id}/` is called

#### Scenario: Cannot delete builtin role
- **WHEN** admin views builtin role "SUPERUSER"
- **THEN** the "删除" button is not visible in the actions column

#### Scenario: Delete without permission
- **WHEN** non-admin views the page
- **THEN** "删除" button is not visible for any role

### Requirement: Role management Vuex Store module
The system SHALL provide a Vuex Store module `roleManagement` (namespaced) with actions: `list` (GET /api/roles/), `create` (POST /api/roles/), `update` (PATCH /api/roles/{id}/), `delete` (DELETE /api/roles/{id}/), `permissions` (GET /api/permissions/ for loading the full permission registry).

#### Scenario: List roles
- **WHEN** component dispatches `roleManagement/list` with `{search: "管理员"}`
- **THEN** GET `/api/roles/?search=管理员` is called

#### Scenario: Load permissions
- **WHEN** component dispatches `roleManagement/permissions`
- **THEN** GET `/api/permissions/` is called, returns full permission list

### Requirement: Permission display name i18n
All permission display names in the permission matrix SHALL use i18n keys. The frontend SHALL store permission display name translations in the user management i18n module, mapping permission codes to translated names.

#### Scenario: Permission name in Chinese
- **WHEN** user language is zh-cn and permission "page:workflow" is displayed
- **THEN** the display name shows "流程管理" instead of raw code

#### Scenario: Permission name in English
- **WHEN** user language is en and permission "page:workflow" is displayed
- **THEN** the display name shows "Workflow Management"
