from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Optional

from django.db import transaction
from django.utils import timezone

from apps.clients.models import Cliente
from apps.clients.services import ClientService
from apps.inventory.models import Product
from apps.shared.serializers import model_to_legacy_dict

from .models import Sale, SaleDetail


def q2(value) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class SaleService:
    client_service = ClientService()

    def register_sale_from_cart(
        self,
        cart_items,
        usuario_id: int,
        cliente_data: Optional[dict] = None,
        metodo_pago: Optional[str] = None,
        observaciones: Optional[str] = None,
        descuento: Decimal | int | float = 0,
        numero_factura: str | None = None,
        ciudad: str | None = None,
        abono: Decimal | int | float = 0,
    ) -> int:
        cliente_obj = None
        cliente_data = cliente_data or {}
        rut = (cliente_data.get("rut") or "").strip()

        with transaction.atomic():
            if rut:
                defaults = {
                    "nombres": cliente_data.get("nombres") or "",
                    "ap_pat": cliente_data.get("ap_pat") or "",
                    "ap_mat": cliente_data.get("ap_mat"),
                    "telefono": cliente_data.get("telefono"),
                    "email": cliente_data.get("email"),
                    "direccion": cliente_data.get("direccion"),
                    "estado": True,
                }
                cliente_obj = self.client_service.get_or_create_by_rut(rut, defaults)

            sale = Sale.objects.create(
                cliente=cliente_obj,
                usuario_id=usuario_id,
                total=Decimal("0.00"),
                descuento=q2(descuento or 0),
                metodo_pago=metodo_pago,
                observaciones=observaciones,
                estado="completada",
                fecha_venta=timezone.now(),
                numero_factura=numero_factura,
                ciudad=ciudad,
            )

            subtotal_general = Decimal("0.00")
            subtotal_15 = Decimal("0.00")
            subtotal_5 = Decimal("0.00")
            subtotal_0 = Decimal("0.00")
            descuento_total = q2(descuento or 0)
            iva_15 = Decimal("0.00")
            iva_5 = Decimal("0.00")

            for item in cart_items:
                producto_id = int(item["producto_id"])
                cantidad = int(item.get("cantidad", 0) or 0)
                if cantidad <= 0:
                    continue

                product = (
                    Product.objects.select_for_update()
                    .filter(producto_id=producto_id)
                    .first()
                )
                if not product:
                    raise ValueError(f"Producto ID {producto_id} no existe.")

                stock_actual = product.cantidad or 0
                if stock_actual < cantidad:
                    raise ValueError(f"Stock insuficiente para {product.nombre}.")

                precio_base = product.costo_venta_1 or product.costo_unitario or 0
                precio = q2(precio_base)
                tarifa_iva = q2(item.get("tarifa_iva") or 0)
                descuento_linea = q2(item.get("descuento") or 0)

                base = q2(precio * cantidad)
                base_desc = q2(base - descuento_linea)
                iva_linea = q2(base_desc * tarifa_iva)
                total_linea = q2(base_desc + iva_linea)

                if tarifa_iva == q2("0.15"):
                    subtotal_15 += base_desc
                    iva_15 += iva_linea
                elif tarifa_iva == q2("0.05"):
                    subtotal_5 += base_desc
                    iva_5 += iva_linea
                else:
                    subtotal_0 += base_desc

                SaleDetail.objects.create(
                    venta=sale,
                    producto=product,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=base,
                    tarifa_iva=tarifa_iva,
                    descuento=descuento_linea,
                    valor_total=total_linea,
                    codigo_principal=item.get("codigo_principal") or product.codigo,
                    codigo_auxiliar=item.get("codigo_auxiliar"),
                )

                product.cantidad = stock_actual - cantidad
                product.save(update_fields=["cantidad"])

                subtotal_general += base_desc

            total_iva = iva_15 + iva_5
            total_pagar = subtotal_general + total_iva
            abono_val = q2(abono or 0)
            saldo_val = q2(total_pagar - abono_val)

            sale.subtotal_general = q2(subtotal_general)
            sale.subtotal_tarifa_15 = q2(subtotal_15)
            sale.subtotal_tarifa_5 = q2(subtotal_5)
            sale.subtotal_tarifa_0 = q2(subtotal_0)
            sale.descuento_total = descuento_total
            sale.iva_15 = q2(iva_15)
            sale.iva_5 = q2(iva_5)
            sale.total = q2(total_pagar)
            sale.abono = abono_val
            sale.saldo = saldo_val
            sale.save(
                update_fields=[
                    "subtotal_general",
                    "subtotal_tarifa_15",
                    "subtotal_tarifa_5",
                    "subtotal_tarifa_0",
                    "descuento_total",
                    "iva_15",
                    "iva_5",
                    "total",
                    "abono",
                    "saldo",
                ]
            )

        return sale.venta_id

    def get_sale_details_for_receipt(self, venta_id: int):
        return (
            Sale.objects.select_related("cliente", "usuario")
            .prefetch_related("detalles__producto")
            .filter(venta_id=venta_id)
            .first()
        )

    def get_all_sales_with_details(self) -> Iterable[Sale]:
        return (
            Sale.objects.select_related("cliente", "usuario")
            .prefetch_related("detalles__producto")
            .order_by("-fecha_venta")
        )

    def serialize_sale(self, sale: Sale) -> dict:
        data = model_to_legacy_dict(sale)
        data["cliente"] = model_to_legacy_dict(sale.cliente) if sale.cliente else None
        data["usuario"] = model_to_legacy_dict(sale.usuario) if sale.usuario else None
        data["detalles"] = [model_to_legacy_dict(det) for det in sale.detalles.all()]
        return data
