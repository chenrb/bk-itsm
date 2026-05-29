# BK-ITSM 去蓝鲸依赖重构计划

## 1. 背景与目标

BK-ITSM 当前深度耦合蓝鲸 PaaS 平台，核心依赖包括：

- **blueapps**：提供 Django 框架基础（settings、auth、middleware、Celery、WSGI）
- **iam**：提供基于蓝鲸 IAM 的权限系统
- **blueking**：提供 ESB（企业服务总线）SDK，所有外部服务通信的通道
- **weixin**：提供微信/企业微信登录和通知
- **apigw_manager**：提供 API 网关 JWT 认证
- **bk_notice_sdk**：蓝鲸通知 SDK
- **bkstorages**：蓝鲸存储后端（Ceph/BKRepo）

**目标**：在独立分支上完全去除蓝鲸依赖，使项目可独立部署运行，摆脱技术债。

**技术选型**：
| 领域 | 现有方案 | 替代方案 |
|------|----------|----------|
| 用户认证 | 蓝鲸统一登录（blueapps account） | Django 原生 auth + session |
| 权限控制 | 蓝鲸 IAM SDK | django-guardian 对象级权限 |
| 流程引擎 | pipeline（内嵌） | 保留不动（不依赖蓝鲸平台） |
| 通知系统 | 蓝鲸 CMSI（ESB 消息总线） | 抽象 Notifier 接口（邮件/SMS/Webhook 可插拔） |

---

## 2. 依赖侵入分析

### 2.1 侵入深度评估

| 组件 | 耦合等级 | 涉及文件数 | 替换难度 |
|------|----------|-----------|----------|
| blueapps 框架 | **致命** | 30+ | 极高 — 整个 Django 配置基础 |
| blueking ESB SDK | **高** | 15+ | 高 — 所有外部服务通信 |
| iam SDK + auth_iam | **高** | 60+（SDK 28+ 集成） | 高 — 全部权限模型 |
| weixin 模块 | **高** | 20+ | 中 — OAuth + 通知 |
| apigw_manager | **中** | 5 | 中 — JWT 认证层 |
| bk_notice_sdk | **低** | 2 | 低 — 纯 Django app 插件 |
| bkstorages | **低** | 1 | 低 — 标准存储后端替换 |
| adapter 适配层 | **中** | 15+ | 低 — 删除即可 |
| sops_proxy | **中** | 10+ | 低 — 删除即可 |
| business_rules | **低** | 10+ | 低 — 删除即可 |

### 2.2 blueapps 表面清单

blueapps 是最关键的依赖，它不是一个工具库，而是应用框架本身：

- `blueapps.conf.default_settings` — `from ... import *` 注入全部 Django settings
- `blueapps.core.wsgi.get_wsgi_application` — WSGI 入口
- `blueapps.core.celery.celery_app` — Celery 应用实例
- `blueapps.account.models.User` — 用户模型
- `blueapps.account.middlewares.*` — 3 个认证中间件
- `blueapps.account.decorators.login_exempt` — 10+ view 文件使用
- `blueapps.middleware.request_provider.RequestProvider` — 线程本地 request
- `blueapps.contrib.celery_tools.periodic.periodic_task` — 8 个 task 文件使用
- `blueapps.template.backends.mako.MakoTemplates` — 模板引擎
- `blueapps.opentelemetry.*` — OpenTelemetry 集成
- `blueapps.core.exceptions.middleware.AppExceptionMiddleware` — 异常处理

---

## 3. 分阶段执行计划

### Phase 1: 基础设施 — Settings / WSGI / Celery / 中间件

**目标**：应用可以 `python manage.py runserver` 启动，不再 import blueapps。

**工作项**：

1. 新建 `config/base_settings.py` — 显式定义所有 Django 基础配置
2. 重写 `config/default.py` — 替换 blueapps 通配 import，移除蓝鲸专属配置
3. 重写 `config/__init__.py` — 标准 Celery app，移除 RUN_VER
4. 重写 `wsgi.py` — 用 Django 原生 WSGI
5. 重写 `config/dev.py`、`config/stag.py`、`config/prod.py` — 移除 blueapps patch import
6. 简化 `settings.py` — 移除 weixin settings 动态 import
7. 更新 `requirements.txt` — 移除蓝鲸包，添加 django-guardian

