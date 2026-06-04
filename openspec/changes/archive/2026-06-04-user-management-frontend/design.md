## Context

BK-ITSM 前端基于 Vue 3 + BKUI-Vue（蓝鲸组件库）+ Vuex 4 构建。管理类页面统一放在 `/manage/` 路由下，使用 `<bk-table>` + `<bk-dialog>` / `<bk-sideslider>` 实现列表+弹窗模式。API 调用通过 Vuex Store 的 actions 中封装 `ajax.get/post/put/delete` 完成。

后端 `user-management-module` 变更提供了完整的用户管理 REST API（`/api/users/`、`/api/departments/`、`/api/roles/`、`/api/user-groups/`、`/api/permissions/`、`/api/security-policies/`），前端需要新建对应管理页面。

当前状态：
- `/manage/user_management` 路由已注册但组件为空
- `/project/role.vue` 管理角色组，使用旧 API，需迁移
- 前端无部门树、角色权限、安全策略相关页面
- 前端权限检查使用 `usePermission` composable + IAM action 字符串，需扩展支持新权限编码

## Goals / Non-Goals

**Goals:**

- 为用户、部门、角色、角色组、安全策略各提供完整的管理页面
- 所有页面遵循项目现有 BKUI-Vue 组件和布局模式
- 对接后端权限体系，前端路由守卫和按钮权限基于 `permissions` 数组
- 角色组管理从 `/project/role.vue` 迁移到 `/manage/user_group`
- 部门树使用 BKUI-Vue 的树组件，支持懒加载
- 所有用户可见文本使用 i18n

**Non-Goals:**

- 不重写整体布局框架或导航结构（使用现有 manage 区域）
- 不引入新的 UI 组件库（仅用 BKUI-Vue 已有组件）
- 不修改后端 API（前端完全消费 `user-management-module` 提供的 API）
- 不实现前端单元测试（项目现状无前端测试框架）
- 不做响应式适配（管理后台以桌面端为主）

## Decisions

### D1: 页面路由统一在 `/manage/` 下

**选择**：5 个新页面全部注册为 `/manage/` 的子路由

**理由**：现有管理功能（全局设置、通知配置等）均在 `/manage/` 下，用户管理属于系统管理范畴，应放在同一区域。路由注册复用 `manage.js` 路由文件。

**替代方案**：
- 新建 `/system/` 路由区域 → 增加导航菜单改动，收益不大
- 在 `/project/` 下管理 → 不符合"系统管理"定位

### D2: Vuex Store 按资源拆分为独立模块

**选择**：新建 5 个 Vuex Store 模块：`userManagement`、`department`、`roleManagement`、`userGroup`、`securityPolicy`

**理由**：与现有模式一致（`store/modules/role.js`、`store/modules/datadict.js`）。每个模块封装对应资源的 CRUD actions，组件通过 `this.$store.dispatch('userManagement/list', params)` 调用。

**替代方案**：
- 单一 `userManagement` Store → 模块过大，维护困难
- Pinia Store → 项目同时使用 Vuex 和 Pinia，但管理类页面现有代码都用 Vuex，保持一致

### D3: 部门树使用 BKUI-Vue `<bk-big-tree>` 组件

**选择**：使用 `<bk-big-tree>` 实现部门树，配合懒加载（`lazy` + `async-load` 属性）

**理由**：`<bk-big-tree>` 是 BKUI-Vue 提供的大数据树组件，支持虚拟滚动、懒加载、节点拖拽排序，满足部门树的交互需求。

**替代方案**：
- 自定义递归组件 → 工作量大，功能不如 `<bk-big-tree>` 完整
- 第三方树组件（如 vue3-tree） → 引入新依赖，风格不统一

### D4: 权限矩阵使用分组勾选面板

**选择**：角色编辑时，权限分配使用按 category 分组的 Checkbox 面板（workflow、ticket、system、project、sla、task 六个分组），每个分组内按 page → button → feature 三层展示

**理由**：38 个权限如果平铺为单列 checkbox 列表过长，按业务模块分组更直观。三层权限（page 全选 → 自动勾选对应 btn/feature）可通过前端逻辑实现联动提示（但后端不做联动，仅前端展示）。

### D5: 角色组页面替代原有 `/project/role.vue`

**选择**：新建 `/manage/user_group` 页面管理角色组，原 `/project/role.vue` 保留但重定向到新页面

**理由**：角色组（UserGroup）属于系统管理资源，不应放在项目级别页面中。新页面使用新的 `/api/user-groups/` API，旧页面做 301 重定向以保证书签兼容。

### D6: 前端权限检查扩展 `usePermission` composable

**选择**：扩展现有 `usePermission` composable，增加 `hasPermissionCode(code)` 方法，直接检查 `permissions` 数组中是否包含指定权限编码（如 `feature:system:user-manage`）

**理由**：现有 `hasPermission()` 方法基于 IAM action 字符串（如 `user_create`），新增 `hasPermissionCode()` 支持新权限编码格式，两套并存过渡，最终统一到新格式。

### D7: 弹窗 vs SideSlider 选择策略

**选择**：
- 用户创建/编辑 → `<bk-sideslider>`（字段多：username、password、chname、email、phone、department、leader）
- 部门创建/编辑 → `<bk-dialog>`（字段少：name、parent、order）
- 角色创建/编辑 → `<bk-sideslider>`（需展示权限矩阵）
- 角色组创建/编辑 → `<bk-dialog>`（字段简单 + member-select）
- 安全策略编辑 → `<bk-dialog>`（单字段编辑：value）

**理由**：字段多、交互复杂的表单用 SideSlider 给予充足空间；简单表单用 Dialog。

## Risks / Trade-offs

- **[BKUI-Vue 组件 API 不稳定]** → BKUI-Vue v2.x API 可能与文档有差异，实现时需实际测试组件行为，备选方案为降级到基础 HTML + 自定义样式
- **[权限过渡期两套并存]** → 旧 IAM action 字符串和新权限编码短期内共存，`usePermission` 需同时支持两种格式，增加维护成本 → 计划在角色管理前端上线后逐步迁移
- **[部门树大数据量性能]** → 如果部门数超过 500 个，懒加载可保证性能；但全量加载场景（搜索、移动节点）需要后端分页支持 → 后端 `/api/departments/` 已支持 `flat=true` 参数返回扁平列表
- **[member-select 组件兼容性]** → 现有 member-select 依赖 `@blueking/user-selector` 和 JSONP API，需确保 `/api/c/compapi/v2/usermanage/fs_list_users/` 后端已实现 → 该 API 在 `user-management-module` 变更的 auth spec 中已定义
- **[路由冲突]** → `/manage/user_management` 已注册，需确认新组件正确替换 → 直接更新 `manage.js` 中的 import 指向新组件

## Migration Plan

1. 新增 Store 模块和路由，不影响现有页面
2. 新建 `/manage/user_management` 组件替换空页面
3. 新建 `/manage/department`、`/manage/role`、`/manage/user_group`、`/manage/security_policy` 页面
4. `/project/role.vue` 添加重定向逻辑到 `/manage/user_group`
5. 在导航菜单（左侧边栏）中添加"用户管理"分组入口
6. 验证所有页面 API 联调

## Open Questions

- 左侧导航菜单是否需要新增"用户管理"分组，还是复用现有"系统管理"分组下的子菜单？→ 取决于导航配置的实现方式
- 是否需要部门节点拖拽排序功能？→ 后端 Department 有 `order` 字段，前端可支持拖拽但非必须
