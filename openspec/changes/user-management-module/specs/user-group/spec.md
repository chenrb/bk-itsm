## Functional Overview

### Module Purpose

通用角色组（UserGroup）是工作流引擎中"处理人分组"的核心概念。与 Role（权限授权）不同，UserGroup 的唯一目的是：**将一组用户打包，在流程设计时作为处理人候选**。

### Business Capabilities

1. **角色组管理**：管理员或组 owner 创建角色组、添加/移除成员
2. **流程设计集成**：流程设计器中，处理人类型选"自定义角色"时，列出所有 UserGroup
3. **工单处理人解析**：工单流转到某节点时，`resolve_processors("GENERAL", "3,5")` 解析为 UserGroup 3 和 5 的全部成员

### Built-in UserGroups

| group_key | 名称 | 业务含义 |
|-----------|------|---------|
| `DEV` | 开发 | 开发人员组，用于指派开发相关工单 |
| `PM` | 产品/开发经理 | 产品经理组，用于指派需求审批工单 |
| `OPT` | 运营 | 运营人员组 |
| `OPS` | 运维 | 运维人员组，用于指派运维相关工单 |
| `TEST` | 测试 | 测试人员组，用于指派测试相关工单 |
| `GENERAL_6` | 变更经理 | 变更审批角色组 |
| `GENERAL_7` | 故障派单员 | 故障工单分派角色组 |
| `GENERAL_8` | 服务台小组 | 服务台一线处理角色组 |

内置角色组通过 `init_builtin_data --app user_group` 初始化，默认 members 为空（由管理员配置）。

### Processor Resolution: Complete Type Reference

`resolve_processors(user_type, users_param, ticket=None)` 是替代 `UserRole.get_users_by_type()` 的核心函数，用于工单流转时确定处理人列表。完整类型定义：

| user_type | users_param 含义 | 解析逻辑 | 返回值 |
|-----------|-----------------|---------|--------|
| `PERSON` | 逗号分隔 username | 直接拆分 | `["zhangsan", "lisi"]` |
| `GENERAL` | 逗号分隔 UserGroup ID | 查询 UserGroup.members | 去重 username 列表 |
| `STARTER` | 空 | `ticket.creator` | `["creator_name"]` |
| `STARTER_LEADER` | username | `User.leader` | `["leader_name"]` |
| `ASSIGN_LEADER` | state_id | 查找该 state 的处理人，再取其 leader | `["leader_name"]` |
| `ORGANIZATION` | 逗号分隔 Department ID | 递归查询部门及子部门的全部用户 | 去重 username 列表 |
| `BY_ASSIGNOR` | 空（运行时由派单人填写） | 不在此函数解析，由工单引擎在派单时动态设置 | `[]`（由调用方处理） |
| `EMPTY` | 空 | 无人处理（占位类型） | `[]` |
| `VARIABLE` | 工单字段变量引用 | 由调用方从工单表单数据中提取实际值后传入 `resolve_processors` | 取决于变量值 |
| `OPEN` | 空 | 不限处理人（任何登录用户） | `[]`（由调用方跳过权限检查） |
| `API` | 第三方系统标识 | 非人工处理，由外部系统回调 | `[]` |

**注意**：`BY_ASSIGNOR`、`OPEN`、`API`、`VARIABLE` 四种类型的实际处理人不在 `resolve_processors` 中解析，而是由工单引擎（ticket 模块）在特定时机通过其他逻辑确定。`resolve_processors` 对这四种类型返回空列表，不抛异常。

**已移除的类型**（不再支持）：
- `CMDB` — 原查蓝鲸 CMDB 角色，本地无对应数据
- `IAM` — 原查蓝鲸权限中心角色，由 Role 替代
- `VARIABLE_LEADER` — 使用频率为零，合并到 `STARTER_LEADER` 逻辑

### Backward Compatibility

前端流程设计器中的处理人类型选择依赖以下 API：

1. `GET /api/role/types/?is_processor=true` — 返回可选的处理人类型列表（不含 CMDB/IAM）
2. `GET /api/role/users/?role_type=GENERAL` — 返回 UserGroup 列表（id, name, count）
3. `GET /api/role/users/?role_type=ADMIN` — 返回 Role 列表（id, name, count）

这些 API 保持原有 URL 和响应格式不变，确保前端流程设计器无需修改。

### Key Behaviors

- UserGroup 的 `owners` 有该组的编辑权限（添加/移除 members），不等同于组成员
- UserGroup 的 `members` 是可作为工单处理人的人员
- 内置 UserGroup（`is_builtin=True`）不可删除，但可修改 members/owners
- `project_key` 用于项目级别的角色组隔离（默认 `"0"` 表示全局）
- 工单数据中 `processors="3,5"` 存储的是 UserGroup ID，需确保 `init_builtin_data` 按固定顺序创建以保持 ID 一致

## ADDED Requirements

### Requirement: UserGroup model for processor grouping
The system SHALL provide a UserGroup model with fields: `name` (CharField), `group_key` (CharField, unique), `desc` (TextField, blank), `members` (M2M to User, related_name="user_groups"), `owners` (M2M to User, related_name="owned_user_groups"), `is_builtin` (BooleanField, default=False), `project_key` (CharField, default="0"), plus standard audit fields (creator, create_at, update_at, updated_by, is_deleted). Soft delete SHALL be supported.

