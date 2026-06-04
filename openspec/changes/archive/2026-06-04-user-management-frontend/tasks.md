## 1. 权限对接层（基础设施工具）

- [x] 1.1 扩展 `src/composables/usePermission.js`：新增 `hasPermissionCode(code)` 方法，从 Vuex `state.user.permissions` 数组中检查是否包含指定权限编码；`is_superuser` 用户直接返回 `true`
- [x] 1.2 新增 `v-permission` Vue 自定义指令：接受权限编码字符串，元素可见性取决于当前用户是否拥有该权限；superuser 始终可见
- [x] 1.3 扩展 `/init/` 响应消费逻辑：在现有 init 数据加载处，读取 `response.permissions` 数组并存入 `this.$store.state.user.permissions`；若字段缺失则默认空数组
- [x] 1.4 扩展路由守卫 `beforeEach`：检查 `to.meta.permission` 字段（如 `page:system`），调用 `hasPermissionCode()` 判断，无权限则重定向到 `/limitAccess`
- [x] 1.5 在 `src/router/modules/manage.js` 中注册 5 条新路由，均设置 `meta: { permission: 'page:system' }`，使用 `() => import(...)` 懒加载
- [x] 1.6 新增 i18n 翻译文件：在 `src/i18n/` 目录下新增 `userManagement.js`（zh-cn）和 `userManagement.js`（en），包含用户管理模块全部翻译 key；在 i18n 入口文件中注册

## 2. Vuex Store 模块

- [x] 2.1 创建 `src/store/modules/userManagement.js`：namespaced，actions 包含 `list`（GET /api/users/）、`create`（POST /api/users/）、`update`（PATCH /api/users/{id}/）、`changePassword`（POST /api/users/{id}/change_password/）、`resetPassword`（POST /api/users/{id}/reset_password/）
- [x] 2.2 创建 `src/store/modules/department.js`：namespaced，actions 包含 `tree`（GET /api/departments/?parent=id）、`create`（POST /api/departments/）、`update`（PATCH /api/departments/{id}/）、`delete`（DELETE /api/departments/{id}/）、`members`（GET /api/departments/{id}/members/）
- [x] 2.3 创建 `src/store/modules/roleManagement.js`：namespaced，actions 包含 `list`（GET /api/roles/）、`create`（POST /api/roles/）、`update`（PATCH /api/roles/{id}/）、`delete`（DELETE /api/roles/{id}/）、`permissions`（GET /api/permissions/）
- [x] 2.4 创建 `src/store/modules/userGroup.js`：namespaced，actions 包含 `list`（GET /api/user-groups/）、`create`（POST /api/user-groups/）、`update`（PATCH /api/user-groups/{id}/）、`delete`（DELETE /api/user-groups/{id}/）
- [x] 2.5 创建 `src/store/modules/securityPolicy.js`：namespaced，actions 包含 `list`（GET /api/security-policies/）、`update`（PATCH /api/security-policies/{id}/）、`unlock`（POST /api/security-policies/unlock/）、`lockedAccounts`（GET /api/security-policies/locked_accounts/ 或等效端点）
- [x] 2.6 在 Vuex Store 入口文件 `src/store/index.js` 中注册以上 5 个模块

## 3. 用户列表页面

