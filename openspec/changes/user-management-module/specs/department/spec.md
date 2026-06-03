## Functional Overview

### Module Purpose

部门管理模块提供建立本地组织架构体系的能力。替代原有通过蓝鲸用户管理 API 查询部门树的方式，所有部门数据存储在本地数据库中。部门用于：

1. **组织架构可视化**：前端树形选择器展示公司组织结构
2. **工单处理人解析**：`ORGANIZATION` 类型处理人通过部门递归查询关联用户
3. **人员归属管理**：用户可属于多个部门，有一个主部门

### Business Capabilities

1. **部门树管理**：管理员创建、编辑、调整部门层级结构（支持多级嵌套）
2. **部门成员管理**：将用户分配到部门，指定主部门
3. **部门停用**：停用部门不影响已有工单引用，但该部门不再出现在新建流程的处理人选择中
4. **部门查询**：前端懒加载树、全量树、部门成员列表等多种查询方式

### Department in Workflow Context

工单流程设计器中，处理人类型 `ORGANIZATION` 引用部门 ID。运行时解析流程：
```
流程节点 processors_type="ORGANIZATION", processors="3"
  → resolve_processors() 查询 Department(id=3) 及其所有子部门
  → 递归查找 DeptMembership 获取全部用户
  → 返回去重的 username 列表作为处理人候选人
```

### Key Behaviors

- 一个用户可归属多个部门（通过 DeptMembership），但只有一个主部门（`is_primary=True`）
- `User.department` FK 是主部门的冗余字段，查询时避免 JOIN DeptMembership
- 部门停用（`is_active=False`）时：子部门不受影响；该部门不再出现在前端选择器中；已有工单引用该部门 ID 的数据不受影响
- 部门物理删除：仅允许在没有子部门且没有成员时执行；否则只能停用
- `full_name` 由 ancestor path 拼接（如 "总公司/技术部/后端组"），反映树的当前位置
- 部门移动（改变 parent）时，`full_name` 需重新计算

## ADDED Requirements

### Requirement: Department tree model
The system SHALL provide a Department model using `django-mptt`'s `MPTTModel` with `TreeForeignKey` for parent. Fields: `name` (CharField, required), `parent` (TreeForeignKey to self, nullable), `order` (IntegerField, default=0), `is_active` (BooleanField, default=True), plus mptt-managed fields (`level`, `lft`, `rgt`, `tree_id`). The model SHALL provide computed properties: `full_name` (returns ancestor path like "总公司/技术部/后端组"), `has_children` (returns True if any child exists). The model ordering SHALL be by `tree_id`, `lft`.

#### Scenario: Create root department
- **WHEN** a Department is created with name="总公司" and parent=None
- **THEN** `dept.level` is 0, `dept.full_name` is "总公司"

#### Scenario: Create child department
- **WHEN** a Department is created with name="技术部" and parent=总公司
- **THEN** `dept.level` is 1, `dept.full_name` is "总公司/技术部"

#### Scenario: Department has_children
- **WHEN** 技术部 has child departments
- **THEN** `技术部.has_children` is True

#### Scenario: Department without children
- **WHEN** 后端组 has no child departments
- **THEN** `后端组.has_children` is False

### Requirement: DeptMembership M2M through table
The system SHALL provide a DeptMembership model as the through table for User-Department M2M relationship. Fields: `user` (FK to User), `department` (FK to Department), `is_primary` (BooleanField, default=False). Each user SHALL have at most one primary department. The User model's `department` FK field SHALL always point to the primary DeptMembership's department (denormalized for query performance).

#### Scenario: User joins multiple departments
- **WHEN** user is added to DeptMembership with departments [技术部, 项目组] and 技术部 is marked `is_primary=True`
- **THEN** `user.department` is 技术部, user is in both departments

#### Scenario: Primary department constraint
- **WHEN** a user already has a primary DeptMembership
- **THEN** setting another DeptMembership as `is_primary=True` SHALL move the primary flag and update `user.department`

### Requirement: Department CRUD API
The system SHALL provide a DRF ViewSet for Department with list, retrieve, create, update, partial_update, destroy actions. Creation and modification SHALL be restricted to users with `feature:system:department-manage` permission. The list endpoint SHALL support filtering by `is_active`, `parent`. Destroy SHALL soft-delete (set `is_active=False`) rather than hard-delete if child departments or members exist.

#### Scenario: Create department
- **WHEN** POST with `{name: "财务部", parent: 1}`
- **THEN** department is created under parent, returns full tree info

#### Scenario: Delete department with members
- **WHEN** DELETE on a department that has DeptMembership records
- **THEN** department is soft-deleted (is_active=False), not hard-deleted

### Requirement: Department tree lazy-load API
The system SHALL provide API endpoints compatible with the existing frontend SelectTree component: `GET /gateway/usermanage/get_first_level_departments/` returns root departments; `GET /gateway/usermanage/get_department_info/?id=X` returns a department's detail including children. Response format for each department node SHALL include: `id`, `name`, `full_name`, `has_children`, `children` (array of child nodes, empty for lazy loading), `route` (array of `{id, name}` ancestor chain).

#### Scenario: Get first level departments
- **WHEN** GET `/gateway/usermanage/get_first_level_departments/`
- **THEN** returns list of root-level departments with `has_children` correctly set

#### Scenario: Lazy load children
- **WHEN** GET `/gateway/usermanage/get_department_info/?id=3`
- **THEN** returns department 3 detail with `children` populated from direct child departments

#### Scenario: Department route
- **WHEN** department "后端组" (under 总公司→技术部) is retrieved
- **THEN** `route` is `[{id:1, name:"总公司"}, {id:2, name:"技术部"}]`

### Requirement: Department users API
The system SHALL provide `GET /gateway/usermanage/get_department_users/?id=X&recursive=true|false` returning users in a department. When `recursive=true`, SHALL include users from all descendant departments. Response SHALL filter sensitive info (password hash, etc.). `GET /gateway/usermanage/get_department_users_count/?id=X` returns `{count: N}`.

#### Scenario: Get department users non-recursive
- **WHEN** GET with `id=3&recursive=false`
- **THEN** returns only users directly in department 3

#### Scenario: Get department users recursive
- **WHEN** GET with `id=3&recursive=true`
- **THEN** returns users in department 3 and all descendant departments

### Requirement: User department info API
The system SHALL provide `GET /gateway/usermanage/get_user_info/?username=X` returning the user's department memberships. Response SHALL be an array of `{id, name, full_name, is_primary}` objects.

#### Scenario: Get user departments
- **WHEN** GET with `username=zhangsan`
- **THEN** returns list of departments the user belongs to with `is_primary` flag

### Requirement: Full department tree API
The system SHALL provide `GET /gateway/usermanage/get_departments/` returning the full department tree as a nested structure. The response SHALL use `build_tree()` utility to convert flat list to tree with `route` on each node. The endpoint SHALL be cached for 5 minutes.

#### Scenario: Get full tree
- **WHEN** GET `/gateway/usermanage/get_departments/`
- **THEN** returns nested tree structure starting from root departments

### Requirement: Department registered in Django admin
The system SHALL register Department model in Django admin with tree display, supporting add/edit/delete inline.

#### Scenario: Admin department management
- **WHEN** admin visits `/admin/users/department/`
- **THEN** department tree is displayed with inline editing
