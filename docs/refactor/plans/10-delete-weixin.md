# Plan 10: 删除 weixin 模块 + 清理微信相关配置

> 前置条件：Plan 01-09 已完成
> 目标：移除所有微信/企业微信集成代码

## 1. 删除目录

| 目录 | 文件数 | 说明 |
|------|--------|------|
| `weixin/` | ~32 | 微信集成（models, views, middlewares, migrations） |
| `miniweixin/` | 如存在 | 小程序微信集成 |
| `frontend/weixin/` | - | 微信前端（独立 Vue 应用） |
| `static/weixin/` | - | 微信编译后静态资源 |
| `mako_templates/weixin/` | - | 微信 Mako 模板 |

```bash
rm -rf weixin/
rm -rf miniweixin/
rm -rf frontend/weixin/
rm -rf static/weixin/
rm -rf mako_templates/weixin/
```

## 2. 处理 import 失败的文件

### `itsm/component/notify.py`

- 移除 `from weixin.core.settings import WEIXIN_APP_EXTERNAL_HOST`
- 微信通知逻辑移除或用 Webhook 替代

### `itsm/component/constants/basic.py`

- 移除微信相关常量

### `itsm/sla/models/policy.py`

- 检查是否有微信相关引用，移除

### `config/default.py`

- 确认已移除 `weixin.core` 和 `weixin` 的 INSTALLED_APPS 条目（Plan 02 应已处理）
- 确认已移除 weixin middleware（Plan 02 应已处理）
- 确认已移除 weixin context_processors（Plan 02 应已处理）
- 移除 `WX_QY_AGENTID`, `WX_QY_CORPSECRET`, `WX_USER` 配置
- 移除 `OUT_LINK` 配置
- 移除 `WEIXIN_APP_EXTERNAL_SHARE_HOST`, `TICKET_NOTIFY_HOST` 微信链接配置

### `settings.py`

- 确认已移除 weixin settings import（Plan 03 应已处理）

### `urls.py`

- 检查是否有 weixin URL 路由，移除

## 3. 清理微信相关环境变量

从文档/配置中移除：
- `BKAPP_USE_WEIXIN`
- `BKAPP_IS_QY_WEIXIN`
- `BKAPP_WEIXIN_APP_ID`
- `BKAPP_OUT_LINK`
- `BKAPP_WX_QY_AGENTID`
- `BKAPP_WX_QY_CORPSECRET`
- `BKAPP_WX_USER`

## 验证

```bash
ls weixin/ miniweixin/ 2>&1
# 应显示 "No such file or directory"

grep -rn "from weixin\|import weixin" --include="*.py" itsm/
grep -rn "from weixin\|import weixin" --include="*.py" config/
# 均应返回零匹配
```
