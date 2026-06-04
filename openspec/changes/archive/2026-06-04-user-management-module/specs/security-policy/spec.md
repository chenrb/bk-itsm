## Functional Overview

### Module Purpose

安全策略模块提供运行时可配置的密码策略和登录安全策略。所有策略存储在数据库中（SecurityPolicy 模型），管理员可通过 API 修改，无需重启服务即可生效。

### Security Policy Categories

#### Password Policies (category: `password`)

| Key | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `password_min_length` | int | 8 | 密码最小长度 |
| `password_require_uppercase` | bool | True | 是否要求包含大写字母 |
| `password_require_lowercase` | bool | True | 是否要求包含小写字母 |
| `password_require_digit` | bool | True | 是否要求包含数字 |
| `password_require_special` | bool | False | 是否要求包含特殊字符 |
| `password_history_count` | int | 0 | 禁止重复使用最近 N 次密码（0=不限制） |
| `password_max_age_days` | int | 0 | 密码过期天数（0=永不过期） |

#### Login Policies (category: `login`)

| Key | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `login_max_attempts` | int | 5 | 连续失败锁定阈值 |
| `login_lockout_minutes` | int | 30 | 锁定持续时间（分钟） |

#### Session Policies (category: `session`)

| Key | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `session_timeout_minutes` | int | 480 | Session 空闲超时时间（分钟），默认 8 小时 |

### Password Change Flow with Security

```
用户请求修改密码
  → 验证旧密码（自助修改时）
  → PasswordValidator 检查：
    → 长度 >= password_min_length
    → 包含大写（如果 password_require_uppercase）
    → 包含小写（如果 password_require_lowercase）
    → 包含数字（如果 password_require_digit）
    → 包含特殊字符（如果 password_require_special）
  → PasswordHistory 检查：
    → 新密码不在最近 password_history_count 次历史中
  → 通过 → 保存旧密码到 PasswordHistory → 更新密码
```

### Login Lockout Flow

```
用户登录失败
  → LoginAttempt.attempts += 1
  → attempts < login_max_attempts → 返回 "用户名或密码错误"
  → attempts >= login_max_attempts → locked_until = now + login_lockout_minutes
    → 返回 "账户已锁定，请 X 分钟后重试"

用户登录成功
  → LoginAttempt.attempts = 0, locked_until = None
  → 正常创建 session

被锁定用户尝试登录
  → 检查 locked_until > now → 直接返回锁定提示，不验证密码
  → 检查 locked_until <= now → 已过期，正常验证，成功则重置
```

### Admin Unlock Flow

管理员可通过 Django admin 或 API 手动解锁被锁定的账户：
- `POST /api/security-policies/{id}/unlock/` — 清除指定用户的 LoginAttempt 记录
- 仅 `feature:system:security-manage` 权限可执行

### Key Behaviors

- 所有策略在数据库中存储，修改后立即生效，无需重启
- `SecurityPolicy.get_value(key, default)` 提供便捷的运行时查询
- 内置策略（`is_builtin=True`）不可删除，但可修改 value
- PasswordValidator 注册在 Django `AUTH_PASSWORD_VALIDATORS` 中，在用户创建和密码修改时自动触发
- `password_history_count=0` 时不进行密码历史检查（功能关闭）
- `login_max_attempts` 按 `(username, ip_address)` 组合计数，同一用户不同 IP 分别计数

## ADDED Requirements

### Requirement: SecurityPolicy model for runtime configuration
The system SHALL provide a SecurityPolicy model with fields: `key` (CharField, unique), `value` (JSONField), `category` (CharField, one of: password, login, session), `description` (TextField, blank), `is_builtin` (BooleanField, default=True). The model SHALL provide a class method `get_value(key, default=None)` that returns the deserialized value for a given key.

#### Scenario: Get password min length
- **WHEN** `SecurityPolicy.get_value("password_min_length", 8)` is called and the DB record exists with value=12
- **THEN** returns 12

#### Scenario: Get with default
- **WHEN** `SecurityPolicy.get_value("nonexistent_key", "default_val")` is called and no record exists
- **THEN** returns "default_val"

#### Scenario: Update policy value
- **WHEN** admin updates `password_min_length` from 8 to 12
- **THEN** next call to `get_value("password_min_length")` returns 12 without restart

### Requirement: Password policy validation
The system SHALL validate passwords against SecurityPolicy settings on user creation and password change. Supported policies: `password_min_length` (int, default 8), `password_require_uppercase` (bool, default True), `password_require_lowercase` (bool, default True), `password_require_digit` (bool, default True), `password_require_special` (bool, default False). Validation SHALL be implemented as a Django password validator class.

#### Scenario: Password too short
- **WHEN** user sets password "abc" and `password_min_length` is 8
- **THEN** validation fails with message "密码长度不能少于 8 个字符"

