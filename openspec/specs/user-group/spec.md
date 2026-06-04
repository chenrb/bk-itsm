## Purpose

通用角色组（UserGroup）是工作流引擎中"处理人分组"的核心概念。与 Role（权限授权）不同，UserGroup 的唯一目的是将一组用户打包，在流程设计时作为处理人候选。

## Requirements

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
