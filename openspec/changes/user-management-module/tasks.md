## 1. 模块骨架与 User 模型

- [x] 1.1 创建 `itsm/users/` app 骨架（`__init__.py`、`apps.py`、`urls.py`、`admin.py`）
- [x] 1.2 将 `AUTH_USER_MODEL` 改为 `users.User`，`INSTALLED_APPS` 中用 `itsm.users` 替换 `itsm.component.users`
- [x] 1.3 将 User、UserManager、UserProperty 模型从 `itsm/component/users/models.py` 迁入 `itsm/users/models/user.py`，新增 `leader`（self-FK）、`department`（FK to Department，nullable）字段，添加 `display_name` 属性（nickname > chname > username）；所有字段 `verbose_name` 和 `help_text` 使用 `gettext_lazy`
- [x] 1.4 为 User 模型添加 `get_property(key)` 方法（chname 直接返回字段，其他查 UserProperty）
- [x] 1.5 生成并应用 `0001_initial` 迁移（users app）
- [x] 1.6 注册 User 和 UserProperty 到 Django admin
- [x] 1.7 实现 User ViewSet（CRUD），包含 `change_password` 和 `reset_password` 自定义 action；停用用户（`is_active=False`）在处理人解析中应被过滤

## 2. Department 模型与 API

- [x] 2.1 创建 `itsm/users/models/department.py`，定义 Department（MPTTModel）和 DeptMembership 模型；所有字段 `verbose_name`、`help_text` 使用 `gettext_lazy`
- [x] 2.2 实现 `Department.full_name`（计算属性，祖先路径拼接）和 `has_children` 属性
- [x] 2.3 创建 Department 和 DeptMembership 的 DRF Serializer；错误消息使用 `gettext`
- [x] 2.4 创建 Department ViewSet（CRUD + 软删除）；响应错误消息使用 `gettext`
- [x] 2.5 实现 `/gateway/usermanage/get_first_level_departments/` 视图（根部门列表）
- [x] 2.6 实现 `/gateway/usermanage/get_department_info/` 视图（部门详情 + 子部门懒加载）
- [x] 2.7 实现 `/gateway/usermanage/get_departments/` 视图（全量部门树）
- [x] 2.8 实现 `/gateway/usermanage/get_department_users/` 视图（部门用户列表，支持 recursive）
- [x] 2.9 实现 `/gateway/usermanage/get_department_users_count/` 视图（部门用户计数）
- [x] 2.10 实现 `/gateway/usermanage/get_user_info/` 视图（用户所属部门）
- [x] 2.11 注册 Department 和 DeptMembership 到 Django admin
- [x] 2.12 在 `itsm/users/urls.py` 中注册部门相关 URL（保持 `/gateway/usermanage/*` 路径兼容）

## 3. Permission 模型与初始化

- [x] 3.1 创建 `itsm/users/models/permission.py`，定义 Permission 模型（code, name, category, permission_type, is_builtin）；所有字段 `verbose_name` 使用 `gettext_lazy`
- [x] 3.2 创建 Permission ReadOnlyModelViewSet（list, retrieve）+ 自定义创建（仅限非 builtin）；错误消息使用 `gettext`
- [x] 3.3 创建 Permission Serializer；`name` 字段内置数据使用 `gettext` 支持多语言名称
- [x] 3.4 在 `itsm/users/data/permissions.py` 中声明式定义内置权限（page/button/feature 三层，按 category 分组）
- [x] 3.5 在 `init_builtin_data` management command 中添加 `--app permission` 模块
- [x] 3.6 注册 Permission 到 Django admin

## 4. Role（权限角色）模型与 API