**验证**：`python manage.py check` 无 import 错误

---

### Phase 2: 认证 — 自定义 User 模型 + Django Session Auth

**目标**：用户可以登录/登出，API 认证正常。

**工作项**：

1. 新建 `itsm/component/users/` app — User 模型（对齐 blueapps User 字段）、login/logout 视图
2. 注册 User 模型 — `AUTH_USER_MODEL = "users.User"`
3. 替换 `login_exempt` — 在 `itsm/component/decorators.py` 添加兼容实现，更新 10 个 view 文件的 import
4. 替换 User 模型引用 — `get_user_model()` 替代 `blueapps.account.models.User`
5. 更新 `urls.py` — 替换 account URL

**验证**：`python manage.py migrate` 成功，`createsuperuser` 可用，登录/登出正常

---

### Phase 3: 移除 ESB / BlueKing 通信层

**目标**：移除所有外部蓝鲸服务通信代码。

**工作项**：

1. 删除目录：`blueking/`、`itsm/component/esb/`、`adapter/`、`itsm/component/bkoauth/`、`itsm/component/auto_register/`、`itsm/plugin_service/`
2. 新建 `itsm/component/utils/user_adapter.py` — 基于本地 User 的用户查询
3. 处理 `client_backend` 消费方 — 通知 → Phase 5，用户查询 → user_adapter，CMDB/SOPS → stub 或移除
4. 移除 pipeline_plugins 中的蓝鲸集成组件（bk_sops、bk_devops、bk_plugin）

**验证**：`grep -r "blueking\|from itsm.component.esb\|from adapter" --include="*.py"` 零匹配

---

### Phase 4: 权限 — 用 django-guardian 替代 IAM

**目标**：所有 API 权限检查走 django-guardian + Django 内置权限。

**工作项**：

1. 删除目录：`iam/`（60 文件）、`itsm/auth_iam/`（28 文件）
2. 重写 `itsm/component/drf/permissions.py` — IAM 类 → guardian 类
3. 重写 `itsm/component/generics.py` — 移除 IAM 异常处理
4. 更新业务层权限调用 — ticket/workflow/service/project 中的 IAM 调用
5. 移除 IAM 配置 — USE_IAM、IAM_SKIP_AUTH、BK_IAM_* 变量
6. 删除 `itsm/component/constants/iam.py`

**验证**：`grep -r "from iam " --include="*.py" itsm/` 零匹配

---

### Phase 5: 通知系统 — 抽象 Notifier 接口

**目标**：通知不再依赖蓝鲸 CMSI。

**工作项**：

1. 新建 `itsm/component/notifiers/` — BaseNotifier ABC + EmailNotifier + SmsNotifier + WebhookNotifier
2. 重写 `itsm/component/notify.py` — 通过 NotifierRegistry 分发
3. 删除 `weixin/` 模块
4. 清理 weixin 相关 settings 和 URL

**验证**：无 `client_backend.cmsi` 调用残留，Email notifier 可发送

---

### Phase 6: 清理残余依赖

**目标**：零蓝鲸代码残留。

**工作项**：

1. 删除目录：`sops_proxy/`、`business_rules/`、`itsm/component/apigw/`、`itsm/component/bkchat/`、`platform_config/`
2. 替换 `periodic_task` 装饰器（8 个 task 文件）
3. 替换其他 blueapps 引用（logger、settings proxy、exceptions）
4. 重写 OpenAPI 认证 — 移除 apigw_manager，用 PyJWT 直接实现
5. 更新文件存储 — bkstorages → Django FileSystemStorage 或 django-storages
6. 删除配置文件：`app.yml`、`app_desc.yaml`、`Procfile`、`Aptfile`

**验证**：`grep -rE "blueapps|blueking|apigw_manager|bk_notice|bkstorages|from iam |RUN_VER" --include="*.py"` 零匹配

---

### Phase 7: 最终验证

**工作项**：

