## Context

BK-ITSM 已完成蓝鲸平台解耦（P1-P18），但用户管理、组织架构、角色权限能力仍散落在四个位置：

- `itsm/component/users/` — User 模型 + 登录视图（极简）
- `itsm/role/` — RoleType + UserRole + BKUserRole（BKUserRole 依赖蓝鲸 API，RoleType 冗余）
- `itsm/gateway/` — 6 个 usermanage 视图 + 2 个 bk_login 视图（部门相关全部调蓝鲸）
- `itsm/component/utils/` — user_adapter.py（已本地化）+ client_backend_query.py（仍调蓝鲸）

当前系统完全无法处理：组织架构、用户 Leader 关系、部门人员解析。`init/` 接口因调用不存在的 `update_cmdb_common_roles()` 直接 500。IAM 权限桩永远返回 True，等于没有权限系统。

## Goals / Non-Goals

**Goals:**

- 建立完整的本地用户管理模块，包含用户、部门、角色（权限）、角色组（处理人）、权限、安全策略
- 前端 API 保持 URL 兼容（`/gateway/usermanage/*`、`/gateway/bk_login/*`、`/api/role/*`、`/init/`）
- 前端人员选择器 `@blueking/user-selector` 无需修改
- 三层权限粒度（page / button / feature），前后端统一消费
- 安全策略（密码、登录）数据库建模，管理员可运行时修改
- 工作流处理人类型解析全部本地化，去掉 CMDB / IAM 类型
- Django admin 注册所有新模型，提供基础管理界面

**Non-Goals:**

- 不做多租户 / 项目级资源权限（权限粒度为功能级，不区分项目范围）
- 不做 SSO / OAuth / LDAP 等外部认证集成（保持 Session + JWT）
- 不重写前端权限组件（只提供 `permissions` 数组，前端自行集成路由守卫和 `v-permission`）
- 不做用户自助注册（用户由管理员创建或 init_builtin_data 初始化）
- 不做审计日志（可后续独立建设）

## Decisions

### D1: 模块结构 — 新建 `itsm/users/` 替代多个散落模块

**选择**：新建独立 Django app `itsm/users/`，将 User 模型、Department、Role、UserGroup、Permission、SecurityPolicy 全部放入。

**替代方案**：
- 扩展现有 `component/users/` — 这个 app 名为 component，定位是共享工具，不适合放业务模型
- 拆成多个 app（users + org + rbac）— 过度拆分，User 和 Department 紧耦合，Role 和 Permission 也紧耦合

**理由**：单 app 降低跨 app 关系复杂度，`AUTH_USER_MODEL = "users.User"` 保持不变（db_table 变更但 label 不变）。

### D2: 树形实现 — django-mptt

**选择**：继续使用已安装的 django-mptt (`django-mptt==0.18.0`)。

**替代方案**：
- django-treebeard (MP) — 需新增依赖，部门树规模小（3-5 层、几十节点）不需要其写性能优势
- django-fast-treenode — 过新，社区小

**理由**：部门组织架构是典型的读多写少、浅层树，mptt 的 Nested Sets 完全满足。

### D3: Role 与 UserGroup 拆分

**选择**：拆为两个独立模型。

| 维度 | Role (权限角色) | UserGroup (通用角色组) |
|------|----------------|----------------------|
| 目的 | 授予系统权限 | 工作流处理人分组 |
| 核心 | permissions M2M | members M2M |
| 前端 | 权限管理页面 | 流程设计处理人选择 |
| 内置 | 超级管理员、流程管理员、统计查看员 | 开发组、运维组、测试组等 |

**理由**：当前 UserRole 用 `role_type` 字段区分两种职责，语义混淆。ADMIN 类型的 members = "有这个权限的人"，GENERAL 类型的 members = "可以被分配单据的人"，这是两个完全不同的概念。

### D4: 权限编码规范 — `{type}:{module}:{action}`

**选择**：统一的 permission code 命名规范。

- `page:workflow` — 页面级（前端路由守卫）
- `btn:workflow:create` — 按钮级（前端 v-permission 指令）
- `feature:workflow:manage` — 功能级（后端 DRF permission_class）

**理由**：三段式编码让前端和后端都能按前缀过滤，初始化时可按 category 批量分配。Permission 模型的 `category` 字段（workflow/ticket/system/project）和 `permission_type` 字段（page/button/feature）与 code 前缀对应。

### D5: 安全策略建模 — 数据库存储

**选择**：新建 `SecurityPolicy` 模型存储策略配置，替代 settings 配置。

**字段设计**：
- `key` — 策略标识（如 `password_min_length`、`login_max_attempts`）
- `value` — JSONField 存储策略值
- `category` — 分类（password / login / session）
- `description` — 策略描述

**替代方案**：settings.py 配置 — 用户要求可运行时修改，必须存数据库。

### D6: 前端 API 兼容策略

**选择**：在 `itsm/users/urls.py` 中注册与原路径相同的 URL pattern。

- `/gateway/usermanage/*` → 保持 URL，视图从本地 Department 表查数据
- `/gateway/bk_login/*` → 保持 URL，视图从本地 User 表查数据
- `/init/` → 保持 URL，去掉蓝鲸同步调用，新增 `permissions` 字段
- `/api/role/*` → 保持 URL，Role 和 UserGroup 各自注册 ViewSet
- `/api/c/compapi/v2/usermanage/fs_list_users/` → 保持 URL（人员选择器 JSONP 兼容）