- [x] 4.1 创建 `itsm/users/models/role.py`，定义 Role 模型（name, role_key, members M2M, owners M2M, permissions M2M, is_builtin + 审计字段 + 软删除）；创建 `itsm/users/data/permissions.py` 声明全部内置 Permission（见 spec 中 Permission Code Registry）；所有字段 `verbose_name` 使用 `gettext_lazy`
- [x] 4.2 实现 `Role.has_permission(code)` 方法
- [x] 4.3 实现 `User.has_permission(code)` 方法（聚合所有 Role 的 permissions，superuser 直接返回 True）
- [x] 4.4 实现 Role 的 backward-compat 类方法：`is_itsm_superuser()`、`is_workflow_manager()`、`is_statics_manager()`、`get_access_by_user()`
- [x] 4.5 创建 Role Serializer（members/owners 为 username 列表，permissions 为 code 列表）
- [x] 4.6 创建 Role ViewSet（CRUD，权限控制 `feature:system:role-manage`）
- [x] 4.7 创建 `GET /api/role/types/` 兼容视图（返回处理人类型列表，不含 CMDB/IAM）
- [x] 4.8 创建 `GET /api/role/users/` 兼容视图（GENERAL→UserGroup，ADMIN→Role）
- [x] 4.9 创建 `GET /api/role/users/extra/get_access_by_user/` 兼容视图
- [x] 4.10 创建 `GET /api/role/users/extra/get_global_choices/` 兼容视图
- [x] 4.11 在 `init_builtin_data` 中添加 `--app role` 模块（超级管理员、流程管理员、统计查看员 + 对应 permissions）；按 spec 中 Built-in Role → Permission Matrix 分配权限；内置 Role 的 `name` 使用 `gettext` 支持多语言
- [x] 4.12 注册 Role 到 Django admin（含 permissions inline）
- [x] 4.13 在 `itsm/users/urls.py` 中注册 Role 和 Permission 相关 URL（保持 `/api/role/*` 路径兼容）

## 5. UserGroup（通用角色组）模型与 API

- [x] 5.1 创建 `itsm/users/models/user_group.py`，定义 UserGroup 模型（name, group_key, members M2M, owners M2M, is_builtin, project_key + 审计字段 + 软删除）；所有字段 `verbose_name` 使用 `gettext_lazy`
- [x] 5.2 创建 UserGroup Serializer（members/owners 为 username 列表）
- [x] 5.3 创建 UserGroup ViewSet（CRUD，owners 或 `feature:system:group-manage` 权限可编辑）
- [x] 5.4 在 `init_builtin_data` 中添加 `--app user_group` 模块（DEV、PM、OPT、OPS、TEST、变更经理、故障派单员、服务台小组）；内置 UserGroup 的 `name` 使用 `gettext` 支持多语言
- [x] 5.5 注册 UserGroup 到 Django admin（含 members/owners inline）
- [x] 5.6 在 `itsm/users/urls.py` 中注册 UserGroup 相关 URL

## 6. SecurityPolicy 模型与安全功能

- [x] 6.1 创建 `itsm/users/models/security.py`，定义 SecurityPolicy（key, value JSONField, category, description, is_builtin）、LoginAttempt（username, ip_address, attempts, locked_until）、PasswordHistory（user FK, password_hash, created_at）模型；所有字段 `verbose_name` 使用 `gettext_lazy`
- [x] 6.2 实现 `SecurityPolicy.get_value(key, default)` 类方法
- [x] 6.3 实现 Django PasswordValidator 类，从 SecurityPolicy 读取策略并验证密码；验证错误消息使用 `gettext` 并支持参数插值（如 `%(min_length)s`）
- [x] 6.4 改写登录视图，集成 LoginAttempt 锁定逻辑；错误消息（"用户名或密码错误"、"账户已锁定"等）使用 `gettext`
- [x] 6.5 实现密码修改时 PasswordHistory 检查逻辑
- [x] 6.6 创建 SecurityPolicy Serializer 和 ViewSet（list, retrieve, update, unlock action；仅 `feature:system:security-manage` 可修改）；unlock action 接受 `{username}` 清除 LoginAttempt 记录
- [x] 6.7 在 `init_builtin_data` 中添加 `--app security_policy` 模块（password/login/session 三类默认策略初始化，含 password_max_age_days 和 session_timeout_minutes）
- [x] 6.8 注册 SecurityPolicy、LoginAttempt、PasswordHistory 到 Django admin
- [x] 6.9 在 settings 中注册自定义 PasswordValidator

## 7. 认证与 init 接口改写

- [x] 7.1 将 LoginView 和 logout_view 从 `itsm/component/users/views.py` 迁入 `itsm/users/views/auth.py`
- [x] 7.2 将 CustomUserBackend（JWT）从 `itsm/openapi/authentication/backend.py` 迁入 `itsm/users/backends.py`
- [x] 7.3 更新 `AUTHENTICATION_BACKENDS` 指向新位置
- [x] 7.4 改写 `itsm/sites/views.py` 的 `init()` 视图：去掉 `update_cmdb_common_roles()` 和 `BKUserRole.get_or_update_user_roles()` 调用，`chname` 用 `user.chname`，新增 `permissions` 字段
- [x] 7.5 实现 `/gateway/bk_login/get_batch_users/` 视图（查本地 User 表 + DeptMembership，兼容 JSONP）
- [x] 7.6 实现 `/gateway/bk_login/get_all_users/` 视图（全量用户，30 分钟缓存）
- [x] 7.7 实现 `/api/c/compapi/v2/usermanage/fs_list_users/` 视图（人员选择器 JSONP 兼容）
- [x] 7.8 在 `itsm/users/urls.py` 中注册认证相关 URL（保持 `/account/*`、`/gateway/bk_login/*`、`/api/c/compapi/*` 路径）

