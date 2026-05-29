# Plan 13: OpenAPI 认证重写 + 文件存储替换

> 前置条件：Plan 01-06 已完成
> 目标：OpenAPI 不再依赖 apigw_manager，文件存储不再依赖 bkstorages

## 1. 重写 OpenAPI 认证

### `itsm/openapi/authentication/backend.py`

移除 `apigw_manager.apigw.authentication.UserModelBackend`，用 PyJWT 实现：

```python
import jwt
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """替代 apigw_manager 的 JWT 认证"""

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        try:
            user = User.objects.get(username=payload.get("sub"))
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, None)


class CustomUserBackend:
    """兼容 DRF AUTHENTICATION_BACKENDS 配置"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
```

### `itsm/openapi/apps.py`

- 移除 `from blueapps.utils import get_client_by_user`
- 移除 ESB 公钥同步逻辑（`api_public_key` 相关）
- 移除 `ENABLE_SYNC_API_GATEWAY` 条件块

### `config/default.py`

- 确认已移除 `apigw_manager.apigw` 的 INSTALLED_APPS 条目（Plan 02 应已处理）
- 确认已移除 APIGW JWT middleware（Plan 02 应已处理）
- 确认已移除 `APIGW_APP_CODE`, `APIGW_SECRET_KEY`, `APIGW_USERNAME`, `APIGW_PUBLIC_KEY` 配置
- 确认已移除 `BK_APIGW_NAME`, `BK_API_URL_TMPL` 配置

## 2. 替换文件存储

### `adapter/utils/storage.py`

此文件已在 Plan 06 随 adapter 目录一起删除。

### 如有其他文件引用 bkstorages

```bash
grep -rn "bkstorages" --include="*.py"
```

将 `from bkstorages.backends.rgw import RGWBoto3Storage` 替换为：

```python
from django.core.files.storage import FileSystemStorage
```

### `config/default.py`

添加存储配置：

```python
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
# 生产环境可改为：
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
```

如需 S3/MinIO 支持，添加 `django-storages` 和 `boto3` 到 requirements.txt。

## 3. 移除 bk_notice_sdk

### `config/default.py`

- 确认已移除 `"bk_notice_sdk"` 的 INSTALLED_APPS 条目（Plan 02 应已处理）

### `urls.py`

- 移除 `bk_notice_sdk` URL 路由（如有）

## 验证

```bash
grep -rn "apigw_manager\|bkstorages\|bk_notice" --include="*.py"
# 应返回零匹配

python manage.py check
```
