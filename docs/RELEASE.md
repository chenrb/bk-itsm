# Changelog

## [Version: 3.0.0] - 2026-05-31
【重构】完全解耦蓝鲸 PaaS 平台，支持独立部署
【重构】Python 3.13 + Django 6.0 + DRF 全栈升级
【重构】ESB/apigw/bkchat → platform_client HTTP 客户端
【重构】IAM SDK → guardian 权限框架
【重构】移除 blueapps、bkstorages、six 等遗留依赖
【重构】清理 SOPS/DevOps 任务基础设施、WeChat 通知系统
【重构】移除 6 个废弃 Django 模型（WorkflowSnap、DefaultField、OldSla、ServiceProperty、PropertyRecord、CostomTab）
【重构】前端 Vue 3 重构，移除 SOPS/DevOps 组件
