## Functional Overview

### Module Purpose

用户列表页面是用户管理模块的主入口，提供用户的搜索、创建、编辑、启用/停用、密码管理功能。页面位于 `/manage/user_management`，使用 BKUI-Vue 的 `<bk-table>` + `<bk-sideslider>` 组件实现。

### Business Capabilities

1. **用户列表**：分页展示所有用户，支持按 username、chname、department、is_active 过滤和搜索
2. **创建用户**：管理员通过 SideSlider 填写用户信息（用户名、密码、中文名、邮箱、手机、主部门、直属上级）
3. **编辑用户**：管理员修改用户信息（不可修改 username）
4. **密码管理**：用户自助修改密码（需验证旧密码），管理员重置其他用户密码
5. **启用/停用**：管理员切换用户 is_active 状态

### Page Layout

```
┌─────────────────────────────────────────────────────┐
│ 用户管理                                            │
├─────────────────────────────────────────────────────┤
│ [+ 新增用户]     搜索: [________] [部门 ▼] [状态 ▼] │
├─────────────────────────────────────────────────────┤
│ ☐ | 用户名   | 中文名 | 邮箱      | 部门  | 状态 | 操作 │
│──|──────────|───────|──────────|──────|─────|──────│
│  | zhangsan | 张三   | zs@co.com| 技术部| 启用 | 编辑..│
│  | lisi     | 李四   | ls@co.com| 运维部| 停用 | 编辑..│
├─────────────────────────────────────────────────────┤
│                                    < 1 2 3 ... 10 > │
└─────────────────────────────────────────────────────┘
```

### Integration Points

- **API**: `GET /api/users/`（列表）、`POST /api/users/`（创建）、`PUT /api/users/{id}/`（更新）、`POST /api/users/{id}/change_password/`、`POST /api/users/{id}/reset_password/`
- **Store**: `store/modules/userManagement.js`
- **权限**: `feature:system:user-manage` 控制创建/编辑/密码重置操作
- **组件复用**: `member-select` 用于选择直属上级（leader 字段）

### Key Behaviors

- 列表默认按 `date_joined` 倒序排列
- 搜索为 username 和 chname 的模糊匹配
- 创建用户时 username 和 password 为必填
- 停用用户在操作列显示"启用"按钮，启用用户显示"停用"按钮
- 编辑用户 SideSlider 中，username 字段只读不可修改

## ADDED Requirements

### Requirement: User list page with search and filter
The system SHALL provide a user list page at `/manage/user_management` displaying a `<bk-table>` with columns: username, chname (中文名), email, department (主部门名称), is_active (状态标签), date_joined (创建时间), actions (操作). The page SHALL support text search filtering by username and chname, dropdown filter by department, and dropdown filter by is_active status. Pagination SHALL follow project default (10 per page).

#### Scenario: Load user list
- **WHEN** user navigates to `/manage/user_management`
- **THEN** the page loads user list from `GET /api/users/?page=1&page_size=10` and displays in table

#### Scenario: Search by username
- **WHEN** user types "zhang" in search input and presses enter
- **THEN** the table filters to show users whose username or chname contains "zhang"

#### Scenario: Filter by department
- **WHEN** user selects department "技术部" from dropdown
- **THEN** the table shows only users whose primary department is "技术部"

#### Scenario: Filter by active status
- **WHEN** user selects "已停用" from status dropdown
- **THEN** the table shows only users with `is_active=false`

### Requirement: Create user dialog
The system SHALL provide a `<bk-sideslider>` for creating new users with form fields: username (required), password (required), chname (中文名), nickname, email, phone, department (department tree selector), leader (member-select for single user). The submit button SHALL call `POST /api/users/`. Only users with `feature:system:user-manage` permission SHALL see the create button.

#### Scenario: Open create slider
- **WHEN** admin clicks "新增用户" button
- **THEN** a SideSlider opens with empty form fields

#### Scenario: Submit create form
- **WHEN** admin fills username="wangwu", password="TempPass1!", chname="王五" and clicks submit
- **THEN** `POST /api/users/` is called with form data, slider closes, table refreshes

#### Scenario: Submit without required fields
- **WHEN** admin submits form without username
- **THEN** form validation shows error on username field, no API call is made

#### Scenario: Create without permission
- **WHEN** non-admin user views the page
- **THEN** the "新增用户" button is hidden or disabled

