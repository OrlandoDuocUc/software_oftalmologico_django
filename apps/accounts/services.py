from __future__ import annotations

from typing import Iterable, Optional

from django.db import transaction
from werkzeug.security import check_password_hash, generate_password_hash

from .models import LegacyUser, Role


class LegacyUserService:
    """
    Replica la lógica de app.domain.use_cases.services.user_service pero usando
    directamente el ORM de Django.
    """

    def authenticate(self, username: str, password: str):
        try:
            user = LegacyUser.objects.select_related("rol").get(username=username)
        except LegacyUser.DoesNotExist:
            return None

        if not user.estado:
            return "inactivo"

        if check_password_hash(user.password, password):
            return user
        return None

    def get_user(self, user_id: int) -> Optional[LegacyUser]:
        return LegacyUser.objects.select_related("rol").filter(usuario_id=user_id).first()

    def get_all_users(self) -> Iterable[LegacyUser]:
        return LegacyUser.objects.select_related("rol").all()

    def register_user(
        self,
        nombre: str,
        ap_pat: str,
        ap_mat: Optional[str],
        username: str,
        email: str,
        password: str,
        rol_nombre: str = "Vendedor",
    ) -> LegacyUser:
        with transaction.atomic():
            rol = Role.objects.filter(nombre__iexact=rol_nombre).first()
            if not rol:
                raise ValueError(f"Rol '{rol_nombre}' no existe")

            password_hash = generate_password_hash(password)
            return LegacyUser.objects.create(
                rol=rol,
                username=username,
                password=password_hash,
                nombre=nombre,
                ap_pat=ap_pat,
                ap_mat=ap_mat,
                email=email,
                estado=True,
            )

    def update_user(self, user_id: int, **attrs) -> Optional[LegacyUser]:
        user = self.get_user(user_id)
        if not user:
            return None

        password = attrs.pop("password", None)
        if password:
            user.password = generate_password_hash(password)

        for key, value in attrs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.save()
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        try:
            user.delete()
            return True
        except Exception:
            user.estado = False
            user.save(update_fields=["estado"])
            return False
