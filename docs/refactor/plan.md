# BK-ITSM 重构计划

## 已完成阶段

### Phase 1: 去蓝鲸依赖 → [归档](phase1-bk-decoupling/)

将 BK-ITSM 从蓝鲸 PaaS 平台完全解耦，使项目可独立部署运行。16 个子计划全部完成。

- 技术规格：[spec.md](phase1-bk-decoupling/spec.md)
- 16 个子计划：[plans/](phase1-bk-decoupling/plans/)
- 关键提交：`e1c87a87`
- 替代方案：blueapps → Django auth、IAM SDK → guardian、ESB → platform_client、bkstorages → django-storages、apigw_manager JWT → PyJWT

### Phase 2: 死代码与残余清理 → [归档](phase2-cleanup/)

清理 Phase 1 后的无引用代码、WeChat 通知系统、SOPS/DevOps 任务基础设施。

- 关键提交：`689d1ed9`, `25fd5cc7`, `0376e6b3`, `68704d97`
- SOPS/DevOps 完整移除（激进模式，含 SopsTask/SubTask 模型）
- ESB/apigw/bkchat stub → `itsm/component/platform_client/http.py`
- `itsm/helper/` app 解散，代码各归其位
- `config/integrations.py` 143→54 行
- 总计 ~130 文件，~11,000 行删除

### Phase 2.1: 持续清理

Phase 2 后发现的零散死代码清理。

- 删除 `core/` 包（`BkWSGIHandler` 及自定义 WSGI 入口）— 根目录 `wsgi.py` 已使用标准 Django WSGI，`core/` 无任何引用

### 验证状态

零蓝鲸硬依赖残留（blueapps、blueking、apigw_manager、bk_notice_sdk、bkstorages、iam SDK、auth_iam、esb、apigw、bkchat、helper、core — 全部归零）。

---

## 待规划阶段

<!-- 在此添加新的重构计划 -->
