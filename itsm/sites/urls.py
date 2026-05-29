# -*- coding: utf-8 -*-
from django.urls import include, re_path

from itsm.sites.views import index, get_footer, init

urlpatterns = [
    re_path(r"^$", index),
    re_path(r"^init/$", init),
    re_path(r"^core/footer/$", get_footer),
    re_path(r"^helper/", include("itsm.helper.urls")),
]
