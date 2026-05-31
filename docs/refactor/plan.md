# BK-ITSM 重构计划

## 已完成阶段

### Phase 1: 去蓝鲸依赖 → [归档](phase1-bk-decoupling/)

将 BK-ITSM 从蓝鲸 PaaS 平台完全解耦，使项目可独立部署运行。16 个子计划全部完成。

- 技术规格：[spec.md](phase1-bk-decoupling/spec.md)
- 16 个子计划：[plans/](phase1-bk-decoupling/plans/)
- 关键提交：`e1c87a87`
- 替代方案：blueapps → Django auth、IAM SDK → guardian、ESB → platform_client、bkstorages → django-storages、apigw_manager JWT → PyJWT

### Phase 2: 死代码与残余清理 → [归档](phase2-cleanup/)

清理 Phase 1 后的无引用代码、WeChat 通知系统、SOPS/DevOps 任务基础设施。

- 关键提交：`689d1ed9`, `25fd5cc7`, `0376e6b3`, `68704d97`
- SOPS/DevOps 完整移除（激进模式，含 SopsTask/SubTask 模型）
- ESB/apigw/bkchat stub → `itsm/component/platform_client/http.py`
- `itsm/helper/` app 解散，代码各归其位
- `config/integrations.py` 143→54 行
- 总计 ~130 文件，~11,000 行删除

### Phase 2.1: 持续清理

Phase 2 后发现的零散死代码清理。

- 删除 `core/` 包（`BkWSGIHandler` 及自定义 WSGI 入口）— 根目录 `wsgi.py` 已使用标准 Django WSGI，`core/` 无任何引用
- 删除死的 URL 路由 `itsm.plugin_service.urls`、middleware `HttpsMiddleware` / `ProfilerMiddleware` / `InstrumentProfilerMiddleware`
- 删除 `error_pages/`（模板不存在，handler 无效）、`common/context_processors.py`、`itsm/component/request_middlewares.py`
- 删除 `sync_saas_apigw.py` 及 `data/`（蓝鲸 API 网关同步残余）
- 删除 `Makefile`、`scripts/settings_saas.py`、`scripts/convert_yaml.py`、`test_script/`、`itsm/tests/runner.py`、`docs/itsm_nfs/`
- 清理 `requirements.txt` 移除 19 个未使用包（109→64 行）
- 清理 `misc_middlewares.py` 未使用 import、`PREFIX_KEY` 改用 `APP_CODE`
- 修正 `.pre-commit-config.yaml` Python 版本 3.11→3.13
- 移除 `config/i18n.py` 中无引用的 `LOCALEURL_USE_ACCEPT_LANGUAGE`
- `common/redis.py` 移除 `six.moves` import
- 全局移除 `six` 依赖（12 个文件），替换为 Python 3 原生等价物（`six.iteritems` → `.items()`、`six.string_types` → `str`、`six.with_metaclass` → `metaclass=` 等）
- 删除重复 `locale/zh-cn/`（与 `zh_CN` 内容相同）、`locale/cmd.md`（过时 PaaS i18n 笔记）
- 删除整个 `scripts/` 目录（旧版 PaaS CI 脚本、commit-msg 校验、过时文档）
- 前端 SOPS/DevOps 残余清理：删除 4 个 Vue 组件，清理 20+ 引用文件中的 `TASK-SOPS` 类型、store actions、palette 入口等（-1658 行）
- 全局移除 `from __future__ import`（251 个文件，含 migrations）
- 全局移除 `class Xxx(object):` Python 2 风格类声明（41 个文件）
- 清理 `itsm/component/utils/basic.py` 14 个死函数（913→630 行），清理未使用 import 和死常量
- 删除 9 个零引用工具文件（`utils/ago.py`、`auth.py`、`batch.py`、`bk_math.py`、`django_helper.py`、`local.py`、`patch_cache.py`、`robot.py`、`sandbox.py`）
- 删除 `data/sentinel.py`（Redis Sentinel 客户端，零引用）
- 删除 3 个零引用 DRF 子模块（`drf/mixins.py`、`drf/parsers.py`、`drf/routers.py`）
- 删除 `WorkflowPipelineWrapper` 死类（`workflow/backend.py`），修复 5 个预存 `for ... in X):` 语法错误
- 删除 `frontend/pc/src/views/i18n_patch.py`（Python 2 脚本，已无法运行）
- 清理 `requirements.txt` 移除 2 个未使用包（`httplib2`、`pydantic`，64→62 行）

