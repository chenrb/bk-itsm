# -*- coding: utf-8 -*-
"""Pipeline + RPC + Trigger + SLA 配置"""
PIPELINE_END_HANDLER = "itsm.ticket.handlers.pipeline_end_handler"
ENABLE_EXAMPLE_COMPONENTS = True

PRC_AUTO_DISCOVER_PATH = ["rpc.components"]

TRIGGER_AUTO_DISCOVER_PATH = ["action.components"]

INTERVAL_TICK_PERCENT = 0.01  # SLA任务后台更新频率: 1%

PIPELINE_ENGINE_ADMIN_API_PERMISSION = (
    "itsm.helper.permissions.check_permission_success"
)
