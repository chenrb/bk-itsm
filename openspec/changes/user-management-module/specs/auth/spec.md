## Functional Overview

### Module Purpose

认证模块负责用户身份验证和前端初始化数据提供。提供两种认证方式：Session（Web UI）和 JWT（OpenAPI）。`/init/` 接口是前端 SPA 加载时的首个请求，返回当前用户信息和权限列表。

### Authentication Flows

#### Web UI 登录流程
```
用户访问页面 → 前端调用 /init/
  → 未登录 → 前端跳转 /account/login/
    → POST username + password
      → 成功 → session 创建 → 返回 {result: true, data: {redirect_url: "/"}}
      → 失败 → 返回 {result: false, message: "用户名或密码错误"} (401)
        → 超过锁定次数 → 返回 {result: false, message: "账户已锁定，请 X 分钟后重试"}
  → 已登录 → 返回用户信息 + 权限列表
```

#### OpenAPI JWT 认证流程
```
外部系统调用 /openapi/* 接口
  → 携带 Authorization: Bearer <token>
    → 解码 JWT (HS256, SECRET_KEY)
      → payload.sub 或 payload.username 查找/创建本地 User
        → 找到 → 认证通过
        → 未找到 → 自动创建 User（nickname=username，无密码）→ 认证通过
    → token 过期 → 认证失败，请求作为匿名用户处理
```

### Init Endpoint Response

`GET /init/` 返回结构：

```json
{
  "code": 0,
  "result": true,
  "data": {
    "DEFAULT_PROJECT": "0",
    "chname": "张三",
    "username": "zhangsan",
    "all_access": ["SUPERUSER"],
    "IS_ITSM_ADMIN": 1,
    "need_target": false,
    "location": "",
    "permissions": [
      "page:workflow",
      "page:ticket",
      "feature:workflow:manage",
      "btn:workflow:create",
      "..."
    ]
  }
}
```

**与原接口的变化**：
- `chname` 从 `user.get_property("chname")` 改为直接 `user.chname`
- 移除 `UserRole.update_cmdb_common_roles()` 调用（原 500 错误源）
- 移除 `BKUserRole.get_or_update_user_roles()` 调用（蓝鲸 API 依赖）
- 新增 `permissions` 数组（聚合所有 Role 的 Permission code）
- `all_access` 和 `IS_ITSM_ADMIN` 保持不变（前端虽为死代码，但保持兼容）

### Gateway API Compatibility

以下 API 保持原有 URL 不变，改为查本地数据库：

| URL | 功能 | 数据源 |
|-----|------|--------|
| `/gateway/bk_login/get_batch_users/` | 批量用户查询 | User + DeptMembership |
| `/gateway/bk_login/get_all_users/` | 全量用户（30分钟缓存） | User |
| `/api/c/compapi/v2/usermanage/fs_list_users/` | 人员选择器 JSONP | User |
| `/gateway/usermanage/*` | 部门相关 API | Department + DeptMembership |

### Key Behaviors

- 登录失败时触发 LoginAttempt 累加，达到上限后锁定账户
- 登录成功时重置 LoginAttempt
- JWT 认证用于 `/openapi/*` 路径，自动创建用户但不设密码
- Session 认证用于 Web UI，依赖 Django session middleware
- `/init/` 接口不调用任何外部 API，全部从本地数据库查询

## ADDED Requirements

### Requirement: Session authentication
The system SHALL keep Django session-based authentication via `ModelBackend` as the primary authentication method for web UI access. Login endpoint SHALL be `POST /account/login/` accepting `username` and `password`, using Django's `authenticate()` + `login()`. Logout endpoint SHALL be `POST /account/logout/` using Django's `logout()`.

#### Scenario: Successful login
- **WHEN** POST `/account/login/` with valid username and password
- **THEN** session is created, returns `{result: true, data: {redirect_url: "/"}}`

#### Scenario: Failed login
- **WHEN** POST `/account/login/` with invalid credentials
- **THEN** returns `{result: false, message: "用户名或密码错误"}` with status 401

