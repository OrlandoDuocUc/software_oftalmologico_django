from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.utils import timezone
from werkzeug.security import check_password_hash

from .models import LegacyUser


class LegacyUserBackend(BaseBackend):
    """
    Permite autenticar usuarios contra la tabla legacy `usuarios` conservando
    la gestión de sesiones estándar de Django.
    """

    def authenticate(self, request, username=None, password=None, **kwargs) -> Optional[User]:
        if username is None or password is None:
            return None
        try:
            legacy = LegacyUser.objects.select_related("rol").get(username=username)
        except LegacyUser.DoesNotExist:
            return None

        if not legacy.estado:
            return None

        if not check_password_hash(legacy.password, password):
            return None

        user_model = get_user_model()
        defaults = {
            "first_name": legacy.nombre or "",
            "last_name": legacy.ap_pat or "",
            "email": legacy.email or "",
        }
        user, created = user_model.objects.get_or_create(username=legacy.username, defaults=defaults)

        user.first_name = legacy.nombre or ""
        user.last_name = " ".join(filter(None, [legacy.ap_pat, legacy.ap_mat]))[:150]
        user.email = legacy.email or ""
        is_admin = legacy.rol and legacy.rol.nombre.lower() == "administrador"
        user.is_staff = is_admin
        user.is_superuser = is_admin
        user.last_login = timezone.now()
        user.save()

        if request is not None:
            request.session["legacy_user_id"] = legacy.usuario_id
            request.session["rol"] = legacy.rol.nombre if legacy.rol else ""

        return user

    def get_user(self, user_id: int) -> Optional[User]:
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
