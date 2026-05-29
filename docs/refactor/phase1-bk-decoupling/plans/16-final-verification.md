# Plan 16: 最终验证

> 前置条件：Plan 01-15 已完成
> 目标：确认零蓝鲸依赖，项目可正常运行

## 1. 完整 import 审计

```bash
# 核心依赖检查
grep -rE "blueapps|blueking|apigw_manager|bk_notice|bkstorages|from iam |RUN_VER" --include="*.py" | grep -v "docs/" | grep -v "__pycache__"

# 扩展检查
grep -rE "from weixin|from adapter|from sops_proxy|from business_rules|from itsm.auth_iam|from itsm.component.esb|from itsm.plugin_service|from itsm.component.apigw|from itsm.component.bkchat|from itsm.component.bkoauth|from itsm.component.auto_register" --include="*.py" | grep -v "docs/" | grep -v "__pycache__"
```

以上两条命令均应返回零匹配。

## 2. Django 系统检查

```bash
python manage.py check --deploy
```

应无 ERROR 级别问题（WARNING 可接受）。

## 3. 数据库迁移

```bash
# 空 DB 上
python manage.py makemigrations --check
python manage.py migrate
```

## 4. 运行测试

```bash
python manage.py test itsm.tests --keepdb
```

如有测试失败，逐个分析是否因重构导致，修复或删除无效测试。

## 5. 功能验证清单

| 功能 | 验证方法 |
|------|----------|
| 启动 | `python manage.py runserver` 无报错 |
| 登录 | 访问 `/account/login/`，输入用户名密码可登录 |
| 登出 | 访问 `/account/logout/` |
| API 访问 | 登录后访问 `/api/` 返回正常 JSON |
| 权限检查 | 非 admin 用户访问 admin API 返回 403 |
| Celery 任务 | `celery -A config worker` 可启动 |
| Pipeline | 创建工单流程正常执行 |
| 通知 | 邮件通知可发送（需配置 SMTP） |
| 静态文件 | `python manage.py collectstatic` 正常 |
| Admin 后台 | `/admin/` 可访问 |

## 6. 更新文档

### `CLAUDE.md`

- 移除蓝鲸相关环境变量说明
- 更新 `requirements.txt` 中的依赖说明
- 更新架构说明（无蓝鲸依赖）

### `docs/refactor/plan.md` 和 `docs/refactor/spec.md`

- 标记为已完成

## 7. Git 操作

```bash
git add -A
git status  # 确认变更合理
git diff --stat  # 确认删除的文件和新增的文件
```

## 完成标志

- [ ] import 审计零匹配
- [ ] `python manage.py check` 通过
- [ ] `python manage.py migrate` 通过
- [ ] `python manage.py test itsm.tests` 通过
- [ ] 功能验证清单全部通过
- [ ] CLAUDE.md 已更新
