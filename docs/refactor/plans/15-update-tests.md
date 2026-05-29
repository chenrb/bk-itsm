# Plan 15: 更新测试文件

> 前置条件：Plan 01-14 已完成
> 目标：所有测试文件不再引用已删除的模块

## 1. 替换 Celery app import（13 个文件）

| 旧 import | 新 import |
|-----------|-----------|
| `from blueapps.core.celery.celery import app` | `from config import celery_app as app` |

### 涉及文件

- `itsm/tests/workflow/test_base_service.py`
- `itsm/tests/workflow/test_bk_sops.py` — 考虑删除（bk_sops 组件已移除）
- `itsm/tests/workflow/test_bk_devops.py` — 考虑删除（bk_devops 组件已移除）
- `itsm/tests/workflow/test_itsm_approve.py`
- `itsm/tests/workflow/test_itsm_auto.py`
- `itsm/tests/workflow/test_webhook.py`
- `itsm/tests/ticket/test_ticket_view.py`
- `itsm/tests/ticket/test_ticket_remark.py`
- `itsm/tests/components/test_utils.py`
- `itsm/tests/helper/test_helper.py`

## 2. 删除已无意义的测试文件/目录

| 目录/文件 | 原因 |
|-----------|------|
| `itsm/tests/iam/` | IAM SDK 已删除 |
| `itsm/tests/adapter/` | adapter 已删除 |
| `itsm/tests/workflow/test_bk_sops.py` | bk_sops 组件已删除 |
| `itsm/tests/workflow/test_bk_devops.py` | bk_devops 组件已删除 |

```bash
rm -rf itsm/tests/iam/
rm -rf itsm/tests/adapter/
rm -f itsm/tests/workflow/test_bk_sops.py
rm -f itsm/tests/workflow/test_bk_devops.py
```

## 3. 更新引用已删除模块的测试

搜索测试文件中的蓝鲸引用：
```bash
grep -rn "from iam\|from itsm.auth_iam\|from blueapps\|from blueking\|from adapter\|from weixin\|from sops_proxy\|from business_rules" --include="*.py" itsm/tests/
```

对每个匹配：
1. 如测试的是已删除功能 → 删除测试
2. 如仅 import 用于 mock → 替换为新的 import
3. 如测试逻辑依赖蓝鲸服务 → 重写测试用例

## 4. 更新测试 runner

检查 `itsm/tests/runner.py`：
```bash
grep -rn "blueapps\|RUN_VER" itsm/tests/runner.py
```

如有引用则替换。

## 5. 更新 CI 配置

### `.github/workflows/django.yml`

- 移除 `RUN_VER` 环境变量设置
- 移除 `BKPAAS_*` 环境变量
- 保留 `BK_MYSQL_*` 和 `BROKER_URL` 配置

### `bin/pre_compile`

- 移除 `RUN_VER` 相关逻辑（如文件保留的话）

## 验证

```bash
grep -rn "blueapps\|blueking\|from iam\|from adapter\|RUN_VER" --include="*.py" itsm/tests/
# 应返回零匹配

# 尝试运行测试（可能需要配置测试数据库）
python manage.py test itsm.tests --keepdb 2>&1 | head -50
```