### P2-16: 继续清理
- 恢复误删的 `robot.py`（`trigger/action/components/automatic_announcement.py` 有活跃引用）
- 全局替换 `import mock` → `from unittest import mock`（23 个测试文件），移除 `mock==5.1.0` 依赖
- 删除 `utils/user_adapter.py`（零引用）、`component/generics.py`（零引用 DRF 异常处理器）
- 合并 `bunch.py` → `bk_bunch.py`（迁移唯一引用到 `bk_bunch.bunchify`）
- 清理 `requirements.txt` 移除 2 个未使用包（`factory_boy`、`xlrd`）

### P2-17: 移除废弃 Django 模型
- 删除 `WorkflowSnap`、`DefaultField`（workflow deprecated.py，已迁移至 WorkflowVersion）
- 删除 `OldSla`（service，已迁移至 sla app）
- 删除 `ServiceProperty`、`PropertyRecord`（service，legacy 属性系统）
- 删除 `CostomTab`（project，URL 已注释禁用）
- 清理对应的序列化器、视图、URL、admin、manager 迁移方法
- 创建 3 个 DROP TABLE 迁移（workflow/0053、service/0032、project/0008）

### P3: 迁移重置

删除全部历史迁移文件，从零生成干净的 `0001_initial.py`，项目作为全新项目对待（需 DROP DATABASE + CREATE）。

- 删除 Pipeline 8 个子应用的 77 个历史迁移文件（2017-2021）
- 为 19 个应用生成全新 `0001_initial.py`（14 ITSM + 5 Pipeline）
  - `service` 因跨应用 FK 依赖自动拆分为 `0001_initial` + `0002_initial`
- 3 个未注册 Pipeline 子应用（`django_signal_valve`、`contrib.statistics`、`contrib.periodic_task`）不生成迁移
- `config/local_settings.py` 补充 `REDIS_*` 配置（`common/redis.py` 模块级引用需要）
- 无升级路径：已部署实例必须 DROP DATABASE 后重新 `migrate`

### P4: apps.py 清理

审计全部 23 个 `apps.py`，移除死代码、一次性迁移 handler、蓝鲸残余信号连接。22 个文件，删除 11,348 行。

- `task/apps.py`：删除空 `app_ready_handler`（仅 `pass`）
- `workflow/apps.py`：删除 `fix_migrate_error()`（旧迁移 hack，P3 后无用）
- `project/apps.py`：删除 `init_lesscode_project()`（蓝鲸低代码残余）
- `ticket/apps.py`：删除 `TicketComment.fix_comments()`（一次性数据迁移伪装成持久 handler）
- `postman/apps.py`：删除 uppercase system code 一次性迁移 handler
- `service/apps.py`：断开 `register_builtin_iam_service`、`register_builtin_bkbase_service` 信号连接
- 清理孤立代码：`service/managers.py`（init_iam_services、init_bkbase_services）、`workflow/managers.py`（init_iam_system、init_iam_default_workflow、init_bkbase_workflow）、`service/signals/handlers.py`（iam/bkbase handler 函数）
- 清理孤立常量：`BUILTIN_IAM_SERVICES`、`BUILTIN_BKBASE_SERVICES`、`BKBASE_CATALOG_KEY`
- 删除 `initials/workflow/iam_default.json`、`iam_user.json`、`bkbase/` 目录（8 个 JSON 文件）

### P5: 环境变量与配置清理

统一环境变量命名，删除蓝鲸 PaaS 残余配置垫片，补齐缺失的 `DATABASES` 定义。