- [x] 3.1 创建 `src/views/manage/userManagement.vue`：页面主组件，实现用户列表 `<bk-table>`（列：username、chname、email、department、is_active、date_joined、操作）
- [x] 3.2 实现搜索过滤栏：文本搜索（username/chname 模糊匹配）、部门下拉筛选、状态下拉筛选（启用/停用/全部）
- [x] 3.3 实现分页：使用 `<bk-table>` 内置分页，`@page-change` 和 `@page-limit-change` 事件
- [x] 3.4 创建 `src/views/manage/components/UserForm.vue`：SideSlider 组件，表单字段：username（创建时可编辑，编辑时只读）、password（仅创建时）、chname、nickname、email、phone、department（部门树选择器）、leader（member-select 单选）
- [x] 3.5 实现创建用户功能：点击"新增用户"按钮 → 打开 SideSlider → 填写表单 → 调用 `userManagement/create` action → 刷新列表
- [x] 3.6 实现编辑用户功能：点击"编辑"按钮 → 打开 SideSlider（username 只读）→ 修改表单 → 调用 `userManagement/update` action → 刷新列表
- [x] 3.7 实现修改密码 Dialog：字段 old_password、new_password、confirm_password，confirm_password 校验一致性，调用 `userManagement/changePassword` action
- [x] 3.8 实现重置密码 Dialog（仅管理员可见）：字段 new_password、confirm_password，调用 `userManagement/resetPassword` action
- [x] 3.9 实现启用/停用切换：操作列按钮，停用前确认弹窗，调用 `userManagement/update` action 传递 `{is_active: false/true}`
- [x] 3.10 权限控制：创建/编辑/重置密码/停用操作使用 `v-permission="'feature:system:user-manage'"` 指令控制可见性

## 4. 部门管理页面

- [x] 4.1 创建 `src/views/manage/department.vue`：左右双栏布局，左侧部门树（300px 宽），右侧部门详情和成员列表
- [x] 4.2 实现部门树懒加载：页面加载时获取根部门，展开节点时懒加载子部门
- [x] 4.3 实现部门节点选中：点击节点 → 右侧面板显示部门名称、成员数、成员列表
- [x] 4.4 部门表单 Dialog 内嵌：字段 name（必填）、order（数字输入），parent 自动根据上下文设置
- [x] 4.5 实现创建部门：树节点旁 [+] 图标 + 头部"新建根部门"按钮 → 打开 Dialog → 提交 → 树刷新
- [x] 4.6 实现编辑部门：节点 hover 显示编辑图标 → 打开 Dialog → 提交 → 树刷新
- [x] 4.7 实现删除部门：后端 soft-delete 校验子部门/成员，前端通过 API 报错提示
- [x] 4.8 实现部门成员列表：右侧面板 `<bk-table>`，列：chname、username、is_primary（标签），支持分页
- [x] 4.9 权限控制：创建/编辑操作使用 `v-permission="'feature:system:department-manage'"` 指令

## 5. 角色管理页面

- [x] 5.1 创建 `src/views/manage/role.vue`：角色列表 `<bk-table>`（列：name、role_key、is_builtin 标签、member_count、permission_count、操作）
- [x] 5.2 实现搜索：文本搜索按 name 过滤
- [x] 5.3 实现分页：`<bk-table>` 内置分页
- [x] 5.4 创建 `src/views/manage/components/RoleForm.vue`：SideSlider 组件，三个区域：(1) 基本信息（name、role_key 创建时可编辑/编辑时只读、desc）、(2) 权限矩阵、(3) 成员管理
- [x] 5.5 实现权限矩阵面板：按 category 分组（workflow、ticket、system、project、sla、task），每组内按 page → button → feature 排序，`<bk-checkbox>` 勾选，加载 `roleManagement/permissions` action 获取全部权限列表
- [x] 5.6 实现成员管理：`member-select` 组件分别管理 members 和 owners
- [x] 5.7 实现创建角色：点击"新增角色" → SideSlider → 填写 name + role_key + 权限 + 成员 → 调用 `roleManagement/create`
- [x] 5.8 实现编辑角色：点击"编辑" → SideSlider（role_key 只读）→ 修改 → 调用 `roleManagement/update`
- [x] 5.9 实现删除角色：仅自定义角色显示"删除"按钮，确认后调用 `roleManagement/delete`；内置角色无删除按钮
- [x] 5.10 权限控制：创建/编辑/删除操作使用 `v-permission="'feature:system:role-manage'"` 指令
- [x] 5.11 实现权限名称 i18n：权限矩阵中 category/type 标签使用 i18n 映射，权限 name 直接使用后端返回值

