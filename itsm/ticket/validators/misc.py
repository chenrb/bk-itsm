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
from django.utils.translation import gettext as _
from rest_framework import serializers

from common.log import logger
from itsm.component.utils.basic import Regex
from itsm.component.utils.client_backend_query import get_bk_users
from itsm.role.models import UserRole
from itsm.ticket.models import Ticket, TicketComment, TicketCommentInvite


def days_validate(days):
    """天数参数校验"""
    try:
        days = int(days)
    except ValueError:
        raise serializers.ValidationError(_("天数参数类型错误！"))
    return days


def notify_log_validate(data, operator):
    """发送通知的校验"""

    # 发送关注信息的校验
    message = data.get("message", "")
    ticket_id = data.get("ticket_id")

    if not message:
        raise serializers.ValidationError(_("请填写关注信息！"))
    if len(message) > 200:
        raise serializers.ValidationError(_("关注信息不能超过200个字符！"))

    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        logger.error("发送关注通知校验失败：单据不存在 ticket_id={}".format(ticket_id))
        raise serializers.ValidationError(
            _("发送关注通知校验失败：单据不存在，请联系管理员")
        )

    if not ticket.can_invite_followers(operator):
        raise serializers.ValidationError(
            _("发送关注通知校验失败：单据已结束或权限不足")
        )

    followers = data.get("followers")
    followers_type = data.get("followers_type")
    receivers = UserRole.get_users_by_type(
        user_type=followers_type, users=followers
    )
    if not receivers:
        logger.error(
            "发送关注通知校验失败：接收人不存在：receivers={}, followers={}, followers_type={}".format(
                receivers, followers, followers_type
            )
        )
        raise serializers.ValidationError(
            _("发送关注通知校验失败：通知人不存在或通知角色没有人员，请联系管理员")
        )

    return ticket, ",".join(receivers)




def email_invite_validate(ticket, invitor, receivers):
    """邮件邀请评价校验"""

    if not ticket.can_comment(invitor):
        raise serializers.ValidationError(_("抱歉，您无权发送评价邀请"))

    # 验证每个接收者是否存在
    all_users = get_bk_users(users=receivers)
    for receiver in receivers:
        if receiver not in all_users:
            raise serializers.ValidationError(_("【{}】用户不存在").format(receiver))
