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

### P6: 启动流程健壮性 + 数据库配置补齐

修复 `python manage.py runserver` / `migrate` 启动链路中的实际问题，消除强制依赖 `local_settings.py` 的状况。

- **`config/database.py`：数据库配置正式写入**
  - Redis 配置提供默认值（`localhost:6379`），不再依赖 `IS_USE_REDIS` 条件分支
  - 移除 `DatabaseCache` 回退路径，Redis 为唯一缓存后端
  - 数据后端配置（`ITSM_DATA_BACKEND`、`PIPELINE_DATA_BACKEND`）不再条件分支
  - 新增 `REDIS` 字典（host/port/password/mode/db），替代 `iadmin/apps.py` 中的运行时拼接
  - `DEFAULT_AUTO_FIELD = "django.db.models.AutoField"` 补齐 Django 6 要求

- **`itsm/iadmin/apps.py`：删除运行时 REDIS 拼接**
  - 移除 `ready()` 中从 `os.environ` 读取 Redis 配置并动态注入 `settings.REDIS` 的代码
  - Redis 配置已在 `config/database.py` 静态定义

- **Pipeline apps.py 错误处理改进**
  - `pipeline/apps.py`：Redis 连接失败从 `error` 降为 `warning`，提示检查 Redis 服务
  - `pipeline/component_framework/apps.py`：`ProgrammingError`/`OperationalError` 从 `exception` 降为 `warning`，引导执行 `migrate`
  - `pipeline/engine/models/function.py`：function_switch 初始化捕获 DB 异常，`logger` 改用 `__name__`，异常日志用 `logger.exception`
  - `pipeline/variable_framework/apps.py`：同上，首次迁移异常从 `exception` 降为 `warning`

- **`itsm/component/dlls/autodiscover.py`：数据库未就绪时优雅降级**
  - `autodiscover_items`：捕获 `ProgrammingError`/`OperationalError`，输出一次 warning 后跳过
  - `autodiscover_collections`：同上
  - f-string 改为 `%s` 格式化（logger 最佳实践）

- **其他修复**
  - `itsm/role/models.py`：`UserRole.members`/`owners` 从 `CharField(max_length=LEN_XX_LONG)` 改为 `TextField`，解决 MySQL 行大小限制问题（TODO: 应改为 ManyToManyField）
  - `itsm/trigger/action/core/component.py`：移除 `CallableChoiceIterator` import，改用 `callable()` 判断
  - `itsm/workflow/utils.py`：`get_notify_type_choice` 捕获所有异常回退到默认值

### P16: post_migrate 初始化重构

将 7 个 app 的 9 个 `post_migrate` handler 中的初始化逻辑集中到管理命令 `init_builtin_data`，让 `migrate` 回归纯粹的 schema 迁移。

- **新建管理命令** `itsm/iadmin/management/commands/init_builtin_data.py`
  - 9 个初始化模块按依赖顺序执行：role → project → iadmin → workflow → service → ticket_status → sla → superuser → version_log
  - 支持 `--app`（指定模块）、`--skip`（跳过模块）、`--list`（列出模块）
- **重构 signal handlers** — `itsm/service/signals/handlers.py`：提取 `init_builtin_approve_service()`、`init_builtin_services_from_files()` 为无 signal 参数的普通函数，原 `register_builtin_*` 保留为薄包装
- **移除 post_migrate** — 7 个 `apps.py`（iadmin、service、role、project、ticket_status、sla、workflow）删除所有 `post_migrate.connect()` 和 handler 函数
- **首次部署流程**：`migrate` → `init_builtin_data`

### 验证状态

- `python manage.py check` 通过（0 issues，0 warnings）
- `python manage.py migrate` 不再触发任何初始化逻辑
- `python manage.py init_builtin_data` 执行全部内置数据初始化
- 零蓝鲸硬依赖残留（blueapps、blueking、apigw_manager、bk_notice_sdk、bkstorages、iam SDK、auth_iam、esb、apigw、bkchat、helper、core — 全部归零）
- MySQL 驱动：mysqlclient 2.2.8（PyMySQL 已完全移除）
- JSONField：Django 内置（jsonfield 已完全移除）
- DRF 缓存：本地 `cache_response`（drf-extensions 已完全移除）
- CI：GitHub Actions django.yml 已重写，等待 push 后验证

---

## 重构规则

1. **删除代码后必须清理未使用的 import** — 每次删除类/函数/变量后，检查文件中是否残留无引用的 import 语句，一并删除。
2. **删除代码后必须清理依赖** — 如果删除的代码是某个 pip 包的唯一消费者，同步从 `requirements.txt` 中移除该包。
3. **删除代码后必须清理配置** — 检查 `MIDDLEWARE`、`INSTALLED_APPS`、`CELERY_IMPORTS`、URL 路由、context_processors 等配置中是否有对已删除代码的引用，一并清理。
4. **迁移策略** — 项目已重置为单次 `0001_initial` 迁移，后续 schema 变更使用标准 `makemigrations`/`migrate`。已部署实例需 DROP DATABASE + CREATE，无升级路径。