### Requirement: Edit user dialog
The system SHALL provide a `<bk-sideslider>` for editing existing users with the same form fields as create, except username SHALL be read-only and password field SHALL be omitted. The submit button SHALL call `PATCH /api/users/{id}/`. Only users with `feature:system:user-manage` permission SHALL see the edit button.

#### Scenario: Open edit slider
- **WHEN** admin clicks "编辑" on a user row
- **THEN** a SideSlider opens with form pre-filled with user's current data

#### Scenario: Username is read-only
- **WHEN** admin opens edit slider for user "zhangsan"
- **THEN** the username field shows "zhangsan" and is disabled/readonly

#### Scenario: Submit edit form
- **WHEN** admin changes chname to "张三丰" and clicks submit
- **THEN** `PATCH /api/users/{id}/` is called with `{chname: "张三丰"}`, slider closes, table refreshes

### Requirement: Change password (self-service)
The system SHALL provide a "修改密码" action button on the current user's row that opens a `<bk-dialog>` with fields: old_password (required), new_password (required), confirm_password (required). The submit button SHALL call `POST /api/users/{id}/change_password/`. The confirm_password field SHALL validate that it matches new_password.

#### Scenario: Self-service password change
- **WHEN** user clicks "修改密码" on their own row and fills {old_password: "old", new_password: "NewPass1!", confirm_password: "NewPass1!"}
- **THEN** `POST /api/users/{id}/change_password/` is called, success message is shown

#### Scenario: Password mismatch
- **WHEN** user fills new_password="abc" and confirm_password="xyz"
- **THEN** form validation shows error "两次输入的密码不一致"

#### Scenario: Wrong old password
- **WHEN** user submits with wrong old_password
- **THEN** error message "旧密码不正确" is displayed in the dialog

### Requirement: Reset password (admin)
The system SHALL provide a "重置密码" action button visible only to users with `feature:system:user-manage` permission. Clicking it opens a `<bk-dialog>` with fields: new_password (required), confirm_password (required). The submit button SHALL call `POST /api/users/{id}/reset_password/`.

#### Scenario: Admin resets password
- **WHEN** admin clicks "重置密码" for user "lisi" and fills {new_password: "NewPass1!", confirm_password: "NewPass1!"}
- **THEN** `POST /api/users/{id}/reset_password/` is called, success message is shown

#### Scenario: Non-admin cannot reset
- **WHEN** non-admin user views another user's row
- **THEN** "重置密码" button is not visible

### Requirement: Toggle user active status
The system SHALL provide a toggle action in the operations column to switch user's is_active status. Activating/deactivating SHALL call `PATCH /api/users/{id}/` with `{is_active: true/false}`. A confirmation dialog SHALL be shown before deactivation. Only users with `feature:system:user-manage` permission SHALL see the toggle.

#### Scenario: Deactivate user
- **WHEN** admin clicks "停用" on an active user
- **THEN** confirmation dialog "确定停用该用户？停用后该用户将无法登录" is shown, on confirm `PATCH /api/users/{id}/` with `{is_active: false}` is called

#### Scenario: Activate user
- **WHEN** admin clicks "启用" on an inactive user
- **THEN** `PATCH /api/users/{id}/` with `{is_active: true}` is called directly

#### Scenario: Toggle without permission
- **WHEN** non-admin views the table
- **THEN** the active toggle button is not visible

### Requirement: User management Vuex Store module
The system SHALL provide a Vuex Store module `userManagement` (namespaced) with actions: `list` (GET /api/users/), `create` (POST /api/users/), `update` (PATCH /api/users/{id}/), `changePassword` (POST /api/users/{id}/change_password/), `resetPassword` (POST /api/users/{id}/reset_password/). All actions SHALL use the project's `ajax` utility and return promises.

#### Scenario: List action dispatch
- **WHEN** component calls `this.$store.dispatch('userManagement/list', {page: 1, page_size: 10, search: 'zhang'})`
- **THEN** a GET request is made to `/api/users/?page=1&page_size=10&search=zhang`

#### Scenario: Create action dispatch
- **WHEN** component calls `this.$store.dispatch('userManagement/create', {username: 'test', password: 'xxx'})`
- **THEN** a POST request is made to `/api/users/` with the payload