1. 完整 import 审计 — grep 确认零残留
2. 更新/移除引用已删除模块的测试文件
3. 空 DB 上 `python manage.py migrate` 成功
4. `python manage.py test itsm.tests` 通过
5. 更新 CLAUDE.md 文档

---

## 4. 文件变更汇总

### 4.1 需删除的目录（14 个）

| 目录 | 文件数 | 说明 |
|------|--------|------|
| `blueking/` | ~50 | ESB SDK |
| `iam/` | ~60 | IAM SDK |
| `weixin/` | ~30 | 微信集成 |
| `sops_proxy/` | ~10 | SOPS 代理 |
| `business_rules/` | ~10 | 业务规则 |
| `adapter/` | ~15 | 环境适配 |
| `itsm/auth_iam/` | ~28 | IAM 集成 |
| `itsm/component/esb/` | 3 | ESB 封装 |
| `itsm/component/bkoauth/` | ~5 | OAuth |
| `itsm/component/auto_register/` | ~5 | 自动注册 |
| `itsm/component/apigw/` | ~10 | API Gateway |
| `itsm/component/bkchat/` | ~5 | BKChat |
| `itsm/plugin_service/` | ~10 | 插件服务 |
| `platform_config/` | ~10 | 平台配置 |

### 4.2 需新建的文件（11 个）

| 文件 | 说明 |
|------|------|
| `config/base_settings.py` | 独立 Django 基础配置 |
| `itsm/component/users/__init__.py` | 用户 app |
| `itsm/component/users/models.py` | 自定义 User 模型 |
| `itsm/component/users/apps.py` | AppConfig |
| `itsm/component/users/views.py` | 登录/登出视图 |
| `itsm/component/users/urls.py` | 认证 URL |
| `itsm/component/utils/user_adapter.py` | 本地用户查询 |
| `itsm/component/notifiers/base.py` | 通知抽象接口 |
| `itsm/component/notifiers/email.py` | 邮件通知 |
| `itsm/component/notifiers/sms.py` | 短信通知 |
| `itsm/component/notifiers/webhook.py` | Webhook 通知 |

### 4.3 需修改的高影响文件

| 文件 | 修改内容 |
|------|----------|
| `config/default.py` | 移除 blueapps 通配 import，重写 settings 基础 |
| `config/__init__.py` | 替换 Celery app，移除 RUN_VER |
| `config/dev.py` | 移除 blueapps patch import |
| `config/stag.py` | 移除 blueapps patch import |
| `config/prod.py` | 移除 blueapps patch import |
| `settings.py` | 移除 weixin settings import |
| `wsgi.py` | 用 Django WSGI |
| `urls.py` | 替换 account/notice URL |
| `requirements.txt` | 移除蓝鲸包，添加 django-guardian |
| `itsm/component/drf/permissions.py` | IAM → guardian 权限类 |
| `itsm/component/generics.py` | 移除 IAM 异常处理 |
| `itsm/component/notify.py` | 用新 notifier 接口 |
| `itsm/component/decorators.py` | 添加 login_exempt |
| `itsm/component/misc_middlewares.py` | 移除 RUN_VER/weixin 逻辑 |
| 10 个 view 文件 | 替换 login_exempt import |
| 8 个 task 文件 | 替换 periodic_task import |
| `itsm/openapi/authentication/backend.py` | 移除 apigw_manager |
| `itsm/ticket/permissions.py` | 移除 IamRequest |
| `itsm/iadmin/apps.py` | 移除 blueapps User |

---

## 5. 风险与注意事项

1. **数据迁移**：从 `account_user`（blueapps）迁移到新的 `users_user` 表，需数据迁移脚本
2. **权限映射**：IAM 的 37 个 action + 22 个 resource 需要映射到 guardian 的 permission 模型
3. **Pipeline 插件**：bk_sops/bk_devops/bk_plugin 三个集成组件移除后，使用这些节点的存量流程会报错，需要兼容处理
4. **前端适配**：前端 `ajax.js` 中的 401/403/499 处理逻辑需要适配新的权限响应格式（499 不再存在）
5. **测试覆盖**：大量测试文件引用了 `blueapps.core.celery.celery.app`，需批量更新
