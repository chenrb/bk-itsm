## Why

BK-ITSM 完成蓝鲸平台解耦后，用户管理、组织架构、角色权限等核心能力散落在 `component/users/`、`role/`、`gateway/`、`component/utils/` 四处，且大量依赖已不存在的蓝鲸外部 API。`init/` 接口直接 500，部门树和组织架构角色解析完全不可用，IAM 权限体系全部桩化（永远返回 True），安全策略为零。需要构建一套完整的本地用户管理模块来替代。

## What Changes

- **新建统一用户管理模块 `itsm/users/`**，替代现有 `component/users/`、`role/`、`gateway/` 中用户/角色/部门相关代码
- **新增 `Department` 树形模型**（django-mptt），建立本地组织架构体系
- **新增 `DeptMembership` 中间表**，支持用户多部门归属
- **扩展 `User` 模型**，新增 `leader`（自引用 FK）和 `department`（主部门 FK）字段
- **拆分 `UserRole` 为 `Role`（权限授权角色）和 `UserGroup`（通用角色组/处理人组）两个独立模型**，消除语义混淆
- **新增 `Permission` 模型**，建立 page/button/feature 三层权限粒度体系，替代桩化的 IAM
- **新增 `SecurityPolicy` 模型**，密码策略、登录策略等存储在数据库中可随时修改
- **新增 `LoginAttempt` 模型**，支持登录失败锁定
- **新增 `PasswordHistory` 模型**，防止密码重复使用
- **改写 `init/` 接口**，返回本地用户信息 + 权限列表，去掉蓝鲸同步调用
- **改写部门相关 gateway 视图**，从本地 Department 表返回数据，保持前端 API 兼容
- **改写 `UserRole.get_users_by_type()`**，从本地表解析处理人，去掉 CMDB/IAM 类型
- **删除 `BKUserRole` 模型**及其所有引用
- **删除 `RoleType` 模型**，Role 和 UserGroup 各自独立，不需要类型表
- **删除 `client_backend_query.py` 中所有蓝鲸 API 调用**，替换为本地查询
- **删除 `component/utils/user_adapter.py`**，功能迁入新模块
- **删除 `gateway/` app**，视图迁入新模块
- **保持前端人员选择器 `@blueking/user-selector` API 兼容**
- **BREAKING**：`AUTH_USER_MODEL` 从 `users.User` 变更为 `users.User`（同一个 app label，需迁移）；数据库需 drop 重建

## Capabilities

### New Capabilities

- `user-model`: User 模型扩展（leader、主部门字段）及 User CRUD API
- `department`: Department 树形组织架构模型、CRUD API、部门树懒加载接口
- `role`: Role 权限授权角色模型、Permission 模型、权限分配与管理 API
- `user-group`: UserGroup 通用角色组模型、成员管理、工作流处理人解析
- `auth`: 认证体系（Session + JWT）、登录/登出、`init/` 接口改写
- `security-policy`: SecurityPolicy/LoginAttempt/PasswordHistory 模型、密码策略验证、登录安全

### Modified Capabilities

（无既有 spec 需要修改）

## Impact

- **Django apps**：新增 `itsm/users/`，删除 `itsm/role/`、`itsm/gateway/`，重构 `itsm/component/users/`（最终删除）
- **数据库**：新增 Department、DeptMembership、Permission、SecurityPolicy、LoginAttempt、PasswordHistory 表；User 表新增字段；Role/UserGroup 替代原 RoleType+UserRole+BKUserRole；需 drop 重建
- **API**：`/init/` 返回结构新增 `permissions` 字段；部门相关 `/gateway/usermanage/*` 和 `/gateway/bk_login/*` 路由保持 URL 兼容；`/api/role/*` 路由保持兼容
- **前端**：人员选择器 API 兼容不变；`init/` 返回的 `permissions` 数组供路由守卫和按钮权限使用
- **依赖**：`django-mptt` 已安装；无新增 pip 依赖
- **迁移**：`manage.py init_builtin_data` 需扩展以初始化 Permission、Role、UserGroup、Department 数据
- **配置**：`AUTH_USER_MODEL`、`INSTALLED_APPS`、`AUTHENTICATION_BACKENDS`、`MIDDLEWARE` 需调整
