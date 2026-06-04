## Context

BK-ITSM 已从蓝鲸 PaaS 完全解耦（Phase 1-16 重构完成），但认证层仍依赖蓝鲸 SSO：
- 前端 `ajax.js` 401 处理跳转 `login_url`（指向蓝鲸平台，已不存在）
- `@blueking/login-modal` 弹窗（依赖蓝鲸平台 iframe）
- `login.js` 注册 `window.BLUEKING.corefunc`（蓝鲸宿主 API）
- Cookie 前缀 `bkitsm_`、语言 cookie `blueking_language` 为蓝鲸遗留命名

后端已有完整的 Django session 认证：`POST /account/login/` + `ModelBackend`，但前端未使用。

开发环境：Vite `:8004` → proxy → Django `:8001`。生产环境：Django 直接 serve 静态文件。

## Goals / Non-Goals

**Goals:**
- 实现 Vue SPA 内登录页，未登录用户自动跳转
- 后端登录接口改为纯 JSON API
- 清理所有蓝鲸 SSO 依赖代码
- Cookie 前缀统一为 `itsm_`

**Non-Goals:**
- 不实现 SSO / OAuth / LDAP 等外部认证集成
- 不实现 MFA / 二步验证
- 不实现密码找回功能
- 不修改 OpenAPI JWT 认证（已独立运作）
- 不实现 "记住我" 功能

## Decisions

### D1: SPA 内登录页 vs 服务端渲染登录页

**选择**: Vue SPA 登录页（`/login` 路由）

**替代方案**: 保留 Django 模板登录页，未登录时全页面跳转

**理由**: SPA 体验一致，UI 统一，路由守卫统一控制认证状态。Django 模板登录页已删除。

### D2: CSRF 流程

**选择**: 复用 Django CSRF middleware 自动设置的 cookie

**流程**: `GET /init/` → Django 返回 401 + CSRF cookie → 前端登录页从 cookie 读取 token → `POST /account/login/` 携带 `X-CSRFToken` header

**替代方案**: `@csrf_exempt` 登录端点

**理由**: 保持 CSRF 保护。Django `CsrfViewMiddleware` 在所有响应（包括 401）上设置 cookie，无需额外端点。

### D3: 认证状态检测

**选择**: `window.username` 全局变量

**替代方案**: Vuex/Pinia state

**理由**: 现有代码大量依赖 `window.username`、`window.IS_ITSM_ADMIN` 等全局变量，保持一致。路由守卫在 app mount 前也需要检测状态。

### D4: Init 失败时仍然 mount app

**选择**: `getPlatformPreData` 失败时仍 `app.mount("#app")`

**替代方案**: 不 mount，等待重新请求

**理由**: 路由守卫需要 app 已 mount 才能工作。Init 401 时 mount app → 守卫检测到 `window.username` 为空 → 跳转 `/login`。

### D5: Cookie 前缀 `itsm_`

**选择**: `itsm_sessionid`、`itsm_csrftoken`

**替代方案**: 保持 `bkitsm_`

**理由**: 项目已不叫 "BK-ITSM" 在 PaaS 上运行，前缀应反映项目名称。

## Risks / Trade-offs

- **[Breaking] Cookie 名称变更** → 所有用户需重新登录。无迁移路径（旧 cookie 自动失效）
- **CSRF cookie 可能未设置** → `init/` 视图需确保不 `csrf_exempt`，且 `CsrfViewMiddleware` 在响应中设置 cookie。`ensure_csrf_cookie` 作为登录端点的保障
- **Vite dev 模式** CSRF cookie 域 → `localhost` 在 dev 和 proxy 中一致，无跨域问题
- **登出使用 fetch 而非 axios** → 因为 axios baseURL 是 `/api/`，登出端点在 `/account/logout/`。使用原生 fetch 避免 baseURL 问题