#### Scenario: Password missing uppercase
- **WHEN** user sets password "abcdefg1" and `password_require_uppercase` is True
- **THEN** validation fails with message "密码必须包含大写字母"

#### Scenario: Password meets all requirements
- **WHEN** user sets password "Abcdefg1!" and all policies are satisfied
- **THEN** validation passes

### Requirement: LoginAttempt model and lockout
The system SHALL provide a LoginAttempt model with fields: `username` (CharField), `ip_address` (GenericIPAddressField), `attempts` (IntegerField, default=0), `locked_until` (DateTimeField, nullable). After each failed login, `attempts` SHALL be incremented. When `attempts` reaches `login_max_attempts` (from SecurityPolicy, default 5), the account SHALL be locked until `locked_until` (calculated as `now + login_lockout_minutes` from SecurityPolicy, default 30). Successful login SHALL reset attempts to 0.

#### Scenario: Failed login increments attempts
- **WHEN** login fails for username "zhangsan"
- **THEN** LoginAttempt.attempts is incremented by 1

#### Scenario: Account lockout after max attempts
- **WHEN** 5th consecutive failed login occurs and `login_max_attempts` is 5
- **THEN** `locked_until` is set to now + 30 minutes, further login attempts are rejected with "账户已锁定"

#### Scenario: Successful login resets
- **WHEN** login succeeds for "zhangsan"
- **THEN** LoginAttempt.attempts is reset to 0, `locked_until` is cleared

#### Scenario: Locked account login rejected
- **WHEN** login attempted for account with `locked_until` in the future
- **THEN** returns error "账户已锁定，请 X 分钟后重试" without checking password

### Requirement: PasswordHistory model
The system SHALL provide a PasswordHistory model with fields: `user` (FK to User, CASCADE), `password_hash` (CharField), `created_at` (DateTimeField, auto_now_add). On password change, the system SHALL check against `password_history_count` (from SecurityPolicy, default 0, meaning disabled) previous passwords. If the new password matches any of the last N passwords, the change SHALL be rejected.

#### Scenario: Password reuse rejected
- **WHEN** user changes to a password that was used in the last 3 passwords, and `password_history_count` is 3
- **THEN** change is rejected with "不能使用最近 3 次使用过的密码"

#### Scenario: Password history disabled
- **WHEN** `password_history_count` is 0
- **THEN** no password history check is performed

#### Scenario: Password change stores history
- **WHEN** user successfully changes password
- **THEN** old password hash is stored in PasswordHistory

### Requirement: SecurityPolicy CRUD API
The system SHALL provide a DRF ViewSet for SecurityPolicy with list, retrieve, update actions. Only users with `feature:system:security-manage` permission SHALL modify policies. Creation and deletion SHALL be restricted (policies managed via init_builtin_data).

#### Scenario: List policies
- **WHEN** GET `/api/security-policies/`
- **THEN** returns all security policies grouped by category

#### Scenario: Update policy value
- **WHEN** PATCH `/api/security-policies/{id}/` with `{value: 12}` by admin user
- **THEN** policy value is updated, takes effect immediately

#### Scenario: Non-admin update rejected
- **WHEN** non-admin user attempts to update a policy
- **THEN** returns 403 Forbidden

### Requirement: Admin unlock locked account
The system SHALL provide `POST /api/security-policies/unlock/` accepting `{username: "zhangsan"}` to clear LoginAttempt records for a user, unlocking the account. This action SHALL be restricted to users with `feature:system:security-manage` permission.

#### Scenario: Admin unlocks account
- **WHEN** admin POST `/api/security-policies/unlock/` with `{username: "zhangsan"}`
- **THEN** LoginAttempt records for zhangsan are deleted, account is immediately unlocked

#### Scenario: Unlock without permission
- **WHEN** non-admin POST `/api/security-policies/unlock/`
- **THEN** returns 403 Forbidden

### Requirement: SecurityPolicy and related models registered in Django admin
The system SHALL register SecurityPolicy, LoginAttempt, and PasswordHistory in Django admin.

#### Scenario: Admin security policy management
- **WHEN** admin visits `/admin/users/securitypolicy/`
- **THEN** policy list is displayed with inline value editing

### Requirement: Init builtin security policies
The system SHALL initialize default security policies via `manage.py init_builtin_data --app security_policy`. Default policies SHALL include: `password_min_length=8`, `password_require_uppercase=True`, `password_require_lowercase=True`, `password_require_digit=True`, `password_require_special=False`, `password_history_count=0`, `password_max_age_days=0`, `login_max_attempts=5`, `login_lockout_minutes=30`, `session_timeout_minutes=480`.

#### Scenario: Init security policies
- **WHEN** `init_builtin_data --app security_policy` is run
- **THEN** all default policies are created with is_builtin=True
