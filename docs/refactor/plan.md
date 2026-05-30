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

### 验证状态

零蓝鲸硬依赖残留（blueapps、blueking、apigw_manager、bk_notice_sdk、bkstorages、iam SDK、auth_iam、esb、apigw、bkchat、helper、core — 全部归零）。

---

## 重构规则

1. **删除代码后必须清理未使用的 import** — 每次删除类/函数/变量后，检查文件中是否残留无引用的 import 语句，一并删除。
2. **删除代码后必须清理依赖** — 如果删除的代码是某个 pip 包的唯一消费者，同步从 `requirements.txt` 中移除该包。
3. **删除代码后必须清理配置** — 检查 `MIDDLEWARE`、`INSTALLED_APPS`、`CELERY_IMPORTS`、URL 路由、context_processors 等配置中是否有对已删除代码的引用，一并清理。

---

## 待规划阶段

<!-- 在此添加新的重构计划 -->
