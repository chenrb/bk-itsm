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
| 05 | [login_exempt + User 引用](plans/05-login-exempt-and-user-refs.md) | 替换 12 个文件的 blueapps account import | 14 修改 | 1h |
| 06 | [删除 ESB/通信层](plans/06-delete-esb.md) | 删除 blueking/、adapter/ 等 6 个目录，移除 pipeline 蓝鲸组件 | 6 目录删除 | 1h |
| 07 | [user_adapter](plans/07-user-adapter.md) | 创建本地用户查询接口，替换 adapter API 调用 | 1 新建 + 4 修改 | 30min |
| 08 | [删除 IAM](plans/08-delete-iam.md) | 删除 iam/、auth_iam/ 目录，处理 import 失败的文件 | 2 目录删除 + 10 修改 | 1-2h |
| 09 | [权限系统 guardian](plans/09-permission-guardian.md) | 重写 DRF 权限类，更新业务层权限调用 | 2 重写 + 5 修改 | 2h |
| 10 | [删除 weixin](plans/10-delete-weixin.md) | 删除 weixin/、miniweixin/、前端微信应用 | 5 目录删除 | 30min |
| 11 | [通知系统](plans/11-notifier-system.md) | 创建 Notifier 抽象接口，重写 notify.py | 5 新建 + 1 重写 | 1-2h |
| 12 | [Celery 清理](plans/12-celery-periodic-tasks.md) | 替换 periodic_task 装饰器（8 文件），清理 Celery import | 8 修改 | 1h |
| 13 | [OpenAPI 认证 + 存储](plans/13-openapi-auth-and-storage.md) | 重写 JWT 认证，替换 bkstorages，移除 bk_notice | 2 重写 | 1h |
| 14 | [残余清理](plans/14-delete-residual.md) | 删除 sops_proxy/、business_rules/ 等 5 目录 + 蓝鲸配置文件 | 5 目录 + 4 文件删除 | 1h |
| 15 | [更新测试](plans/15-update-tests.md) | 更新测试文件 import，删除无效测试，更新 CI | 13 修改 + 4 删除 | 1h |
| 16 | [最终验证](plans/16-final-verification.md) | 完整 import 审计，migrate，运行测试，功能验证 | 验证 | 1h |

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