- **删除 `config/env.py`** — 蓝鲸兼容垫片（`BK_PAAS_HOST`、`BK_URL`、`RUN_VER`、`RUN_MODE`），其内容分配到对应模块或直接删除
- **`APP_TOKEN` → `SECRET_KEY`** — `config/__init__.py` 不再从 `APP_TOKEN` 派生 `SECRET_KEY`，直接读取 `SECRET_KEY` 环境变量
- **补齐 `DATABASES`** — 提交代码中 `DATABASES` 配置从未定义（仅存在于 `local_settings.py` 和部署文档），现在正式写入 `config/database.py`
- **`BKAPP_*` / `BK_*` 环境变量统一重命名** — 28 个环境变量：
  - `BK_MYSQL_*` → `MYSQL_*`、`BKAPP_REDIS_*` → `REDIS_*`
  - `BKAPP_*` 业务前缀全部去掉（`BKAPP_ITSM_ADMIN` → `ITSM_ADMIN`、`BKAPP_BK_USER_WHITE_FIELDS` → `USER_WHITE_FIELDS` 等）
  - `BK_API_URL_TMPL` → `API_URL_TEMPLATE`、`BK_DOC_CENTER_HOST` → `DOC_CENTER_HOST`
  - `BKPAAS_BK_DOMAIN` → `APP_DOMAIN`、`BKPAAS_SHARED_RES_URL` → `SHARED_RES_URL`
- **删除死配置** — `RUN_MODE`、`APP_TOKEN`、`BK_PAAS_HOST`、`BK_CC_HOST`、`BK_JOB_HOST`、`BK_PAAS_ESB_HOST`、`BK_IAM_APP_CODE`、`IAM_ESB_PAAS_HOST`、`CALLBACK_AES_KEY`、`INIT_DEVOPS_TEMPLATE`、`TAPD_OAUTH_URL`、`BK_DESKTOP_URL`、`BK_STATIC_URL`、`ALLOW_CSRF`、`CUSTOM_TITLE`、`LOG_NAME`、`NEED_PROFILE`、`ENABLE_OTEL_TRACE`、`CELERYD_CONCURRENCY`
- **`config/default.py` 移除 `from config.env import *`** — 从 11 个子模块降为 10 个
- **代码清理**：
  - `ticket/models/misc.py` 中 `RUN_MODE[0]` 硬编码为 `"T"` 前缀
  - `ticket/tasks.py` 移除 `RUN_MODE` 引用
  - `component/decorators.py` 移除 `RUN_VER == "ieod"` 分支
  - `workflow/apps.py` 移除 `INIT_DEVOPS_TEMPLATE` 蓝盾初始化代码块及未使用 `settings` import
  - `sites/views.py` 模板上下文变量名统一（`BK_*` → 无前缀）
  - `pipeline/contrib/engine_admin/views.py` 模板上下文 `BKAPP_CSRF_COOKIE_NAME` → `CSRF_COOKIE_NAME`
- **更新 `.env.example`** — 全部使用新变量名，移除 IAM/APIGW 段，新增邮件和文档配置段
- **更新 `.github/workflows/django.yml`** — CI 环境变量同步重命名，移除 `RUN_ENV`、`APP_ID`、`APP_TOKEN`、`USE_IAM` 等死变量

### 验证状态

零蓝鲸硬依赖残留（blueapps、blueking、apigw_manager、bk_notice_sdk、bkstorages、iam SDK、auth_iam、esb、apigw、bkchat、helper、core — 全部归零）。

---

## 重构规则

1. **删除代码后必须清理未使用的 import** — 每次删除类/函数/变量后，检查文件中是否残留无引用的 import 语句，一并删除。
2. **删除代码后必须清理依赖** — 如果删除的代码是某个 pip 包的唯一消费者，同步从 `requirements.txt` 中移除该包。
3. **删除代码后必须清理配置** — 检查 `MIDDLEWARE`、`INSTALLED_APPS`、`CELERY_IMPORTS`、URL 路由、context_processors 等配置中是否有对已删除代码的引用，一并清理。
4. **迁移策略** — 项目已重置为单次 `0001_initial` 迁移，后续 schema 变更使用标准 `makemigrations`/`migrate`。已部署实例需 DROP DATABASE + CREATE，无升级路径。

---

## 待规划阶段

<!-- 在此添加新的重构计划 -->