### Requirement: JWT authentication for OpenAPI
The system SHALL keep JWT authentication via `CustomUserBackend` for OpenAPI (`/openapi/*`) access. The backend SHALL extract JWT from `Authorization: Bearer <token>` header, decode with `settings.SECRET_KEY` using HS256, and look up or auto-create User by username from `payload["sub"]` or `payload["username"]`. Auto-created users SHALL have no password set.

#### Scenario: Valid JWT token
- **WHEN** request includes `Authorization: Bearer <valid_jwt>` with `sub=zhangsan`
- **THEN** user is authenticated as zhangsan

#### Scenario: Auto-create user from JWT
- **WHEN** JWT payload contains username "newuser" who does not exist in DB
- **THEN** User is auto-created with nickname=username, no password

#### Scenario: Expired JWT token
- **WHEN** JWT is expired
- **THEN** authentication returns None, request proceeds as anonymous

### Requirement: Init endpoint rewrite
The system SHALL rewrite the `GET /init/` endpoint to return user info + permissions from local data without any external API calls. The endpoint SHALL NOT call `UserRole.update_cmdb_common_roles()` or `BKUserRole.get_or_update_user_roles()`. Response format SHALL be: `{code: 0, result: true, data: {DEFAULT_PROJECT, chname, username, all_access, IS_ITSM_ADMIN, need_target: false, location: "", permissions: [...]}}`.

#### Scenario: Init returns local data
- **WHEN** authenticated user GET `/init/`
- **THEN** returns user info from local User model, `chname` from `user.chname`, `IS_ITSM_ADMIN` from Role check, `all_access` from Role role_keys, `permissions` from aggregated Role→Permission codes

#### Scenario: Init without external calls
- **WHEN** `/init/` is called and no external services are available
- **THEN** response succeeds with all data from local DB

### Requirement: User batch query API compatibility
The system SHALL provide `GET /gateway/bk_login/get_batch_users/` and `GET /gateway/bk_login/get_all_users/` endpoints querying local User table. The batch endpoint SHALL accept `users` (comma-separated usernames), `properties`, `exact_lookups`, `fuzzy_lookups`, `page`, `page_size` parameters. Response SHALL format users as `{username, display_name, chname, email, phone, departments: [{full_name}]}`.

#### Scenario: Batch users query
- **WHEN** GET `/gateway/bk_login/get_batch_users/?users=zhangsan,lisi`
- **THEN** returns user info with `display_name` and `departments` populated from local DeptMembership

#### Scenario: Fuzzy search
- **WHEN** GET `/gateway/bk_login/get_batch_users/?fuzzy_lookups=zhang`
- **THEN** returns users whose username or chname contains "zhang"

#### Scenario: All users query
- **WHEN** GET `/gateway/bk_login/get_all_users/`
- **THEN** returns all active users, cached for 30 minutes

### Requirement: User selector JSONP API compatibility
The system SHALL provide `GET /api/c/compapi/v2/usermanage/fs_list_users/` endpoint compatible with the `@blueking/user-selector` component. SHALL support JSONP callback via `callback` parameter. SHALL accept `exact_lookups`, `fuzzy_lookups`, `page`, `page_size`, `app_code` parameters. Response SHALL be wrapped in JSONP callback when `callback` parameter is present.

#### Scenario: JSONP user search
- **WHEN** GET with `callback=jQuery123&fuzzy_lookups=zhang`
- **THEN** response is `jQuery123({result: true, data: {results: [...], count: N}})`

#### Scenario: Exact user lookup for selector
- **WHEN** GET with `exact_lookups=zhangsan,lisi`
- **THEN** returns exact match users with username, display_name fields

### Requirement: Authentication backends configuration
The system SHALL configure `AUTHENTICATION_BACKENDS` to include `"django.contrib.auth.backends.ModelBackend"` and the JWT backend from the users module. The `CustomUserBackend` in `itsm/openapi/authentication/` SHALL be updated to import from the new users module or be moved into it.

#### Scenario: Backends configured
- **WHEN** Django settings are loaded
- **THEN** `AUTHENTICATION_BACKENDS` includes ModelBackend and the users module's JWT backend