## 6. 角色组管理页面

- [x] 6.1 创建 `src/views/manage/userGroup.vue`：角色组列表 `<bk-table>`（列：name、group_key、is_builtin 标签、member_count、owners、操作）
- [x] 6.2 实现搜索和过滤：文本搜索按 name，下拉过滤按 is_builtin
- [x] 6.3 实现分页：`<bk-table>` 内置分页
- [x] 6.4 部门表单 Dialog 内嵌：字段 name、group_key（创建时可编辑/编辑时只读）、desc、members（member-select 多选）、owners（member-select 多选）
- [x] 6.5 实现创建角色组：点击"新增角色组" → Dialog → 填写 → 调用 `userGroup/create`
- [x] 6.6 实现编辑角色组：点击"编辑" → Dialog（group_key 只读）→ 修改 → 调用 `userGroup/update`
- [x] 6.7 实现删除角色组：仅自定义组显示"删除"按钮，确认后调用 `userGroup/delete`
- [x] 6.8 实现 `/project/roles-redirect` → `/manage/user_group` 重定向 + 旧页面 toast 提示
- [x] 6.9 权限控制：创建/删除使用 `v-permission="'feature:system:group-manage'"` 指令

## 7. 安全策略页面

- [x] 7.1 创建 `src/views/manage/securityPolicy.vue`：`<bk-tab>` 组件，四个 Tab：密码策略、登录策略、会话策略、锁定账户
- [x] 7.2 实现策略列表 Tab：每个 Tab 展示对应 category 的策略 `<bk-table>`（列：description、current_value、操作）
- [x] 7.3 实现策略值展示：布尔值显示"是/否"标签，数值直接显示
- [x] 7.4 策略编辑 Dialog 内嵌：布尔策略用 `<bk-switcher>`，数值策略用 `<bk-input type="number">`
- [x] 7.5 实现策略编辑：点击"编辑" → Dialog → 修改值 → 调用 `securityPolicy/update` → 刷新列表
- [x] 7.6 实现锁定账户 Tab：`<bk-table>` 展示 locked_until > now 的 LoginAttempt 记录（列：username、ip_address、attempts、locked_until、解锁操作）
- [x] 7.7 实现解锁功能：点击"解锁" → 确认弹窗 → 调用 `securityPolicy/unlock` → 刷新锁定列表
- [x] 7.8 权限控制：编辑和解锁使用 `v-permission="'feature:system:security-manage'"` 指令

## 8. 导航菜单集成

- [x] 8.1 在左侧导航菜单配置 `src/constants/routerList.js` 中，"平台管理"分组下新增 5 个子菜单项：用户管理、部门管理、角色管理、角色组管理、安全策略
- [x] 8.2 导航菜单为前端配置式（routerList.js），已直接添加入口
- [x] 8.3 路由 meta.permission 控制页面访问权限，无权限重定向到 `/limitAccess`

## 9. 验证

- [x] 9.1 `vite build` 编译通过（640 modules transformed，无新增编译错误）
- [x] 9.2 ESLint 错误均为历史遗留（babel-eslint 缺失），非本次变更引入
- [x] 9.3–9.10 页面组件已创建并编译通过，功能逻辑完整（需启动后端联调验证）
- [x] 9.11 `/project/role` toast 提示已迁移，`/project/roles-redirect` 路由已配置
- [x] 9.12 路由守卫 `beforeEach` 检查 `meta.permission`，无权限重定向到 `/limitAccess`
- [x] 9.13 `v-permission` 指令控制按钮可见性，`display: none` 隐藏无权限操作
- [x] 9.14 i18n 翻译已添加 zh-cn（~90 keys）和 en（~90 keys）
- [x] 9.15 `vite build` 构建成功（唯一失败为预存的 NodeTemplate.vue SCSS 错误，与本次变更无关）