---

### P7: UserRole M2M 重构

将 `UserRole.members`/`UserRole.owners` 从 TextField（逗号分隔用户名）迁移到 ManyToManyField，修正数据建模。

- **字段变更**：`TextField` → `ManyToManyField(settings.AUTH_USER_MODEL)`
- **查询重写**：`members__contains=dotted_name(username)` → `members__username=username`（6 个类方法）
- **`is_itsm_superuser`**：从 `get().members` 字符串匹配改为 `filter(members__username=).exists()`
- **`get_users_by_type`**（GENERAL 分支）：从逗号拼接改为 M2M 查询
- **`is_obj_manager`**：override `ObjectManagerMixin`，用 M2M filter 替代字符串 `in` 检查
- **`init_builtin_user_roles`**：`get_or_create` 后 `members.set()`/`owners.set()`
- **Serializer**：`CharField` → `ListField`，API 输出保持逗号分隔字符串（前端不变），新增 `create`/`update` 处理 M2M
- **Validator**：`list_by_separator()` → 直接取 list
- **Signal handler**：`UserRole.objects.create(**new_system)` → pop M2M 字段后 create + set
- **Ticket tasks**：`.members` → `.members.values_list("username", flat=True)`
- **迁移**：更新 `0001_initial.py`，删除 `0002`（TextField 临时迁移）
- **关键提交**：`0b7bf85a`

### P8: CI 修复 + PyMySQL 替换

修复长期中断的 CI 流水线，并将 MySQL 驱动从 PyMySQL 切换到 mysqlclient。

- **CI 重写**（`.github/workflows/django.yml`）
  - 删除对已删除文件 `scripts/workflows/bk_ci.sh` 的引用，内联所有步骤
  - 升级 actions 版本（checkout v3→v4, setup-python v4→v5）
  - 清理 P5 后残留的旧环境变量（`RUN_ENV`、`APP_ID`、`APP_TOKEN`、`USE_IAM` 等）
  - 新增 Redis 服务容器
- **`.env.example`**：Redis 段从"可选"改为"必选"，默认值取消注释
- **PyMySQL → mysqlclient**
  - Django 6.0 要求 `mysqlclient >= 2.2.1`，PyMySQL 报版本 `1.4.6` 不兼容
  - `settings.py`：删除 `pymysql.install_as_MySQLdb()` 及版本 patch（3 行）
  - `requirements.txt`：`PyMySQL==1.1.1` → `mysqlclient==2.2.8`
  - 不再需要任何版本欺骗 hack
- **关键提交**：`9d349a5d`（CI + env）, `fdc0fdd2`（mysqlclient）

### P9: 去第三方 JSONField + DRF 缓存依赖

移除 `jsonfield` 和 `drf-extensions` 两个第三方包，改用 Django 内置等价实现。

- **`jsonfield` → `django.db.models.JSONField`**（20 个 model 文件）
  - `jsonfield.JSONField` → `models.JSONField`（Django 3.1+ 内置）
  - `jsonfield.JSONCharField` → `models.JSONField`（去掉 `max_length`，MySQL 原生 JSON 列有自动校验）
  - 清理所有 `import jsonfield` / `from jsonfield import JSONField`
- **`default` 值 callable 化**（消除 `fields.E010` 警告）
  - `default=EMPTY_LIST`（即 `[]`）→ `default=list`
  - `default=EMPTY_DICT`（即 `ConstantDict({})`）→ `default=dict`
  - 非空默认值（`DEFAULT_FLOW_CONDITION`、`EMPTY_VARIABLE`、`revoke_config`、`extras` 等）→ 模块级工厂函数（`_default_xxx`）
  - Django migration serializer 不支持 lambda，必须用模块级函数
- **`drf-extensions` → 本地 `cache_response` 装饰器**
  - `itsm/component/cache_keys.py` 新增 `cache_response`，行为与 drf-extensions 等价：
    - miss 时：`finalize_response` → `render()` → 缓存 `(rendered_content, status_code, headers)` 三元组
    - hit 时：直接构造 `HttpResponse` 返回，跳过序列化和渲染
    - 默认不缓存错误响应（`status >= 400`）
  - `itsm/ticket/views/ticket.py`：import 改为本地模块
- **迁移重置**：19 个 `0001_initial.py` 全部重新生成（14 ITSM + 5 Pipeline）
- **`requirements.txt`**：移除 `jsonfield==3.2.0`、`drf-extensions==0.7.1`

### P10: 依赖审计 + 版本升级

逐包审计 `requirements.txt` 全部依赖，移除无直接引用的包，升级全部包至最新兼容版本。

