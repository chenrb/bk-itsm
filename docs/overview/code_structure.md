# 代码目录

![](../resource/img/code_structure.png)


- config

  工程配置层，按功能拆分为子模块：`apps.py`（INSTALLED_APPS）、`celery.py`、`database.py`、`integrations.py`（平台集成）、`pipeline.py`（流程引擎+权限）、`env.py`（环境变量）等。`default.py` 聚合所有子模块。

- engine

  pipeline: 自研的流程引擎框架，主要包含任务流程编排页面和任务流程执行服务。
  sla_engine： sla调度引擎，主要用于工单计时统计。

- itsm

  业务逻辑层，包含流程管理、任务管理、服务管理，单据管理等模块。
  component：共享后端工具集，包括 DRF mixins、中间件、platform_client（HTTP 客户端）、常量、通知、任务工具。
  iadmin：提供系统配置，自定义通知等管理能力。
  gateway：第三方接口在itsm的二次封装层。
  openapi：itsm 网关接口提供层。
  postman：Api管理。
  role：角色管理。
  service：服务管理。
  sla：sla管理。
  project：项目管理。
  task: 任务管理。
  ticket: 单据管理（含 schedule_monitor.py 用于 pipeline 卡顿任务检测）。
  trigger: 触发器管理。
  workflow: 流程管理。

- web

  前端资源。

  frontend：pc 端 Vue 2 应用。

  static： 静态文件存放的目录。

  templates：包含首页和 django admin 需要的页面。

  locale：国际化翻译文件。
