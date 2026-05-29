# Plan 04: 自定义 User 模型 + Django Session Auth

> 前置条件：Plan 01-03 已完成
> 目标：建立独立用户模型，用户可以登录/登出，API 认证正常

## 1. 新建 `itsm/component/users/__init__.py`

空文件。

## 2. 新建 `itsm/component/users/models.py`

```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The username field must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField("用户名", max_length=128, unique=True, db_index=True)
    nickname = models.CharField("昵称", max_length=255, blank=True, default="")
    chname = models.CharField("中文名", max_length=255, blank=True, default="")
    phone = models.CharField("电话", max_length=32, blank=True, default="")
    email = models.EmailField("邮箱", blank=True, default="")
    is_staff = models.BooleanField("后台访问权限", default=False)
    is_active = models.BooleanField("启用", default=True)
    date_joined = models.DateTimeField("注册时间", auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users_user"
        verbose_name = "用户"

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        return self.nickname or self.chname or self.username


class UserProperty(models.Model):
    """兼容 blueapps UserProperty"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    key = models.CharField(max_length=128)
    value = models.TextField(blank=True, default="")

    class Meta:
        db_table = "users_user_property"
        unique_together = ("user", "key")
```

## 3. 新建 `itsm/component/users/apps.py`

```python
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "itsm.component.users"
    label = "users"
    verbose_name = "用户管理"
```

**注意**：`label = "users"` 确保 `AUTH_USER_MODEL = "users.User"` 生效。

## 4. 新建 `itsm/component/users/views.py`

```python
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views import View
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
```

## 5. 新建 `itsm/component/users/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
```

## 6. 更新 `config/default.py`

在 INSTALLED_APPS 中添加：
```python
"itsm.component.users",
```

在文件顶部或 AUTHENTICATION_BACKENDS 处设置：
```python
AUTH_USER_MODEL = "users.User"
```

## 7. 更新 `urls.py`

替换蓝鲸 account URL：

```python
# 移除
re_path(r"^account/", include("blueapps.account.urls"))

# 替换为
path("account/", include("itsm.component.users.urls")),
```

## 8. 创建登录模板

新建 `templates/registration/login.html`（最小化）：

```html
<!DOCTYPE html>
<html>
<head><title>登录 - ITSM</title></head>
<body>
<h2>ITSM 登录</h2>
<form method="post">
  {% csrf_token %}
  <input type="hidden" name="next" value="{{ next }}">
  <label>用户名: <input type="text" name="username"></label><br>
  <label>密码: <input type="password" name="password"></label><br>
  <button type="submit">登录</button>
</form>
</body>
</html>
```

## 9. 数据迁移注意事项

如需从 `account_user`（blueapps 表）迁移数据，需编写数据迁移脚本：

```bash
python manage.py makemigrations users
python manage.py migrate
```

## 验证

```bash
python manage.py makemigrations users
python manage.py migrate
python manage.py createsuperuser
# 测试登录/登出
python manage.py runserver
# 访问 /account/login/
```
