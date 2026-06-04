## Functional Overview

### Module Purpose

角色与权限管理页面提供 RBAC 权限体系的前端管理界面。管理员可创建/编辑角色、为角色分配权限、管理角色成员。页面同时展示系统的完整权限注册表（38 个内置权限），帮助管理员理解权限体系。

### Business Capabilities

1. **角色列表**：展示所有角色（内置 + 自定义），显示名称、成员数、权限数
2. **创建角色**：设置名称、role_key、描述
3. **编辑角色**：修改名称、描述，分配权限（权限矩阵勾选），管理成员和负责人
4. **权限总览**：查看系统全部权限（按 category 分组，按 type 分层）
5. **内置角色保护**：内置角色不可删除，但可修改成员和权限

### Page Layout

```
┌───────────────────────────────────────────────────────────────┐
│ 角色管理                                                      │
├───────────────────────────────────────────────────────────────┤
│ [+ 新增角色]                     搜索: [________]             │
├───────────────────────────────────────────────────────────────┤
│ 名称         | 标识        | 类型   | 成员数 | 权限数 | 操作   │
│ 超级管理员   | SUPERUSER   | 内置   | 3      | 38     | 编辑   │
│ 流程管理员   | WORKFLOW_.. | 内置   | 5      | 12     | 编辑   │
│ 运维管理员   | OPS_ADMIN   | 自定义 | 2      | 8      | 编辑 删│
├───────────────────────────────────────────────────────────────┤
│                                               < 1 2 3 ... >  │
└───────────────────────────────────────────────────────────────┘

--- 编辑角色 SideSlider ---

┌─────────────────────────────────────────────────┐
│ 编辑角色 - 超级管理员                            │
├─────────────────────────────────────────────────┤
│ 基本信息                                         │
│ 名称: [超级管理员    ]  标识: [SUPERUSER] (只读)  │
│ 描述: [_________________________]                │
├─────────────────────────────────────────────────┤
│ 权限分配                                         │
│ ┌─ 流程管理 (workflow) ─────────────────────┐   │
│ │ ☑ page:workflow (页面可见)                 │   │
│ │ ☑ btn:workflow:create (创建流程)           │   │
│ │ ☑ btn:workflow:edit (编辑流程)             │   │
│ │ ☑ feature:workflow:manage (管理权限)       │   │
│ └───────────────────────────────────────────┘   │
│ ┌─ 系统管理 (system) ──────────────────────┐     │
│ │ ☑ page:system (页面可见)                   │    │
│ │ ☐ feature:system:user-manage (用户管理)    │    │
│ └───────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│ 成员管理                                         │
│ [member-select: 张三, 李四, ...]                 │
│ 负责人                                           │
│ [member-select: 管理员]                          │
├─────────────────────────────────────────────────┤
│                              [取消] [保存]       │
└─────────────────────────────────────────────────┘
```

### Integration Points

- **API**: `GET /api/roles/`、`POST /api/roles/`、`PATCH /api/roles/{id}/`、`DELETE /api/roles/{id}/`、`GET /api/permissions/`
- **Store**: `store/modules/roleManagement.js`
- **权限**: `feature:system:role-manage` 控制创建/编辑/删除操作
- **组件复用**: `member-select` 用于成员和负责人选择

### Key Behaviors

- 内置角色（`is_builtin=true`）行显示"内置"标签，无删除按钮
- 权限矩阵按 category 分组（workflow、ticket、system、project、sla、task），每组内按 page → button → feature 排序
- 创建角色时 role_key 为必填，创建后不可修改
- 成员列表使用 `member-select` 组件，支持多选

## ADDED Requirements

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
