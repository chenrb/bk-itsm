## Why

项目已从蓝鲸 PaaS 平台完全解耦，但前后端认证流程仍依赖蓝鲸 SSO（`@blueking/login-modal`、`login.js`、`window.login_url` 跳转）。这些依赖已失效——蓝鲸登录服务不存在，未登录用户无法进入系统。需要建立独立的本地认证体系，让 SPA 自身处理登录/登出/会话管理。同时清理蓝鲸遗留的 cookie 前缀（`bkitsm_`）和语言 cookie（`blueking_language`）。

## What Changes

- **新增 Vue 登录页组件**：`/login` 路由，用户名+密码表单，POST JSON 到后端
- **重写前端 401 处理**：移除蓝鲸 SSO 跳转和 `showLoginModal`，改为路由跳转到 `/login`
- **重写后端登录接口**：从 TemplateView 改为纯 JSON API（接受 JSON body，返回 JSON）
- **后端 init 视图**：添加未登录检测，返回 401；移除 `need_target`/`location` 字段
- **路由守卫**：未登录时自动跳转 `/login`，已登录时禁止访问 `/login`
- **登出流程**：改为 POST `/account/logout/` + 前端清除状态 + 路由跳转
- **Cookie 重命名**：`bkitsm_sessionid` → `itsm_sessionid`，`bkitsm_csrftoken` → `itsm_csrftoken`
- **语言 cookie 重命名**：`blueking_language` → `itsm_language`
- **删除蓝鲸 SSO 代码**：`login.js`、`isCrossOriginIFrame.js`、`passApi.js`、`login_success.html`、`@blueking/login-modal` 依赖
- **移除 `UserLoginForbiddenMiddleware`**：不再需要拦截蓝鲸登录重定向
- **删除 Django 登录模板**：`templates/registration/login.html`（由 Vue 登录页替代）

## Capabilities

### New Capabilities
- `spa-auth`: SPA 内登录/登出/会话管理，包含前端登录页、路由守卫、401 处理、CSRF 流程

### Modified Capabilities
<!-- No existing specs to modify -->

## Impact

- **前端**：`src/views/login/`（新增）、`src/router/index.js`、`src/utils/ajax.js`、`src/main.js`、`src/App.vue`、`src/store/index.js`、`src/stores/root.js`、`Navigation.vue`、`index.html`、`package.json`
- **后端**：`config/web.py`、`config/apps.py`、`itsm/users/views/auth.py`、`itsm/users/urls.py`、`itsm/sites/views.py`、`itsm/component/misc_middlewares.py`、`itsm/iadmin/views.py`
- **删除文件**：`templates/registration/login.html`、`src/utils/login.js`、`src/utils/isCrossOriginIFrame.js`、`src/utils/passApi.js`、`login_success.html`
- **依赖移除**：`@blueking/login-modal` npm 包
- **Cookie 变更**：所有用户需重新登录（session cookie 名称变更）
