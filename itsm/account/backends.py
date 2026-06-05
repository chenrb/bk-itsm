# -*- coding: utf-8 -*-
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model


class CustomUserBackend:
    """Authenticate OpenAPI requests via JWT token."""

    def authenticate(self, request, **credentials):
        token = credentials.get("token") or (
            request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
            if request
            else None
        )
        if not token:
            return None
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        username = payload.get("sub") or payload.get("username")
        if not username:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create(username=username, nickname=username)
        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
