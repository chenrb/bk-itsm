# BK-ITSM 重构计划 — 功能修复阶段

> 前一阶段（P1–P18，去蓝鲸依赖 + 死代码清理）已归档至 [plan-v1-decoupling.md](plan-v1-decoupling.md)

## 目标

修复重构后残留的功能性 bug，让应用可正常运行（前端页面可访问、API 可调用、工作流可运转）。

---

## 阶段总览

| 阶段 | 描述 | 状态 |
|------|------|------|
| F1 | 后端崩溃级 bug 修复 | 待开始 |
| F2 | 前端严重 bug 修复 | 待开始 |
| F3 | 前端死代码清理（stores/ 目录） | 待开始 |
| F4 | 集成验证 | 待开始 |

---

## F1: 后端崩溃级 bug 修复

### F1-1: 恢复 DRF 异常处理器

- **文件**：`config/web.py:18`
- **问题**：`EXCEPTION_HANDLER` 指向已删除的 `itsm.component.generics.exception_handler`，所有 API 错误变成 500
- **方案**：在 `itsm/component/` 下新建 `exception_handler.py`，实现标准 DRF 异常处理器；或改用 DRF 默认处理器

### F1-2: 修复 User.get_property() 调用

- **文件**：`itsm/sites/views.py:80`、`itsm/ticket/utils.py:226`
- **问题**：自定义 `User` 模型没有 `get_property()` 方法（蓝鲸 `BKUser` 遗留）
- **方案**：为 `User` 模型添加 `get_property(key)` 方法，从 `properties` JSONField 或类似字段中读取；或根据实际数据结构重写调用点

### F1-3: settings.APP_ID → APP_CODE

- **文件**：`itsm/ticket/utils.py:175`、`itsm/pipeline_plugins/components/collections/webhook.py:282`
- **问题**：`settings.APP_ID` 未定义
- **方案**：全局替换 `settings.APP_ID` → `settings.APP_CODE`

### F1-4: 补齐 settings.REDIS_INST

- **文件**：`itsm/component/data/redis_backend.py`、`itsm/monitor/healthz/check/redis.py`、`itsm/ticket/management/commands/init_ticket_sn.py`
- **问题**：`settings.REDIS_INST` 未定义
- **方案**：在 `config/database.py` 添加 `REDIS_INST` 配置（基于 `CACHES["default"]` 的 Redis 连接信息），或改用 `django-redis` 的 `get_redis_connection()`

### F1-5: 安装 business_rules 包

- **文件**：`itsm/ticket/rules/__init__.py:26`
- **问题**：`from business_rules import run_all` 但包未安装
- **方案**：`requirements.txt` 添加 `business_rules`

### F1-6: 修复 workflow/tasks.py 错误导入

- **文件**：`itsm/workflow/tasks.py:9`
- **问题**：`from itsm.workflow.models import Notify, settings, Project` — `Project` 不在 `workflow.models`
- **方案**：改为 `from itsm.project.models import Project`

### F1-7: 修复 CustomNotice 导入路径

- **文件**：`itsm/project/models/project.py:125`
- **问题**：`from itsm.sla.models import CustomNotice` — 应从 `itsm.iadmin.models` 导入
- **方案**：改为 `from itsm.iadmin.models import CustomNotice`

### F1-8: 修复 LEN_MIDDLE 导入路径

- **文件**：`itsm/openapi/ticket/validators.py:32`
- **问题**：`from itsm.ticket.models import TicketGlobalVariable, LEN_MIDDLE` — `LEN_MIDDLE` 不在 `ticket.models`
- **方案**：改为 `from itsm.component.constants import LEN_MIDDLE`，单独导入

---

## F2: 前端严重 bug 修复

### F2-1: 修复路由守卫内存泄漏

- **文件**：`frontend/pc/src/router/index.js:300-308`
- **问题**：`beforeEach` 内 `bus.on()` 从不 `off()`，每次导航注册新监听器
- **方案**：在 `beforeEach` 中先 `bus.off()` 再 `bus.on()`，或改用一次性监听 / 全局 flag

### F2-2: 修复 Vue 2 指令生命周期

- **文件**：`frontend/pc/src/directives/index.js`
- **问题**：`clickOut`、`anchor`、`cursorIndex`、`bkFocus` 使用 Vue 2 钩子（`bind`/`inserted`/`componentUpdated`）
- **方案**：映射到 Vue 3 等价钩子：`bind` → `beforeMount`，`inserted` → `mounted`，`componentUpdated` → `updated`

### F2-3: 修复 store/index.js 中 this.$t() 调用

- **文件**：`frontend/pc/src/store/index.js`（dataCheck 函数）
- **问题**：Vuex store 没有 `$t` 方法
- **方案**：直接 `import i18n from '@/i18n'` 后用 `i18n.global.t()` 代替 `this.$t()`

### F2-4: 修复 eventType/getAppList 不存在的问题

- **文件**：`frontend/pc/src/views/operation/home.vue:556`
- **问题**：`eventType` store 模块没有 `getAppList` action
- **方案**：确认后端对应接口是否存在，补充 action 或改用正确的 action 名称

---

## F3: 前端死代码清理

### F3-1: 删除 stores/ 目录（43 个未使用的 Pinia 文件）

- **文件**：`frontend/pc/src/stores/` 整个目录
- **问题**：Pinia 从未被使用，所有状态管理走 Vuex
- **方案**：删除 `stores/` 目录，移除 `main.js` 中的 `createPinia()` 和 `app.use(pinia)`，从 `package.json` 移除 `pinia` 依赖

---

## F4: 集成验证

- [ ] `python manage.py check` 通过
- [ ] `python manage.py migrate` 无错误
- [ ] `python manage.py init_builtin_data` 无错误
- [ ] `python manage.py runserver` 启动无报错
- [ ] 前端 `npm run dev` 启动，所有 `.vue` 文件编译通过
- [ ] 前端页面可正常访问（首页、工单列表、流程管理）
- [ ] API 请求返回正常（非 500）

---

## 重构规则

沿用 [plan-v1-decoupling.md](plan-v1-decoupling.md) 中的规则：

1. 删除代码后必须清理未使用的 import
2. 删除代码后必须清理依赖
3. 删除代码后必须清理配置
4. 迁移策略：标准 `makemigrations`/`migrate`
