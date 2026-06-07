# -*- coding: utf-8 -*-
from django.urls import path

from itsm.account.views.auth import api_login, api_logout

urlpatterns = [
    path("login/", api_login, name="login"),
    path("logout/", api_logout, name="logout"),
]
