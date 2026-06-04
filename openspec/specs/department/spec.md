## Purpose

部门管理模块提供建立本地组织架构体系的能力。替代原有通过蓝鲸用户管理 API 查询部门树的方式，所有部门数据存储在本地数据库中。部门用于组织架构可视化、工单处理人解析和人员归属管理。

## Requirements

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
