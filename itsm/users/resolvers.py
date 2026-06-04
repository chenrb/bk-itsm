# -*- coding: utf-8 -*-
"""
处理人解析器：替代 UserRole.get_users_by_type()。
根据 user_type 和 users_param 解析出处理人 username 列表。
"""
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

User = get_user_model()


def resolve_processors(user_type, users_param, ticket=None):
    """
    解析处理人列表。

    Args:
        user_type: 处理人类型 (PERSON, GENERAL, STARTER, etc.)
        users_param: 类型参数（逗号分隔的 ID 或 username）
        ticket: 工单实例（用于 STARTER, ASSIGN_LEADER 等需要工单上下文的类型）

    Returns:
        list[str]: 去重的 username 列表

    Raises:
        ValueError: 不支持的 user_type
    """
    if user_type == "PERSON":
        return _resolve_person(users_param)
    elif user_type == "GENERAL":
        return _resolve_general(users_param)
    elif user_type == "STARTER":
        return _resolve_starter(ticket)
    elif user_type == "STARTER_LEADER":
        return _resolve_leader(users_param)
    elif user_type == "ASSIGN_LEADER":
        return _resolve_assign_leader(users_param, ticket)
    elif user_type == "ORGANIZATION":
        return _resolve_organization(users_param)
    elif user_type in ("BY_ASSIGNOR", "OPEN", "API", "VARIABLE", "EMPTY"):
        return []
    else:
        raise ValueError(_("不支持的处理人类型: %(type)s") % {"type": user_type})


def _resolve_person(users_param):
    """PERSON: 直接拆分 username。"""
    if not users_param:
        return []
    return [u.strip() for u in users_param.split(",") if u.strip()]


def _resolve_general(users_param):
    """GENERAL: 查询 UserGroup.members，过滤 is_active=False 的用户。"""
    if not users_param:
        return []
    from itsm.users.models import UserGroup

    group_ids = [int(x.strip()) for x in users_param.split(",") if x.strip()]
    if not group_ids:
        return []
    usernames = list(
        User.objects.filter(
            user_groups__in=group_ids, is_active=True
        ).values_list("username", flat=True)
    )
    return list(set(usernames))


def _resolve_starter(ticket):
    """STARTER: 返回工单创建人。"""
    if not ticket:
        return []
    creator = getattr(ticket, "creator", "")
    return [creator] if creator else []


def _resolve_leader(users_param):
    """STARTER_LEADER: 查找指定用户的直属上级。"""
    if not users_param:
        return []
    username = users_param.strip().split(",")[0]
    try:
        user = User.objects.get(username=username, is_active=True)
        if user.leader and user.leader.is_active:
            return [user.leader.username]
    except User.DoesNotExist:
        pass
    return []


def _resolve_assign_leader(users_param, ticket):
    """ASSIGN_LEADER: 查找指定节点的处理人的直属上级。"""
    if not ticket or not users_param:
        return []
    state_id = users_param.strip()
    # 查找该 state 的处理人，再取其 leader
    try:
        state = ticket.states.get(id=state_id)
        processors = getattr(state, "processors", "")
        if processors:
            processor_username = processors.split(",")[0]
            user = User.objects.get(username=processor_username, is_active=True)
            if user.leader and user.leader.is_active:
                return [user.leader.username]
    except Exception:
        pass
    return []


def _resolve_organization(users_param):
    """ORGANIZATION: 递归查询部门及子部门的全部用户。"""
    if not users_param:
        return []
    from itsm.users.models import Department, DeptMembership

    dept_ids = [int(x.strip()) for x in users_param.split(",") if x.strip()]
    if not dept_ids:
        return []

    # 递归收集所有子部门
    all_dept_ids = set(dept_ids)
    for dept_id in dept_ids:
        try:
            dept = Department.objects.get(pk=dept_id)
            all_dept_ids.update(
                dept.get_descendants().values_list("id", flat=True)
            )
        except Department.DoesNotExist:
            pass

    # 查询所有部门的活跃用户
    usernames = list(
        User.objects.filter(
            dept_memberships__department_id__in=all_dept_ids, is_active=True
        ).values_list("username", flat=True)
    )
    return list(set(usernames))
