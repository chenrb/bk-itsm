# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2025 Tencent.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext as _

from common.log import logger
from itsm.component.constants import (
    NOTIFY_TYPE_CHOICES,
    BUILTIN_NOTIFY_TYPE,
)


def translate_constant_2(constant):
    temp_constant = []
    for item in constant:
        # py2->py3: 'str' object has no attribute 'decode'
        temp_constant.append((item[0], _(item[1])))
    constant = temp_constant
    return constant


def init_notify_type_choice():
    """获取通知类型（本地配置）"""
    return NOTIFY_TYPE_CHOICES


def get_notify_type_choice():
    from itsm.workflow.models import Notify

    """获取通知类型"""
    try:
        if settings.OPEN_VOICE_NOTICE:
            notify_type_choice = list(Notify.objects.all().values_list("type", "name"))
        else:
            notify_type_choice = list(
                Notify.objects.filter(~Q(type="VOICE")).values_list("type", "name")
            )

        return notify_type_choice
    except Notify.DoesNotExist:
        return NOTIFY_TYPE_CHOICES
    except Exception:
        return NOTIFY_TYPE_CHOICES


def get_third_party_notify_type():
    from itsm.workflow.models import Notify

    """获取第三方通知类型"""
    try:
        notify_type_list = list(
            Notify.objects.exclude(type__in=BUILTIN_NOTIFY_TYPE).values_list(
                "type", flat=True
            )
        )
        if not settings.OPEN_VOICE_NOTICE:
            if "VOICE" in notify_type_list:
                notify_type_list.remove("VOICE")
        return notify_type_list
    except Notify.DoesNotExist:
        return []
