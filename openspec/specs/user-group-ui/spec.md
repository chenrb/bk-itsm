## Purpose

Frontend user group (UserGroup) management page for managing workflow handler groups. User groups are the core concept for "custom role" handler types in the process designer. This page replaces the legacy `/project/role.vue` page and uses the new `/api/user-groups/` API.

## Requirements

### Requirement: UserGroup list page
The system SHALL provide a user group list page at `/manage/user_group` displaying a `<bk-table>` with columns: name (角色组名称), group_key (标识), is_builtin (类型: 内置/自定义, shown as tag), member_count (成员数), owners (负责人, comma-separated usernames), actions (操作). The page SHALL support text search by name and filter by is_builtin. Pagination SHALL follow project defaults.

#### Scenario: Load group list
- **WHEN** user navigates to `/manage/user_group`
- **THEN** page loads groups from `GET /api/user-groups/` and displays in table

#### Scenario: Search group by name
- **WHEN** user types "运维" in search input
- **THEN** table filters to show groups whose name contains "运维"

#### Scenario: Filter builtin groups
- **WHEN** user selects "内置" from type filter
- **THEN** only groups with is_builtin=true are shown

### Requirement: Create user group dialog
The system SHALL provide a `<bk-dialog>` for creating new user groups with form fields: name (required), group_key (required, alphanumeric + underscore only), desc (optional), members (member-select, multi-select), owners (member-select, multi-select). The submit button SHALL call `POST /api/user-groups/`. Only users with `feature:system:group-manage` permission SHALL see the create button.

#### Scenario: Open create dialog
- **WHEN** admin clicks "新增角色组"
- **THEN** dialog opens with empty form

#### Scenario: Submit create group
- **WHEN** admin fills name="一线支持", group_key="L1_SUPPORT" and clicks submit
- **THEN** `POST /api/user-groups/` is called, dialog closes, table refreshes

#### Scenario: Duplicate group_key
- **WHEN** admin submits with group_key="DEV" which already exists
- **THEN** error message "角色组标识已存在" is shown

### Requirement: Edit user group dialog
The system SHALL provide a `<bk-dialog>` for editing user groups with form fields: name, desc, members (member-select), owners (member-select). group_key SHALL be read-only. The submit button SHALL call `PATCH /api/user-groups/{id}/`. Users with `feature:system:group-manage` permission OR users listed as owners of the specific group SHALL be able to edit.

#### Scenario: Admin edits any group
- **WHEN** admin clicks "编辑" on any group
- **THEN** dialog opens with current data pre-filled

#### Scenario: Owner edits their group
- **WHEN** user "zhangsan" is an owner of group "运维" and clicks "编辑"
- **THEN** dialog opens, user can modify members and owners

#### Scenario: Non-owner non-admin cannot edit
- **WHEN** user "lisi" is neither admin nor owner of group "运维"
- **THEN** "编辑" button is not visible or disabled for that group

#### Scenario: Builtin group_key is read-only
- **WHEN** admin opens edit for builtin group "DEV"
- **THEN** the group_key field shows "DEV" and is disabled

### Requirement: Delete custom user group
The system SHALL provide a delete action on custom groups (is_builtin=false). Clicking delete SHALL show a confirmation dialog. On confirm, `DELETE /api/user-groups/{id}/` SHALL be called. Builtin groups SHALL NOT show the delete button.

#### Scenario: Delete custom group
- **WHEN** admin clicks "删除" on custom group "一线支持"
- **THEN** confirmation dialog "确定删除角色组 '一线支持'？" appears, on confirm `DELETE /api/user-groups/{id}/` is called

#### Scenario: Cannot delete builtin group
- **WHEN** admin views builtin group "DEV"
- **THEN** "删除" button is not visible

### Requirement: Redirect from legacy role page
The system SHALL redirect `/project/role` route to `/manage/user_group` to maintain backward compatibility with existing bookmarks. A brief notification message "角色组管理已迁移到系统管理" SHALL be shown on redirect.

#### Scenario: Navigate to old role page
- **WHEN** user navigates to `/project/role`
- **THEN** browser redirects to `/manage/user_group` with a notification toast

### Requirement: UserGroup Vuex Store module
The system SHALL provide a Vuex Store module `userGroup` (namespaced) with actions: `list` (GET /api/user-groups/), `create` (POST /api/user-groups/), `update` (PATCH /api/user-groups/{id}/), `delete` (DELETE /api/user-groups/{id}/).

#### Scenario: List groups
- **WHEN** component dispatches `userGroup/list` with `{search: "运维"}`
- **THEN** GET `/api/user-groups/?search=运维` is called

#### Scenario: Update group members
- **WHEN** component dispatches `userGroup/update` with `{id: 3, members: ["zhangsan", "lisi"]}`
- **THEN** PATCH `/api/user-groups/3/` is called with the payload
