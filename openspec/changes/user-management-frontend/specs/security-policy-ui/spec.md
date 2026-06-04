## Functional Overview

### Module Purpose

安全策略管理页面提供密码策略、登录安全策略、会话策略的运行时配置界面，以及被锁定账户的查看与解锁功能。所有策略存储在后端数据库中，修改后立即生效。

### Business Capabilities

1. **策略列表**：按类别（密码/登录/会话）分组展示所有安全策略
2. **策略编辑**：修改策略值（数字、布尔、字符串类型）
3. **锁定账户**：查看当前被锁定的账户列表，管理员可手动解锁
4. **策略说明**：每个策略显示描述、当前值、默认值

### Page Layout

```
┌───────────────────────────────────────────────────────────────┐
│ 安全策略                                                      │
├───────────────────────────────────────────────────────────────┤
│ [密码策略] [登录策略] [会话策略] [锁定账户]  ← Tab 切换       │
├───────────────────────────────────────────────────────────────┤
│ --- 密码策略 Tab ---                                          │
│ 策略名称              | 当前值  | 默认值 | 操作               │
│ 密码最小长度          | 8       | 8      | [编辑]             │
│ 要求包含大写字母      | 是      | 是     | [编辑]             │
│ 要求包含小写字母      | 是      | 是     | [编辑]             │
│ 要求包含数字          | 是      | 是     | [编辑]             │
│ 要求包含特殊字符      | 否      | 否     | [编辑]             │
│ 密码历史检查数量      | 0       | 0      | [编辑]             │
│ 密码过期天数          | 0       | 0      | [编辑]             │
├───────────────────────────────────────────────────────────────┤
│ --- 锁定账户 Tab ---                                          │
│ 用户名     | IP地址        | 失败次数 | 锁定至         | 操作 │
│ zhangsan   | 192.168.1.5   | 5        | 14:30 (30分钟后)| [解锁]│
│ lisi       | 10.0.0.3      | 5        | 14:45 (25分钟后)| [解锁]│
└───────────────────────────────────────────────────────────────┘

--- 编辑策略 Dialog ---

┌───────────────────────────────────┐
│ 编辑 - 密码最小长度               │
│ 描述: 密码的最小字符数             │
│ 当前值: [8        ]               │
│ 默认值: 8                         │
│                 [取消] [保存]      │
└───────────────────────────────────┘
```

### Integration Points

- **API**: `GET /api/security-policies/`（列表）、`PATCH /api/security-policies/{id}/`（更新）、`POST /api/security-policies/unlock/`（解锁）
- **Store**: `store/modules/securityPolicy.js`
- **权限**: `feature:system:security-manage` 控制策略修改和账户解锁

### Key Behaviors

- 策略列表按 category 分为三个 Tab：密码策略、登录策略、会话策略
- 第四个 Tab 展示锁定账户列表（从 LoginAttempt 模型查询）
- 布尔值策略使用 Switch 组件编辑
- 数值策略使用 InputNumber 组件编辑
- 管理员可一键解锁被锁定的账户

## ADDED Requirements

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
