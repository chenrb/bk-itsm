# BK-ITSM 去蓝鲸依赖重构计划

## 概述

将 BK-ITSM 从蓝鲸 PaaS 平台解耦，使项目可独立部署运行。详细技术规格见 [spec.md](spec.md)。

## 依赖关系图

```
01-base-infra ──→ 02-config-default ──→ 03-settings-and-env ──→ 04-user-model ──→ 05-login-exempt
   ✅                ✅                    ✅                                              │
                                                                                        ↓
                                                                     06-delete-esb ──→ 07-user-adapter
                                                                                        │
                                                                     08-delete-iam ──→ 09-permission-guardian
                                                                                        │
                                                                     10-delete-weixin ─→ 11-notifier-system

                  12-celery-periodic-tasks
                  13-openapi-auth-and-storage
                  14-delete-residual ──→ 15-update-tests ──→ 16-final-verification
```

## 子计划列表

| # | 名称 | 核心工作 | 状态 |
|---|------|----------|------|
| 01 | [基础设施](plans/01-base-infra.md) | base_settings.py、config/\_\_init\_\_.py、wsgi.py | ✅ |
| 02 | [拆分 config/default.py](plans/02-config-default.md) | 按 13 个配置类别拆分为子模块 | ✅ |
| 03 | [settings.py + 环境配置](plans/03-settings-and-env.md) | 简化 settings.py，删除 dev/stag/prod.py | ✅ |
| 04 | [User 模型](plans/04-user-model.md) | 创建自定义 User 模型、登录视图、URL 配置 | ✅ |
| 05 | [login_exempt + User 引用](plans/05-login-exempt-and-user-refs.md) | 替换 12 个文件的 blueapps account import | ✅ |
| 06 | [删除 ESB/通信层](plans/06-delete-esb.md) | 删除 blueking/、adapter/ 等 6 个目录 | ✅ |
| 07 | [user_adapter](plans/07-user-adapter.md) | 创建本地用户查询接口 | ✅ |
| 08 | [删除 IAM](plans/08-delete-iam.md) | 删除 iam/、auth_iam/ 目录 | ✅ |
| 09 | [权限系统 guardian](plans/09-permission-guardian.md) | 重写 DRF 权限类 | ✅ |
| 10 | [删除 weixin](plans/10-delete-weixin.md) | 删除 weixin/、miniweixin/、前端微信应用 | ✅ |
| 11 | [通知系统](plans/11-notifier-system.md) | 创建 Notifier 抽象接口 | ✅ |
| 12 | [Celery 清理](plans/12-celery-periodic-tasks.md) | 替换 periodic_task 装饰器 | ✅ |
| 13 | [OpenAPI 认证 + 存储](plans/13-openapi-auth-and-storage.md) | 重写 JWT 认证，移除 bkstorages | ✅ |
| 14 | [残余清理](plans/14-delete-residual.md) | 删除 sops_proxy/ 等残余目录 | ✅ |
| 15 | [更新测试](plans/15-update-tests.md) | 更新测试 import，更新 CI | ✅ |
| 16 | [最终验证](plans/16-final-verification.md) | 完整 import 审计，migrate，运行测试 | ✅ |

## 总计

- **新建文件**：~15 个
- **修改文件**：~40 个
- **删除目录**：~14 个（~250 文件）
- **删除文件**：~5 个（配置文件）
- **预计总工时**：15-20 小时

## 技术选型

| 领域 | 现有方案 | 替代方案 |
|------|----------|----------|
| 用户认证 | 蓝鲸统一登录（blueapps account） | Django 原生 auth + session |
| 权限控制 | 蓝鲸 IAM SDK | django-guardian 对象级权限 |
| 流程引擎 | pipeline（内嵌） | 保留不动 |
| 通知系统 | 蓝鲸 CMSI（ESB 消息总线） | 抽象 Notifier 接口（邮件/SMS/Webhook） |
| 文件存储 | bkstorages（Ceph/BKRepo） | Django FileSystemStorage / django-storages |
| API 认证 | apigw_manager JWT | PyJWT 直接实现 |

