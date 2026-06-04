## Purpose

Frontend security policy management page providing runtime configuration for password policies, login security policies, and session policies. Also provides a locked accounts view with unlock capability for administrators.

## Requirements

### Requirement: Security policy list with tabs
The system SHALL provide a security policy page at `/manage/security_policy` with `<bk-tab>` component containing four tabs: "密码策略" (category=password), "登录策略" (category=login), "会话策略" (category=session), "锁定账户" (locked accounts). Each policy tab SHALL display a `<bk-table>` with columns: description (策略名称/描述), current_value (当前值), default_value (默认值, shown as reference), actions (编辑).

#### Scenario: Load policy list
- **WHEN** user navigates to `/manage/security_policy`
- **THEN** page loads policies from `GET /api/security-policies/` and displays in tabbed layout

#### Scenario: Switch to login policy tab
- **WHEN** user clicks "登录策略" tab
- **THEN** table filters to show only policies with category="login"

#### Scenario: Boolean value display
- **WHEN** policy "password_require_uppercase" has value=true
- **THEN** current_value column shows "是" (or green tag)

#### Scenario: Numeric value display
- **WHEN** policy "password_min_length" has value=8
- **THEN** current_value column shows "8"

### Requirement: Edit security policy dialog
The system SHALL provide a `<bk-dialog>` for editing policy values. Boolean policies SHALL use `<bk-switcher>` component. Numeric policies SHALL use `<bk-input type="number">` with min/max validation. The submit button SHALL call `PATCH /api/security-policies/{id}/` with `{value: newValue}`. Only users with `feature:system:security-manage` permission SHALL see the edit button.

#### Scenario: Edit numeric policy
- **WHEN** admin clicks "编辑" on "密码最小长度" and changes value to 12
- **THEN** `PATCH /api/security-policies/{id}/` is called with `{value: 12}`, table refreshes

#### Scenario: Edit boolean policy
- **WHEN** admin clicks "编辑" on "要求包含特殊字符" and toggles switcher to "是"
- **THEN** `PATCH /api/security-policies/{id}/` is called with `{value: true}`

#### Scenario: Invalid numeric value
- **WHEN** admin enters -1 for "密码最小长度"
- **THEN** validation error "值不能小于 1" is shown, no API call

#### Scenario: Edit without permission
- **WHEN** non-admin views the page
- **THEN** "编辑" buttons are hidden, policies are read-only

### Requirement: Locked accounts list tab
The system SHALL provide a "锁定账户" tab showing all LoginAttempt records where `locked_until` is in the future. The table SHALL show columns: username (用户名), ip_address (IP地址), attempts (失败次数), locked_until (锁定至, formatted relative time). Each row SHALL have an "解锁" action button.

#### Scenario: View locked accounts
- **WHEN** user clicks "锁定账户" tab
- **THEN** table shows all currently locked accounts from `GET /api/security-policies/locked_accounts/` (or equivalent endpoint)

#### Scenario: No locked accounts
- **WHEN** no accounts are currently locked
- **THEN** empty state shows "当前无锁定账户"

#### Scenario: Unlock account
- **WHEN** admin clicks "解锁" on locked account "zhangsan"
- **THEN** confirmation dialog appears, on confirm `POST /api/security-policies/unlock/` with `{username: "zhangsan"}` is called, row removed from table

#### Scenario: Unlock without permission
- **WHEN** non-admin views the locked accounts tab
- **THEN** "解锁" buttons are hidden

### Requirement: SecurityPolicy Vuex Store module
The system SHALL provide a Vuex Store module `securityPolicy` (namespaced) with actions: `list` (GET /api/security-policies/), `update` (PATCH /api/security-policies/{id}/), `unlock` (POST /api/security-policies/unlock/), `lockedAccounts` (GET /api/security-policies/locked_accounts/ or equivalent).

#### Scenario: List policies
- **WHEN** component dispatches `securityPolicy/list`
- **THEN** GET `/api/security-policies/` is called

#### Scenario: Update policy
- **WHEN** component dispatches `securityPolicy/update` with `{id: 1, value: 12}`
- **THEN** PATCH `/api/security-policies/1/` is called with `{value: 12}`

#### Scenario: Unlock user
- **WHEN** component dispatches `securityPolicy/unlock` with `{username: "zhangsan"}`
- **THEN** POST `/api/security-policies/unlock/` with `{username: "zhangsan"}` is called
