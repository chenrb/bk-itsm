## Why

后端用户管理模块（`user-management-module` 变更）已完成设计，提供了完整的本地用户、部门、角色、角色组、安全策略管理 API，但前端尚无对应的管理界面。当前项目前端中：
- `/manage/user_management` 路由已注册但页面为空
- 部门树管理完全缺失（无任何前端代码）
- 角色组管理散落在 `/project/role.vue`，使用旧的 `role/users/` API
- 角色（权限角色）和安全策略无前端入口
- 前端权限检查仍依赖旧的 `window.IS_ITSM_ADMIN` / `all_access` 死代码，未对接新的 `permissions` 数组

需要在"系统管理"区域下新建一整套用户管理前端页面，与后端 API 对齐，遵循项目现有的 BKUI-Vue 组件库 + Vuex Store + i18n 模式。

## What Changes

- **新增用户管理页面**：用户列表（搜索/过滤/分页）、创建/编辑用户弹窗、密码修改/重置、启用/停用
- **新增部门管理页面**：部门树可视化（懒加载）、创建/编辑/排序部门、部门成员管理
- **新增角色管理页面**：角色列表、创建/编辑角色、权限分配（38 个内置权限可视化勾选）、成员管理
- **新增角色组管理页面**：角色组列表、创建/编辑角色组、成员/负责人管理（替代原 `/project/role.vue`）
- **新增安全策略页面**：密码/登录/会话策略配置、锁定账户查看与解锁
- **新增权限 API Store**：Vuex Store 模块对接 `/api/users/`、`/api/departments/`、`/api/roles/`、`/api/user-groups/`、`/api/permissions/`、`/api/security-policies/`
- **改写 init 接口消费**：`/init/` 响应中读取 `permissions` 数组，存入 Vuex，供路由守卫和组件使用
- **新增路由**：在 `/manage/` 下注册 5 个子路由（user_management、department、role、user_group、security_policy）
- **i18n 词条**：新增用户管理模块的全部中文/英文/日文翻译 key

## Capabilities

### New Capabilities

- `user-list-ui`: 用户列表页面，含搜索过滤、CRUD 弹窗、密码管理、启用/停用功能
- `department-tree-ui`: 部门树管理页面，含树形可视化、懒加载、CRUD、成员管理
- `role-permission-ui`: 角色与权限管理页面，含角色 CRUD、权限矩阵勾选、成员/负责人管理
- `user-group-ui`: 角色组（处理人分组）管理页面，含 CRUD、成员/负责人管理，替代原 project/role.vue
- `security-policy-ui`: 安全策略管理页面，含策略配置编辑、锁定账户列表与解锁
- `permission-integration`: 前端权限对接层，init 接口读取 permissions 数组、路由守卫、组件权限检查

### Modified Capabilities

（无 — 本变更为纯前端新增，不修改后端 spec 行为）

## Impact

- **前端代码**：新增 ~15 个 Vue 组件文件、5 个 Vuex Store 模块、5 条路由
- **依赖**：继续使用 BKUI-Vue（已安装），不引入新第三方库；部门树使用 BKUI-Vue 的 `<bk-tree>` 或 `<bk-big-tree>` 组件
- **API 消费**：所有 API 均由后端 `user-management-module` 变更提供，前端不做数据 Mock
- **i18n**：需在 `src/i18n/` 目录下新增用户管理模块的翻译词条（zh-cn、en、ja 三语言）
- **权限对接**：`/init/` 响应新增 `permissions` 字段需存入 Vuex；现有 `usePermission` composable 需扩展支持新的权限编码格式（`{type}:{module}:{action}`）
- **样式**：遵循现有 `bk-itsm-service` / `itsm-page-content` / `bk-only-btn` 布局体系，不引入新 CSS 框架
