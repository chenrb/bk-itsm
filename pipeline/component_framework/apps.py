# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2025 Tencent. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from django.apps import AppConfig
from django.db.utils import InternalError, OperationalError, ProgrammingError

from pipeline.conf import settings
from pipeline.utils.register import autodiscover_collections

logger = logging.getLogger("root")


def _do_component_sync():
    """Sync component status in DB with registered components (runs after apps are ready)."""
    from pipeline.component_framework.models import ComponentModel
    from pipeline.component_framework.library import ComponentLibrary

    try:
        for code in ComponentLibrary.codes():
            for version in ComponentLibrary.versions(code):
                component_cls = ComponentLibrary.get_component_class(code=code, version=version)
                group_name = getattr(component_cls, "group_name", "")
                new_name = "{}-{}".format(group_name, component_cls.name)
                ComponentModel.objects.update_or_create(
                    code=code, version=version, defaults={"name": new_name, "status": True}
                )
        ComponentModel.objects.exclude(code__in=list(ComponentLibrary.codes())).update(status=False)
    except InternalError:
        logger.warning(
            "[component_framework] 数据库版本字段迁移中，跳过组件注册"
        )
    except (ProgrammingError, OperationalError):
        logger.warning(
            "[component_framework] 数据库表尚未创建，跳过组件注册。"
            "请先执行 python manage.py migrate"
        )


def init_component_framework(**kwargs):
    """
    注册公共部分和当前RUN_VER下的标准插件到数据库
    :return:
    """
    for path in settings.COMPONENT_AUTO_DISCOVER_PATH:
        autodiscover_collections(path)

    # Defer DB status sync to post_migrate (avoids RuntimeWarning from ready())
    from django.db.models.signals import post_migrate

    def _sync_on_migrate(sender, **kwargs):
        post_migrate.disconnect(_sync_on_migrate)
        _do_component_sync()

    post_migrate.connect(_sync_on_migrate)


class ComponentFrameworkConfig(AppConfig):
    name = "pipeline.component_framework"
    verbose_name = "PipelineComponentFramework"

    def ready(self):
        init_component_framework()
