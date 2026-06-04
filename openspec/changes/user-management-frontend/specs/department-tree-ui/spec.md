## Functional Overview

### Module Purpose

部门管理页面提供组织架构树的可视化管理。使用 BKUI-Vue `<bk-big-tree>` 组件展示部门层级结构，支持懒加载、创建/编辑/删除部门、管理部门成员。

### Business Capabilities

1. **部门树展示**：懒加载展示部门层级结构，根节点 → 一级部门 → 子部门
2. **创建部门**：在指定父部门下创建子部门，设置名称和排序
3. **编辑部门**：修改部门名称、排序
4. **删除部门**：删除无成员且无子部门的叶子节点部门（有子部门时提示不可删除）
5. **部门成员查看**：点击部门节点查看该部门下的用户列表

### Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│ 部门管理                                                    │
├──────────────────────┬──────────────────────────────────────┤
│                      │ 技术部 (12人)                         │
│ ▼ 总公司             │──────────────────────────────────────│
│   ├─ 技术部  [+]     │ [添加成员]  [移除成员]                │
│   │  ├─ 前端组       │──────────────────────────────────────│
│   │  └─ 后端组       │ 姓名    | 用户名   | 是否主部门      │
│   ├─ 运维部  [+]     │ 张三    | zhangsan | 是              │
│   └─ 产品部  [+]     │ 王五    | wangwu   | 否              │
│                      │                                      │
│ [+ 新建根部门]       │                                      │
├──────────────────────┴──────────────────────────────────────┤
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

- **API**: `GET /api/departments/`（树）、`POST /api/departments/`（创建）、`PATCH /api/departments/{id}/`（更新）、`DELETE /api/departments/{id}/`（删除）、`GET /api/departments/{id}/members/`（成员列表）
- **Store**: `store/modules/department.js`
- **权限**: `feature:system:department-manage` 控制创建/编辑/删除操作
- **兼容 API**: `GET /gateway/usermanage/get_first_level_departments/`、`GET /gateway/usermanage/get_department_info/` 用于其他页面的部门选择器

### Key Behaviors

- 左侧面板固定宽度 300px，右侧自适应
- 部门树默认展开第一级
- 点击部门节点，右侧加载该部门成员列表
- 删除部门前检查是否有子部门或成员，有则提示不可删除
- 新建根部门按钮在树底部

## ADDED Requirements

### Requirement: Department tree visualization with lazy loading
The system SHALL provide a department tree page at `/manage/department` with a two-panel layout: left panel showing department tree using `<bk-big-tree>` with lazy loading, right panel showing selected department details and members. The tree SHALL load root departments on page mount, and load child departments when a node is expanded.

#### Scenario: Load department tree
- **WHEN** user navigates to `/manage/department`
- **THEN** left panel loads root departments via `GET /api/departments/?parent=null` and renders tree nodes

#### Scenario: Expand department node
- **WHEN** user clicks expand arrow on "技术部" node
- **THEN** child departments are loaded via `GET /api/departments/?parent={id}` and displayed

#### Scenario: Select department node
- **WHEN** user clicks "技术部" node in tree
- **THEN** right panel shows department name, member count, and member list

### Requirement: Create department dialog
The system SHALL provide a `<bk-dialog>` for creating departments with fields: name (required), parent (tree selector, defaults to selected node if any), order (number, defaults to 0). The submit button SHALL call `POST /api/departments/`. Only users with `feature:system:department-manage` permission SHALL see the create button.

#### Scenario: Create child department
- **WHEN** admin selects "技术部" node and clicks [+] icon
- **THEN** create dialog opens with parent pre-filled as "技术部"

#### Scenario: Create root department
- **WHEN** admin clicks "新建根部门" button
- **THEN** create dialog opens with parent field empty

#### Scenario: Submit create department
- **WHEN** admin fills name="测试组" and clicks submit
- **THEN** `POST /api/departments/` is called, tree refreshes, new node appears

#### Scenario: Create without permission
- **WHEN** non-admin views the page
- **THEN** create buttons (+ icon, "新建根部门") are hidden

### Requirement: Edit department dialog
The system SHALL provide a `<bk-dialog>` for editing department name and order. The submit button SHALL call `PATCH /api/departments/{id}/`. A context menu (right-click or three-dot icon) on each tree node SHALL offer "编辑" and "删除" options.

#### Scenario: Open edit dialog
- **WHEN** admin right-clicks "前端组" and selects "编辑"
- **THEN** dialog opens with name="前端组" pre-filled

#### Scenario: Submit edit
- **WHEN** admin changes name to "前端开发组" and submits
- **THEN** `PATCH /api/departments/{id}/` is called, tree node updates

### Requirement: Delete department with validation
The system SHALL provide delete functionality that calls `DELETE /api/departments/{id}/`. Before deletion, the frontend SHALL check if the department has children or members. If it does, a warning message SHALL be shown and deletion SHALL be prevented. Only users with `feature:system:department-manage` permission SHALL see the delete option.

#### Scenario: Delete leaf department
- **WHEN** admin selects "删除" on "前端组" which has no children and no members
- **THEN** confirmation dialog appears, on confirm `DELETE /api/departments/{id}/` is called, node removed from tree

#### Scenario: Delete department with children
- **WHEN** admin selects "删除" on "技术部" which has child "前端组"
- **THEN** warning message "该部门下有子部门，无法删除" is shown, no API call

#### Scenario: Delete department with members
- **WHEN** admin selects "删除" on "运维部" which has 5 members
- **THEN** warning message "该部门下有成员，无法删除" is shown, no API call

### Requirement: Department member list panel
The system SHALL display a member list in the right panel when a department node is selected. The list SHALL show columns: chname (姓名), username (用户名), is_primary (是否主部门, shown as tag). The member list SHALL support pagination.

#### Scenario: View department members
- **WHEN** user clicks "技术部" node
- **THEN** right panel loads `GET /api/departments/{id}/members/` and displays member table

#### Scenario: Empty department
- **WHEN** user clicks a department with no members
- **THEN** right panel shows empty state with message "该部门暂无成员"

### Requirement: Department Vuex Store module
The system SHALL provide a Vuex Store module `department` (namespaced) with actions: `tree` (GET /api/departments/?parent=id for lazy load), `create` (POST /api/departments/), `update` (PATCH /api/departments/{id}/), `delete` (DELETE /api/departments/{id}/), `members` (GET /api/departments/{id}/members/).

#### Scenario: Load tree root
- **WHEN** component dispatches `department/tree` with no parent
- **THEN** GET `/api/departments/?parent=null` is called

#### Scenario: Create department
- **WHEN** component dispatches `department/create` with `{name: "测试组", parent: 5}`
- **THEN** POST `/api/departments/` is called with the payload
