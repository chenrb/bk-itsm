# -*- coding: utf-8 -*-
"""Authentication views - placeholder, will be fully implemented in task 7."""
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "registration/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "/")
        return context

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next", "/")
            return JsonResponse({"result": True, "data": {"redirect_url": next_url}})
        return JsonResponse(
            {"result": False, "message": "用户名或密码错误"}, status=401
        )


def logout_view(request):
    logout(request)
    return JsonResponse({"result": True})
