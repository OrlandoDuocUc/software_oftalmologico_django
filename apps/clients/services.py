from __future__ import annotations

from typing import Optional

from django.db import transaction

from .models import Cliente


class ClientService:
    def create_cliente(self, **data) -> Cliente:
        with transaction.atomic():
            return Cliente.objects.create(**data)

    def get_cliente_by_id(self, cliente_id: int) -> Optional[Cliente]:
        return Cliente.objects.filter(cliente_id=cliente_id).first()

    def get_or_create_by_rut(self, rut: str, defaults: Optional[dict] = None) -> Cliente:
        cliente, _ = Cliente.objects.get_or_create(rut=rut, defaults=defaults or {})
        return cliente

    def list_clientes(self):
        return Cliente.objects.all()
