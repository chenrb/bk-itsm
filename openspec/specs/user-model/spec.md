## Purpose

用户管理模块提供系统用户的全生命周期管理，是所有认证、授权、组织架构、工单处理的基础。替代原有依赖蓝鲸 PaaS 平台的用户查询接口，所有用户数据存储在本地数据库中。

## Requirements

### Requirement: Internationalization across all models and APIs
All model field `verbose_name`, `help_text`, and `Meta.verbose_name`/`verbose_name_plural` SHALL use `gettext_lazy` (imported as `_`). All user-facing error messages in serializers, validators, views, and exceptions SHALL use `gettext` (imported as `_`). Error messages, validation errors, and API response messages SHALL be wrapped with `_()` for translation. This applies to all new models (User, Department, DeptMembership, Role, UserGroup, Permission, SecurityPolicy, LoginAttempt, PasswordHistory) and all new views/serializers.

#### Scenario: Model field verbose_name is translatable
- **WHEN** User model defines `chname` field with `verbose_name=_("中文名")`
- **THEN** the verbose_name is lazily translated in Django admin and forms

#### Scenario: Validation error message is translatable
- **WHEN** password validation fails with message `_("密码长度不能少于 %(min_length)s 个字符")`
- **THEN** the message is translated to the user's active language

### Requirement: User model with leader and department fields
The system SHALL provide a User model extending `AbstractBaseUser` and `PermissionsMixin` with the following fields: `username` (unique), `nickname`, `chname`, `email`, `phone`, `leader` (nullable self-referencing FK to User), `department` (nullable FK to Department as primary department), `is_staff`, `is_active`, `is_superuser`, `date_joined`. The `leader` field SHALL be nullable and blank-able. The `department` field SHALL be nullable and blank-able. The db_table SHALL be `users_user`. The `USERNAME_FIELD` SHALL be `username`. The model SHALL provide a `display_name` property returning `nickname` if set, else `chname` if set, else `username`.

#### Scenario: User with leader
- **WHEN** a User is created with `leader` pointing to another User
- **THEN** `user.leader` returns the referenced User instance

#### Scenario: User without leader
- **WHEN** a User is created without setting `leader`
- **THEN** `user.leader` is None

#### Scenario: User display name fallback
- **WHEN** `nickname` is set, return nickname
- **WHEN** `nickname` is empty but `chname` is set, return chname
- **WHEN** both are empty, return `username`

### Requirement: User CRUD API
The system SHALL provide a DRF ViewSet for User management with list, retrieve, create, update, partial_update, destroy actions. Creation and modification SHALL be restricted to users with `feature:system:user-manage` permission. The list endpoint SHALL support filtering by `username`, `nickname`, `chname`, `email`, `department`, `is_active`. The list endpoint SHALL support search by `username` and `chname`. Pagination SHALL follow project defaults.

#### Scenario: Create user
- **WHEN** an authenticated user with `feature:system:user-manage` sends POST with `{username, password, chname, email, department_id}`
- **THEN** a new User is created and returned with status 201

#### Scenario: Create user without permission
- **WHEN** an authenticated user without `feature:system:user-manage` sends POST
- **THEN** response is 403 Forbidden

#### Scenario: List users with department filter
- **WHEN** GET `/api/users/?department=3`
- **THEN** only users whose primary department or DeptMembership links to department 3 are returned

### Requirement: User registered in Django admin
The system SHALL register User model in Django admin with list display including `username`, `chname`, `email`, `department`, `is_active`, `is_staff`. The admin SHALL support filtering by `is_active`, `is_staff`, `department`. Password changes through admin SHALL use Django's built-in password hashing.

#### Scenario: Admin user list
- **WHEN** admin visits `/admin/users/user/`
- **THEN** user list is displayed with searchable and filterable columns

### Requirement: Password change and reset API
The system SHALL provide `POST /api/users/{id}/change_password/` for self-service password change (requires `old_password` and `new_password`). The system SHALL provide `POST /api/users/{id}/reset_password/` for admin password reset (requires only `new_password`, restricted to `feature:system:user-manage`). Both endpoints SHALL enforce SecurityPolicy password validation and PasswordHistory checks.

#### Scenario: Self-service password change
- **WHEN** user POST `/api/users/me/change_password/` with `{old_password: "old", new_password: "NewPass1!"}`
- **THEN** password is updated, PasswordHistory records old hash, returns 200

#### Scenario: Self-service wrong old password
- **WHEN** user POST `/api/users/me/change_password/` with wrong `old_password`
- **THEN** returns 400 with message "旧密码不正确"

#### Scenario: Admin reset password
- **WHEN** admin with `feature:system:user-manage` POST `/api/users/5/reset_password/` with `{new_password: "TempPass1!"}`
- **THEN** user 5's password is updated without requiring old_password

### Requirement: User property compatibility
The system SHALL keep the `UserProperty` model (user FK, key, value) for backward compatibility with existing code that stores arbitrary KV pairs on users. The User model SHALL provide a `get_property(key)` method that queries UserProperty and returns the value string, or `None` if not found. For `chname`, the method SHALL return `self.chname` directly without querying UserProperty.

#### Scenario: Get chname property
- **WHEN** `user.get_property("chname")` is called
- **THEN** returns `user.chname` directly

#### Scenario: Get arbitrary property
- **WHEN** `user.get_property("profile")` is called and a UserProperty row exists with key="profile"
- **THEN** returns the stored value string

#### Scenario: Get nonexistent property
- **WHEN** `user.get_property("nonexistent")` is called and no matching UserProperty row exists
- **THEN** returns None
