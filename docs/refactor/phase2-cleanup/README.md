# Phase 2: 死代码与残余清理

完成 Phase 1 的 16 个子计划后，进一步清理无引用代码和重构后遗留。

## 提交记录

| 提交 | 描述 | 变更量 |
|------|------|--------|
| `689d1ed9` | 删除死代码、WeChat 通知、SOPS/DevOps、未用 app | 97 files, +73/-7159 |
| `25fd5cc7` | 补充 task views 中 SOPS 残余清理 | 1 file |
| `0376e6b3` | ESB→platform_client, apigw/bkchat stub 删除, helper 清理 | 34 files, +161/-1931 |
| `68704d97` | 解散 itsm/helper app, 代码归位 | 12 files, +24/-89 |

## 具体变更

### P2-01/02: 修复关键 bug
- 修复 `auth_iam` import 崩溃、死 URL 路由、缺失 settings、前端 build 脚本

### P2-03: 删除 SOPS/DevOps gateway 端点 (~450 行)
- 从 `itsm/gateway/views.py` 和 `urls.py` 移除所有 SOPS 代理和 DevOps 流水线函数

### P2-04: 清理 `config/integrations.py`
- 143 行 → 54 行，移除 SOPS/APIGW/BKCRYPTO/BKChat/TAPD/IEOD 等死配置
- 新增 `PLATFORM_API_BASE_URL` 环境变量

### P2-05: 移除未用 Django app
- 从 INSTALLED_APPS 移除 `django_mptt_admin`, `django_extensions`, `django_signal_valve`(顶层), `data_migration`, `itsm/notice/`
- 删除 `django_signal_valve/`, `data_migration/`, `itsm/notice/` 目录

### P2-06: WeChat 清理
- 移除 WEIXIN 通知渠道（常量、触发器、前端组件）
- `TICKET_NOTIFY_HOST` → `FRONTEND_URL`
- 删除 `frontend/weixin/` 目录

### P2-07: SOPS/DevOps 完整移除（激进模式）
- 删除 `SopsTask`/`SubTask` 模型及 ~220 行
- 删除 `itsm/task/tasks.py` 中 sops_task_poller/devops_task_poller (~438 行)
- 删除 pipeline 组件 `sops_task.py`, `devops_task.py`
- 前端删除 sopsTemplate.vue, devopsTemplate.vue
- DB 常量 `TASK_SOPS_STATE`/`TASK_DEVOPS_STATE` 保留（带 deprecated 注释）以兼容已有数据

### P2-08: 死文件清理
- 删除 `celery_statsd.py`, `monitors/`, `common/shortuuid.py`, `common/decorators.py`, `common/middlewares.py`

### P3: ESB/apigw/bkchat stub 替换
- `itsm/component/esb/` → `itsm/component/platform_client/http.py`（基于 `requests` 的 HTTP 客户端）
- 删除 `itsm/component/apigw/` (5 files) 和 `itsm/component/bkchat/` (3 files)
- 所有消费方改为 `from itsm.component.platform_client.http import client_backend, bk`

### P4: itsm/helper app 解散
- `AutoSchedules` → `itsm/ticket/schedule_monitor.py`
- `time_this_function` → `common/utils.py`
- `check_permission_success` → `config/pipeline.is_superuser`（内联）
- 从 INSTALLED_APPS、CELERY_IMPORTS、URL 路由中移除
- 删除 `itsm/helper/` 目录

## 验证结果

最终 import 审计 — 零残留硬依赖：

| 模式 | 结果 |
|------|------|
| `from blueapps` | 零 |
| `from blueking` | 零 |
| `from apigw_manager` | 零 |
| `from bk_notice_sdk` | 零 |
| `from bkstorages` | 零 |
| `from iam` (SDK) | 零 |
| `from itsm.auth_iam` | 零 |
| `from itsm.component.esb` | 零 |
| `from itsm.component.apigw` | 零 |
| `from itsm.component.bkchat` | 零 |
| `from itsm.helper` | 零 |

### P2-09: 删除 `core/` 包
- 删除 `core/__init__.py`、`core/handler/__init__.py`、`core/handler/wsgi.py`、`core/wsgi.py`
- `BkWSGIHandler`（自定义 WSGI handler，处理蓝鲸 PaaS 子路径部署）不再被引用
- 根目录 `wsgi.py` 已使用标准 `django.core.wsgi.get_wsgi_application`

