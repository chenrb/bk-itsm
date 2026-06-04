# -*- coding: utf-8 -*-
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from itsm.users.views.auth import login_view, logout_view
from itsm.users.views.department import DepartmentViewSet
from itsm.users.views.gateway import (
    bk_get_all_users,
    bk_get_batch_users,
    fs_list_users,
    get_department_info,
    get_department_users,
    get_department_users_count,
    get_departments,
    get_first_level_departments,
    get_user_info,
)
from itsm.users.views.permission import PermissionViewSet
from itsm.users.views.role import RoleViewSet
from itsm.users.views.role_compat import (
    get_access_by_user,
    get_global_choices,
    role_types,
    role_users,
)
from itsm.users.views.security import SecurityPolicyViewSet
from itsm.users.views.user import UserViewSet
from itsm.users.views.user_group import UserGroupViewSet

# DRF Router for ViewSets
router = DefaultRouter(trailing_slash=True)
router.register(r"users", UserViewSet, basename="user")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"user-groups", UserGroupViewSet, basename="user-group")
router.register(r"security-policies", SecurityPolicyViewSet, basename="security-policy")

urlpatterns = [
    # ── Auth endpoints (mounted at /account/ via root urls.py) ──
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]

# API ViewSet routes (mounted at /api/ via root urls.py)
api_urlpatterns = router.urls

# Gateway compatibility routes (mounted at /gateway/ via root urls.py)
gateway_usermanage_urlpatterns = [
    re_path(
        r"^usermanage/get_first_level_departments/$",
        get_first_level_departments,
    ),
    re_path(r"^usermanage/get_department_info/$", get_department_info),
    re_path(r"^usermanage/get_departments/$", get_departments),
    re_path(r"^usermanage/get_department_users/$", get_department_users),
    re_path(
        r"^usermanage/get_department_users_count/$", get_department_users_count
    ),
    re_path(r"^usermanage/get_user_info/$", get_user_info),
]

gateway_bk_login_urlpatterns = [
    re_path(r"^bk_login/get_batch_users/$", bk_get_batch_users),
    re_path(r"^bk_login/get_all_users/$", bk_get_all_users),
]

# Role compatibility routes (mounted at /api/role/ via root urls.py)
role_compat_urlpatterns = [
    re_path(r"^types/$", role_types),
    re_path(r"^users/$", role_users),
    re_path(r"^users/extra/get_access_by_user/$", get_access_by_user),
    re_path(r"^users/extra/get_global_choices/$", get_global_choices),
]

# JSONP compatibility (mounted at /api/c/compapi/v2/usermanage/)
compapi_urlpatterns = [
    re_path(r"^fs_list_users/$", fs_list_users),
]