#### Scenario: Create user group
- **WHEN** a UserGroup is created with name="运维一组", group_key="OPS_TEAM_1"
- **THEN** group is created and members/owners can be assigned

#### Scenario: Owner has edit permission
- **WHEN** a user is listed as `owner` of a UserGroup
- **THEN** that user SHALL have permission to edit that UserGroup (add/remove members, rename)

#### Scenario: Non-owner cannot edit
- **WHEN** a user is only a `member` (not `owner`) of a UserGroup
- **THEN** that user SHALL NOT have permission to edit the UserGroup

### Requirement: UserGroup CRUD API
The system SHALL provide a DRF ViewSet for UserGroup with list, retrieve, create, update, partial_update, destroy. Creation and modification SHALL be restricted to: (a) users with `feature:system:group-manage` permission, or (b) owners of the specific UserGroup. The list endpoint SHALL support filtering by `is_builtin`, `project_key`. The serializer SHALL represent `members` and `owners` as lists of usernames.

#### Scenario: Owner edits their group
- **WHEN** a user who is owner of UserGroup "运维一组" sends PATCH to update members
- **THEN** update succeeds with 200

#### Scenario: Non-owner non-admin edits group
- **WHEN** a user who is neither owner nor has `feature:system:group-manage` sends PATCH
- **THEN** response is 403 Forbidden

#### Scenario: List groups by project
- **WHEN** GET `/api/user-groups/?project_key=default`
- **THEN** returns only groups matching that project_key

### Requirement: Processor type resolution
The system SHALL provide a `resolve_processors(user_type, users_param, ticket=None)` function (replacing `UserRole.get_users_by_type`) that resolves a list of usernames based on the processor type. Supported types: PERSON, GENERAL, STARTER, ORGANIZATION, STARTER_LEADER, ASSIGN_LEADER, EMPTY, VARIABLE, BY_ASSIGNOR, API. CMDB and IAM types SHALL NOT be supported.

#### Scenario: GENERAL type resolves from UserGroup
- **WHEN** `resolve_processors("GENERAL", "3,5")` is called
- **THEN** returns usernames from UserGroup id=3 and UserGroup id=5 members, deduplicated

#### Scenario: ORGANIZATION type resolves from Department
- **WHEN** `resolve_processors("ORGANIZATION", "2")` is called
- **THEN** returns usernames of users in Department id=2 (recursive)

#### Scenario: STARTER_LEADER resolves from User.leader
- **WHEN** `resolve_processors("STARTER_LEADER", "zhangsan")` is called and zhangsan.leader is "lisi"
- **THEN** returns `["lisi"]`

#### Scenario: ASSIGN_LEADER resolves from ticket node processor's leader
- **WHEN** `resolve_processors("ASSIGN_LEADER", "5", ticket=ticket)` is called, node 5's processor is "zhangsan", zhangsan.leader is "lisi"
- **THEN** returns `["lisi"]`

#### Scenario: STARTER resolves from ticket creator
- **WHEN** `resolve_processors("STARTER", "", ticket=ticket)` is called, ticket.creator is "zhangsan"
- **THEN** returns `["zhangsan"]`

#### Scenario: PERSON resolves directly
- **WHEN** `resolve_processors("PERSON", "zhangsan,lisi")`
- **THEN** returns `["zhangsan", "lisi"]`

#### Scenario: CMDB type not supported
- **WHEN** `resolve_processors("CMDB", ...)` is called
- **THEN** raises ValueError or returns empty list

### Requirement: UserGroup registered in Django admin
The system SHALL register UserGroup model in Django admin with member and owner inline editing.

#### Scenario: Admin group management
- **WHEN** admin visits `/admin/users/usergroup/`
- **THEN** group list is displayed with inline member editing

### Requirement: Backward compatible role type list API
The system SHALL keep `GET /api/role/types/?is_processor=true` returning the list of processor types. The response SHALL include GENERAL, PERSON, STARTER, STARTER_LEADER, ASSIGN_LEADER, ORGANIZATION, VARIABLE, EMPTY, BY_ASSIGNOR. CMDB and IAM SHALL NOT be included.

#### Scenario: Get processor types
- **WHEN** GET `/api/role/types/?is_processor=true`
- **THEN** returns processor types without CMDB or IAM

### Requirement: Backward compatible role users list API
The system SHALL keep `GET /api/role/users/?role_type=GENERAL` returning UserGroups as the list. Each entry SHALL have `id` (UserGroup.id), `name` (UserGroup.name), `count` (number of members). This SHALL also support `GET /api/role/users/?role_type=ADMIN` returning Roles with the same shape for backward compatibility.

#### Scenario: List GENERAL roles (UserGroups)
- **WHEN** GET `/api/role/users/?role_type=GENERAL&project_key=0`
- **THEN** returns list of UserGroups with `{id, name, count}`

#### Scenario: List ADMIN roles (Roles)
- **WHEN** GET `/api/role/users/?role_type=ADMIN`
- **THEN** returns list of Roles with `{id, name, count, role_key}`