**理由**：前端 30+ 处调用这些接口，改 URL 成本远高于后端兼容。

### D7: BKUserRole / RoleType 删除

**选择**：直接删除，不保留兼容层。

- `BKUserRole` — 缓存蓝鲸角色的烂代码，本地 Department 模型完全替代
- `RoleType` — 拆分后 Role 和 UserGroup 各自独立，不需要类型分类表

**影响**：所有引用 BKUserRole 的代码（`sites/views.py`、`ticket/managers.py`、`task/models.py`、`role/models.py`）需同步改写。

## Functional Architecture

### Cross-Module Workflows

#### 1. User Login → Init → Permission Load

```
浏览器                          后端
────────                       ────────
GET /init/
                               → SessionMiddleware 检查 session
                               → 未登录 → 401
                               → 已登录 → 查询 User, Role, Permission
                               → Role.is_itsm_superuser() → IS_ITSM_ADMIN
                               → Role.get_access_by_user() → all_access
                               → User.has_permission() × all codes → permissions[]
                               → 返回 {chname, username, IS_ITSM_ADMIN, all_access, permissions}
← {data}
前端存储 window.*, Vuex
```

#### 2. Ticket Processor Resolution

```
工单流转到节点 N
  → 节点 N: processors_type="GENERAL", processors="3,5"
  → resolve_processors("GENERAL", "3,5", ticket)
    → UserGroup(id=3).members → ["zhangsan", "lisi"]
    → UserGroup(id=5).members → ["wangwu", "zhangsan"]
    → 去重 → ["zhangsan", "lisi", "wangwu"]
  → 创建 Task 分配给上述用户
```

#### 3. Password Change with Security

```
POST /api/users/me/change_password/ {old, new}
  → authenticate(username, old_password) → 验证旧密码
  → SecurityPolicyPasswordValidator.validate(new_password)
    → 读取 SecurityPolicy 密码策略
    → 检查长度、字符类型
  → PasswordHistory 检查最近 N 次密码
  → 全部通过 → 保存旧密码 hash → 更新密码
```

#### 4. Department Tree → User Selector

```
前端 SelectTree 组件
  → GET /gateway/usermanage/get_first_level_departments/
    → Department.objects.filter(level=0)
    → 返回 [{id, name, has_children}]
  → 用户展开节点 3
  → GET /gateway/usermanage/get_department_info/?id=3
    → Department(id=3).children
    → 返回 {id, name, children: [...], has_children}
```

### Data Model Relationships

```
User ─────────────────────────────────────────────────────────
  │ leader (self-FK, nullable)                    ↑
  │ department (FK → Department, nullable)        │
  │                                                │
  ├── M2M ── Role.members (被授权的人)              │
  │         Role.owners (可编辑角色的人)            │
  │         Role → permissions M2M → Permission    │
  │                                                │
  ├── M2M ── UserGroup.members (工单处理人)         │
  │         UserGroup.owners (可编辑组的人)         │
  │                                                │
  ├── M2M ── DeptMembership → Department           │
  │                                                │
  ├── FK ─── PasswordHistory                       │
  │                                                │
  └── (via username) ── LoginAttempt               │
                           │
Department (MPTTModel)     │
  ├── parent (self-FK)     │
  └── DeptMembership ──────┘
```

### Permission Check Priority

```
User.has_permission(code)
  1. user.is_superuser == True → True (短路返回)
  2. 遍历 user.auth_roles.all()
     → role.has_permission(code)
       → role.permissions.filter(code=code).exists()
  3. 任一 Role 匹配 → True
  4. 无匹配 → False
```

### Module Dependency Order

实施顺序遵循依赖关系：

```
1. Permission ─── 无依赖，纯数据定义
2. Department ─── 无依赖（User.department 后加）
3. User ──────── 依赖 Department（FK）
4. Role ──────── 依赖 User + Permission（M2M）
5. UserGroup ─── 依赖 User（M2M）
6. SecurityPolicy ─── 依赖 User（LoginAttempt, PasswordHistory）
7. Auth ──────── 依赖 User + Role + Department
8. Processor Resolution ──── 依赖 UserGroup + Department + User
9. Cleanup ───── 依赖以上全部完成
```

## Risks / Trade-offs

- **[数据库重建]** 所有新模型 + User 字段变更需要 drop 并重建数据库 → 迁移策略：项目已声明需 drop 重建（P3 阶段重置过），继续沿用
- **[前端权限集成]** `permissions` 数组返回后，前端需要逐步接入路由守卫和按钮指令 → 分步实施，先通过 `IS_ITSM_ADMIN` / `all_access` 兼容旧逻辑，新权限体系并行运行
- **[工作流兼容]** 工单表中 `processors_type="GENERAL"` + `processors="3,5"` 的数据引用 UserRole.id → UserGroup.id 可能不同 → init_builtin_data 必须按固定顺序创建 UserGroup，或提供数据迁移脚本
- **[gateway/ 删除时机]** 删除 gateway app 影响面大（urls.py、v1.py 都引用） → 先在 users/ 中注册所有兼容 URL，验证通过后再删除 gateway/
- **[规模]** 模块较大，约 8 个新模型 → 按 capability 分批实施，每批可独立验证
