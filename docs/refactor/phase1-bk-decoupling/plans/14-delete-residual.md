# Plan 14: 删除残余目录和配置文件

> 前置条件：Plan 01-13 已完成
> 目标：零蓝鲸代码/配置残留

## 1. 删除残余目录

| 目录 | 文件数 | 说明 |
|------|--------|------|
| `sops_proxy/` | ~10 | SOPS 反向代理 |
| `business_rules/` | ~10 | 业务规则引擎 |
| `platform_config/` | ~10 | 蓝鲸平台配置（MOA 等） |
| `itsm/component/apigw/` | ~10 | API Gateway 封装 |
| `itsm/component/bkchat/` | ~5 | BKChat 快速审批 |

```bash
rm -rf sops_proxy/
rm -rf business_rules/
rm -rf platform_config/
rm -rf itsm/component/apigw/
rm -rf itsm/component/bkchat/
```

## 2. 处理 import 失败

### `sops_proxy` 消费方

搜索引用：
```bash
grep -rn "sops_proxy\|from sops_proxy" --include="*.py"
```

如果有引用，移除对应 import 和 URL 路由。

### `business_rules` 消费方

```bash
grep -rn "business_rules\|from business_rules" --include="*.py"
```

### `itsm/component/apigw/` 消费方

```bash
grep -rn "from itsm.component.apigw" --include="*.py"
```

### `itsm/component/bkchat/` 消费方

```bash
grep -rn "from itsm.component.bkchat\|USE_BKCHAT\|BKCHAT" --include="*.py"
```

## 3. 删除蓝鲸配置文件

| 文件 | 说明 |
|------|------|
| `app.yml` | 蓝鲸 SaaS 应用描述 |
| `app_desc.yaml` | 蓝鲸容器化应用描述 |
| `Procfile` | 蓝鲸 PaaS 进程配置 |
| `Aptfile` | 蓝鲸 PaaS 系统包 |

```bash
rm -f app.yml app_desc.yaml Procfile Aptfile
```

## 4. 清理其他 blueapps 残留引用

### blueapps exceptions

```bash
grep -rn "from blueapps.core.exceptions" --include="*.py"
```

如 `itsm/component/esb/esbclient.py` 已在 Plan 06 删除，此处应无残留。

### blueapps settings proxy

```bash
grep -rn "from blueapps.conf" --include="*.py"
```

### blueapps opentelemetry

```bash
grep -rn "blueapps.opentelemetry" --include="*.py"
```

### blueapps mako

```bash
grep -rn "blueapps.template" --include="*.py"
```

### RUN_VER 引用

```bash
grep -rn "RUN_VER" --include="*.py"
```

每个引用要么删除，要么替换为不依赖蓝鲸的逻辑。

## 5. 处理 `celery_statsd.py`

```bash
grep -rn "blueapps" celery_statsd.py
```

如有残留，替换为 `from config import celery_app`。

## 6. 删除 `itsm/tests/adapter/` 测试

```bash
rm -rf itsm/tests/adapter/
```

## 7. 清理数据迁移模块中的蓝鲸引用

```bash
grep -rn "blueapps\|blueking\|iam\|RUN_VER" --include="*.py" data_migration/
```

## 验证

```bash
# 终极 grep — 零蓝鲸依赖
grep -rE "blueapps|blueking|apigw_manager|bk_notice|bkstorages|from iam |RUN_VER" --include="*.py" | grep -v "docs/"
# 应返回零匹配

ls sops_proxy/ business_rules/ platform_config/ itsm/component/apigw/ itsm/component/bkchat/ 2>&1
# 应显示 "No such file or directory"

ls app.yml app_desc.yaml Procfile Aptfile 2>&1
# 应显示 "No such file or directory"
```