## 8. 处理人解析改写

- [x] 8.1 创建 `itsm/users/resolvers.py`，实现 `resolve_processors(user_type, users_param, ticket=None)` 函数；PERSON/GENERAL/STARTER/ORGANIZATION/STARTER_LEADER/ASSIGN_LEADER 在此函数解析，BY_ASSIGNOR/OPEN/API/VARIABLE/EMPTY 返回空列表
- [x] 8.2 实现 GENERAL 类型 → UserGroup.members 解析（过滤 is_active=False 的用户）
- [x] 8.3 实现 ORGANIZATION 类型 → Department 递归用户解析（递归查询子部门，过滤 is_active=False 的用户）
- [x] 8.4 实现 STARTER_LEADER / ASSIGN_LEADER → User.leader 解析
- [x] 8.5 实现 PERSON / STARTER 类型解析；EMPTY / VARIABLE / BY_ASSIGNOR / OPEN / API 返回空列表（由调用方处理）
- [x] 8.6 全局替换 `UserRole.get_users_by_type()` 调用点（20+ 处）为 `resolve_processors()`

## 9. 清理与迁移

- [x] 9.1 删除 `itsm/role/` app（models, views, serializers, urls, migrations）及 `INSTALLED_APPS` 中的注册
- [x] 9.2 删除 `itsm/gateway/` app（views, urls）及 `INSTALLED_APPS` 和 `itsm/api/v1.py` 中的注册
- [x] 9.3 删除 `itsm/component/users/` app（models, views, urls）及 `INSTALLED_APPS` 中的注册
- [x] 9.4 删除 `itsm/component/utils/user_adapter.py`，更新 `config/business.py` 中 `ADAPTER_API` 指向新模块
- [x] 9.5 改写 `itsm/component/utils/client_backend_query.py`：删除所有 `client_backend.usermanage.*` 和 `client_backend.cc.*` 调用，部门相关函数改为查本地 Department 表，保留 `get_user_leader()` 改为查 `User.leader`
- [x] 9.6 更新 `itsm/component/tasks.py`：`update_user_departments()` 改为查本地 DeptMembership，`update_user_cache()` 改为查本地 User
- [x] 9.7 更新 `itsm/ticket/managers.py`、`itsm/task/models.py` 中的 `BKUserRole.get_or_update_user_roles()` 调用为本地查询
- [x] 9.8 删除 `BKUserRole` 模型相关的所有 import 和引用
- [x] 9.9 更新 `urls.py` 根路由：将 `itsm/users/urls.py` 注册到合适位置，确保所有兼容路径生效
- [x] 9.10 更新 `init_builtin_data` 的 superuser 模块，适配新 User 模型
- [x] 9.11 改写 `itsm/component/drf/permissions.py`：`IsAdmin`/`IsManager` 改为调用新 `Role.is_itsm_superuser()` / `Role.is_workflow_manager()`；`IamAuthPermit` 及子类改为基于 `User.has_permission()` 检查，移除 `iam_stub` 依赖

## 10. 验证

- [x] 10.1 `python manage.py check` 通过
- [x] 10.2 `python manage.py migrate` 无错误
- [x] 10.3 `python manage.py init_builtin_data` 全部模块无错误
- [x] 10.4 `python manage.py runserver` 启动无报错
- [x] 10.5 `GET /init/` 返回正确的用户信息 + permissions 列表
- [x] 10.6 部门树 API（`get_first_level_departments`、`get_department_info`）返回正确数据
- [x] 10.7 人员选择器 API（`fs_list_users`、`get_batch_users`）返回正确数据
- [x] 10.8 `resolve_processors()` 各类型解析正确（单元测试）
- [x] 10.9 权限检查 `User.has_permission()` 正确（单元测试）
- [x] 10.10 安全策略（密码验证、登录锁定）正确（单元测试）
- [x] 10.11 前端 `npm run dev` 启动，init 接口正常加载，页面可访问
- [x] 10.12 确认所有新增模型的 `verbose_name` 在 zh-cn、en、ja 三种语言下正确显示（Django admin 切换语言）