### P2-10: 死代码、死依赖、死配置全面清理
- 删除死的 URL 路由 `itsm.plugin_service.urls`、middleware `HttpsMiddleware` / `ProfilerMiddleware` / `InstrumentProfilerMiddleware`
- 删除 `error_pages/`（模板不存在，handler 无效）、`common/context_processors.py`、`itsm/component/request_middlewares.py`
- 删除 `sync_saas_apigw.py` 及 `data/`、`Makefile`、`scripts/`（整个目录）、`test_script/`、`itsm/tests/runner.py`、`docs/itsm_nfs/`
- 清理 `requirements.txt` 移除 19 个未使用包（109→64 行），升级 `django-celery-beat` 2.8.1→2.9.0、`django-timezone-field` 5.1→7.2.1、`RestrictedPython` 8.0→8.2 以兼容 Django 6.0
- 修正 `.pre-commit-config.yaml` Python 版本 3.11→3.13
- 移除 `config/i18n.py` 中无引用的 `LOCALEURL_USE_ACCEPT_LANGUAGE`

### P2-11: 移除 six 依赖
- 全局替换 `six` 为 Python 3 原生等价物，涉及 12 个文件
- `six.iteritems` → `.items()`、`six.string_types` → `str`、`six.integer_types` → `int`、`six.text_type` → `str`、`six.with_metaclass` → `metaclass=`、`six.moves.*` → builtin

### P2-12: 前端 SOPS/DevOps 残余清理
- 删除 4 个 SOPS Vue 组件（sopsDevopsTask、sopsNode、sopsNodeLog、sopsNodeInfo）
- 清理 20+ 引用文件中的 `TASK-SOPS` 类型过滤器、store actions、palette 入口、组件注册
- 删除重复 `locale/zh-cn/`、`locale/cmd.md`

### P2-13: 移除 Python 2 兼容代码
- 全局移除 `from __future__ import` 语句（251 个文件，含所有 migrations）
- 全局移除 `class Xxx(object):` Python 2 风格类声明，改为 `class Xxx:`（41 个文件）
- 涉及 `business_rules/`、`common/`、`itsm/` 下所有子模块

### P2-14: 清理 `basic.py` 死函数
- `itsm/component/utils/basic.py` 913→630 行（-295 行）
- 移除 14 个零外部调用的死函数：`time_delta`、`index_of_list`、`safe_cast`、`duplicate_check`、`safe_remove`、`deep_getattr`、`parse_color`、`log_parser`、`strftime_local`、`dict_to_choices`、`reverse_dict`、`tuple_to_namedtuple`、`rmtree`、`ansi_escape`、`jsonschema_validate`、`get_function_name`、`convert_bytes_to_str`
- 清理 8 个未使用 import（`inspect`、`os`、`posixpath`、`stat`、`Counter`、`reduce`、`jsonschema.validate`、`ParamError`）
- 清理 4 个死常量（`COLOR_REMOVE`、`CLEAR_COLOR_RE`、`LINE_BREAK_RE`、`IPV4_RE`）
- 移除对应的 2 个死测试方法（`test_safe_cast`、`test_duplicate_check`）

### P2-15: 死工具文件全面清理
- 删除 9 个零引用 `itsm/component/utils/` 工具文件：`ago.py`、`auth.py`、`batch.py`、`bk_math.py`、`django_helper.py`、`local.py`、`patch_cache.py`、`robot.py`、`sandbox.py`
- 删除 `itsm/component/data/sentinel.py`（Redis Sentinel 客户端，零引用）
- 删除 3 个零引用 DRF 子模块：`drf/mixins.py`、`drf/parsers.py`、`drf/routers.py`
- 删除 `WorkflowPipelineWrapper` 死类（`workflow/backend.py`），修复 5 个预存 `for ... in X):` 语法错误
- 删除 `frontend/pc/src/views/i18n_patch.py`（Python 2 脚本，已无法运行）
- 清理 `requirements.txt` 移除 2 个未使用包（`httplib2`、`pydantic`）

### P2-16: 继续清理
- 恢复误删的 `robot.py`（`automatic_announcement.py` 有活跃引用）
- 全局替换 `import mock` → `from unittest import mock`（23 个测试文件），移除 `mock==5.1.0`
- 删除 `utils/user_adapter.py`（零引用）、`component/generics.py`（零引用 DRF 异常处理器）
- 合并 `bunch.py` → `bk_bunch.py`，迁移唯一引用
- 清理 `requirements.txt` 移除 `factory_boy`、`xlrd`

## 总影响

| 指标 | 数值 |
|------|------|
| 删除文件 | ~148+ |
| 删除代码行 | ~13,800+ |
| 删除目录 | ~20+ |
| 删除 Django app | 7 个 (auth_iam, notice, helper, + 3 未用第三方) |
| 删除 DB 表 | 2 个 (task_sops_task, task_sub_task) |