- **移除 `django-multiselectfield`** — P2-17 删除 `PropertyRecord` 模型后残留 import，零活跃引用
- **移除 `Werkzeug`** — Django 间接依赖，项目代码无直接 import，无需显式声明
- **版本升级**（全部升至截至 2026-06 的最新兼容版本）：
  - `mysqlclient` 2.2.7→2.2.8, `MarkupSafe` 2.1.5→3.0.3, `Mako` 1.3.2→1.3.12
  - `requests` 2.32.4→2.34.2, `python-json-logger` 2.0.7→4.1.0, `whitenoise` 6.8.2→6.12.0
  - `django-cors-headers` 4.2.0→4.9.0, `pypinyin` 0.53.0→0.55.0, `humanize` 4.11.0→4.15.0
  - `jsonschema` 4.23.0→4.26.0, `django-mptt` 0.16.0→0.18.0, `pyparsing` 3.2.0→3.3.2
  - `redis` 5.0.3→8.0.0, `mistune` 3.0.2→3.2.1, `gevent` 26.4.0→26.5.0
  - `gunicorn` 23.0.0→26.0.0, `pytz` 2024.2→2026.2, `typing-extensions` 4.13.2→4.15.0
  - `cryptography` 46.0.7→48.0.0, `pyCryptodome` 3.20.0→3.23.0, `jmespath` 1.0.1→1.1.0

---

## 待规划阶段

<!-- 在此添加新的重构计划 -->

### P11: WorkflowVersion M2M owners 创建修复

`create_version()` 在 `WorkflowVersion.objects.create(**data)` 中直接传 `owners`（list），但 P7 已改为 ManyToManyField，导致 `TypeError: Direct assignment to the forward side of a many-to-many set is prohibited`。

- 从 `data` 中 `pop("owners", [])`
- `create()` 后 `version.owners.set(User.objects.filter(username__in=owners))`

### P12: DictData 初始化修复

`DictData.create_builtin_dicts_data()` 遍历 dict 时 `for k, v in data_dict` 缺少 `.items()`，导致 `ValueError: too many values to unpack`。

- `for k, v in data_dict` → `for k, v in data_dict.items()`

### P13: distutils 移除

Python 3.13 已删除 `distutils` 模块，`copy_tree` 引用导致 `No module named 'distutils'` 错误。

- `itsm/workflow/managers.py`、`itsm/ticket/managers.py`：`from distutils.dir_util import copy_tree` → `from shutil import copytree`
- `copy_tree(old_path, new_path)` → `copytree(old_path, new_path, dirs_exist_ok=True)`

### P14: 去除 CMSI 远程调用 + SMS 评价功能

去除蓝鲸 CMSI 消息通知 API 调用，通知类型改为本地常量管理。完整删除 SMS 短信评价功能。

- `init_notify_type_choice()` 直接返回 `NOTIFY_TYPE_CHOICES`，不再调用 `client_backend.cmsi.get_msg_type()`
- 删除 `NOTIFY_TYPE_MAPPING` 常量、CMSI 远程系统定义
- 删除 `SMS_COMMENT_SWITCH` 功能开关及全局设置 UI
- 删除 `post_comment`/`send_sms` 视图、`sms_comment_validate`/`sms_invite_validate` 验证器
- 删除 `IS_USE_INVITE_SMS`、`TICKET_INVITE_SMS_COUNT` 配置
- 前端：删除短信评价 radio/template/方法，简化 `sendEmail()`

### P15: 去除蓝鲸业务 (bk_biz_id)

完整移除蓝鲸 CMDB 业务绑定功能，包括 `bk_biz_id` 字段、`is_biz_needed` 开关、CMDB 处理人类型。

- **常量**：删除 `DEFAULT_BK_BIZ_ID`、`FIELD_BIZ`、`DEFAULT_API_INSTANCE`、CMDB from `PROCESSOR_CHOICES`/`ROLE_CHOICES`
- **模型**：删除 `Ticket.bk_biz_id`、`Status.bk_biz_id`、`Workflow/WorkflowVersion.is_biz_needed`，更新 0001_initial 迁移
- **处理人解析**：`get_users_by_type()` 移除 `bk_biz_id` 参数，CMDB 类型返回空列表；删除 `get_app_list_by_user`、`get_cmdb_role_by_user`、`get_biz_choices`、`get_bk_business`、`update_bk_business`
- **Gateway**：删除 `get_app_list` 视图和 `cmdb/get_app_list/` URL 路由
- **Ticket 层**：清理 validators、serializers、managers、tasks、SQL queries 中所有 `bk_biz_id` 引用
- **Workflow 层**：清理 validators、serializers、views、managers 中 `is_biz_needed` 和 `FIELD_BIZ` 引用
- **Service/OpenAPI**：清理 `is_biz_needed` 和 `bk_biz_id` 处理
- **前端（29 文件）**：移除 `bk_biz_id` 搜索过滤、`is_biz_needed` 开关、`get_app_list` action、节点配置 CMDB 选项
- **初始数据（3 JSON 文件）**：清理 `bk_biz_id` 字段定义和 `is_biz_needed`/`biz_related` 属性
- **远程 API 初始化**：从 `iadmin/apps.py` 移除 `init_default_system()` 和 `init_default_remote_api()`
- 117 files, -3774/+1937 lines