---

## Phase 2: 死代码与残余清理

完成 Phase 1 的 16 个子计划后，进一步清理无引用代码和重构后遗留。

### 提交记录

| 提交 | 描述 | 变更量 |
|------|------|--------|
| `689d1ed9` | 删除死代码、WeChat 通知、SOPS/DevOps、未用 app | 97 files, +73/-7159 |
| `25fd5cc7` | 补充 task views 中 SOPS 残余清理 | 1 file |
| `0376e6b3` | ESB→platform_client, apigw/bkchat stub 删除, helper 清理 | 34 files, +161/-1931 |
| `68704d97` | 解散 itsm/helper app, 代码归位 | 12 files, +24/-89 |

### 具体变更

**P2-01/02: 修复关键 bug**
- 修复 `auth_iam` import 崩溃、死 URL 路由、缺失 settings、前端 build 脚本

**P2-03: 删除 SOPS/DevOps gateway 端点** (~450 行)
- 从 `itsm/gateway/views.py` 和 `urls.py` 移除所有 SOPS 代理和 DevOps 流水线函数

**P2-04: 清理 `config/integrations.py`**
- 143 行 → 54 行，移除 SOPS/APIGW/BKCRYPTO/BKChat/TAPD/IEOD 等死配置
- 新增 `PLATFORM_API_BASE_URL` 环境变量

**P2-05: 移除未用 Django app**
- 从 INSTALLED_APPS 移除 `django_mptt_admin`, `django_extensions`, `django_signal_valve`(顶层), `data_migration`, `itsm/notice/`
- 删除 `django_signal_valve/`, `data_migration/`, `itsm/notice/` 目录

**P2-06: WeChat 清理**
- 移除 WEIXIN 通知渠道（常量、触发器、前端组件）
- `TICKET_NOTIFY_HOST` → `FRONTEND_URL`
- 删除 `frontend/weixin/` 目录

**P2-07: SOPS/DevOps 完整移除**（激进模式）
- 删除 `SopsTask`/`SubTask` 模型及 ~220 行
- 删除 `itsm/task/tasks.py` 中 sops_task_poller/devops_task_poller (~438 行)
- 删除 pipeline 组件 `sops_task.py`, `devops_task.py`
- 前端删除 sopsTemplate.vue, devopsTemplate.vue
- DB 常量 `TASK_SOPS_STATE`/`TASK_DEVOPS_STATE` 保留（带 deprecated 注释）以兼容已有数据

**P2-08: 死文件清理**
- 删除 `celery_statsd.py`, `monitors/`, `common/shortuuid.py`, `common/decorators.py`, `common/middlewares.py`

**P3: ESB/apigw/bkchat stub 替换**
- `itsm/component/esb/` → `itsm/component/platform_client/http.py`（基于 `requests` 的 HTTP 客户端）
- 删除 `itsm/component/apigw/` (5 files) 和 `itsm/component/bkchat/` (3 files)
- 所有消费方改为 `from itsm.component.platform_client.http import client_backend, bk`

**P4: itsm/helper app 解散**
- `AutoSchedules` → `itsm/ticket/schedule_monitor.py`
- `time_this_function` → `common/utils.py`
- `check_permission_success` → `config/pipeline.is_superuser`（内联）
- 从 INSTALLED_APPS、CELERY_IMPORTS、URL 路由中移除
- 删除 `itsm/helper/` 目录

### 验证结果

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

### 总影响

| 指标 | 数值 |
|------|------|
| 删除文件 | ~130+ |
| 删除代码行 | ~11,000+ |
| 删除目录 | ~20+ |
| 删除 Django app | 7 个 (auth_iam, notice, helper, + 3 未用第三方) |
| 删除 DB 表 | 2 个 (task_sops_task, task_sub_task) |
