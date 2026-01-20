from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Optional, Sequence

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Compra, CompraDetalle, Product, Proveedor


class ProductService:
    """
    Traducción del ProductUseCases original a Django ORM.
    """

    def list_products(self, include_deleted: bool = False, only_deleted: bool = False) -> Iterable[Product]:
        qs = Product.objects.all()
        if only_deleted:
            return qs.filter(estado=False)
        if not include_deleted:
            qs = qs.filter(estado=True)
        return qs

    def get_product(self, product_id: int) -> Optional[Product]:
        return Product.objects.filter(producto_id=product_id).first()

    def _compute_costs(self, cantidad: int, costo_unitario: Decimal) -> dict:
        cantidad = max(int(cantidad or 0), 0)
        costo_unitario = Decimal(costo_unitario or 0)
        # IVA Ecuador 15 %: costo_total ahora representa el costo unitario con IVA
        costo_total = (costo_unitario * Decimal("1.15"))
        costo_venta_1 = costo_total * Decimal(3)
        costo_venta_2 = costo_total * Decimal(2)
        return {
            "cantidad": cantidad,
            "costo_unitario": costo_unitario,
            "costo_total": costo_total,
            "costo_venta_1": costo_venta_1,
            "costo_venta_2": costo_venta_2,
        }

    def create_product(self, data: dict) -> Product:
        if not data.get("nombre"):
            raise ValueError("El nombre del producto es requerido.")

        cantidad = int(data.get("cantidad") or 0)
        costo_unitario = Decimal(data.get("costo_unitario") or 0)
        if cantidad < 0 or costo_unitario < 0:
            raise ValueError("Cantidad y costo unitario deben ser valores no negativos.")

        payload = {**data, **self._compute_costs(cantidad, costo_unitario)}
        if not payload.get("fecha"):
            payload["fecha"] = timezone.now()

        with transaction.atomic():
            return Product.objects.create(**payload)

    def update_product(self, product_id: int, data: dict) -> Optional[Product]:
        product = self.get_product(product_id)
        if not product:
            return None

        cantidad = data.get("cantidad")
        if cantidad in (None, ""):
            cantidad = product.cantidad or 0
        costo_unitario = data.get("costo_unitario")
        if costo_unitario in (None, ""):
            costo_unitario = product.costo_unitario or 0

        payload = {**data, **self._compute_costs(cantidad, costo_unitario)}

        if not payload.get("fecha"):
            payload["fecha"] = product.fecha

        for key, value in payload.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.save()
        return product

    def delete_product(self, product_id: int) -> bool:
        product = self.get_product(product_id)
        if not product:
            return False
        try:
            with transaction.atomic():
                product.delete()
            return True
        except IntegrityError:
            product.refresh_from_db()
            product.estado = False
            product.save(update_fields=["estado"])
            return False

    def restore_product(self, product_id: int) -> bool:
        product = self.get_product(product_id)
        if not product or product.estado:
            return False
        product.estado = True
        product.save(update_fields=["estado"])
        return True


class PurchaseService:
    """
    Servicio para manejar cabeceras y detalles de compras.
    """

    def list_purchases(self) -> Iterable[Compra]:
        return Compra.objects.select_related("proveedor").prefetch_related("detalles__producto").order_by("-compra_id")

    def create_purchase(self, header: dict, detalles: Sequence[dict]) -> Compra:
        """
        header: dict con campos de compra.
        detalles: lista de dicts con producto_id, cantidad, precio_unitario, tarifa_iva, descuento, etc.
        """
        proveedor = Proveedor.objects.filter(proveedor_id=header.get("proveedor_id")).first()
        if not proveedor:
            raise ValueError("Proveedor no encontrado.")

        with transaction.atomic():
            compra = Compra.objects.create(proveedor=proveedor, **self._compute_totals(header, detalles)["header"])

            # Crear detalles y actualizar inventario
            for det_payload in self._compute_totals(header, detalles)["detalles"]:
                producto = Product.objects.filter(producto_id=det_payload.pop("producto_id")).first()
                if not producto:
                    raise ValueError("Producto no encontrado.")
                
                # Crear el detalle de compra
                detalle = CompraDetalle.objects.create(compra=compra, producto=producto, **det_payload)
                
                # Actualizar el stock del producto en el inventario
                cantidad_anterior = producto.cantidad or 0
                producto.cantidad = cantidad_anterior + detalle.cantidad
                producto.save()

        return compra

    def _compute_totals(self, header: dict, detalles: Sequence[dict]) -> dict:
        subtotal_general = Decimal(0)
        subtotal_15 = Decimal(0)
        subtotal_5 = Decimal(0)
        subtotal_0 = Decimal(0)
        descuento_total = Decimal(0)
        iva_15 = Decimal(0)
        iva_5 = Decimal(0)

        detalles_out = []

        for det in detalles:
            cantidad = Decimal(det.get("cantidad") or 0)
            precio_unitario = Decimal(det.get("precio_unitario") or 0)
            tarifa = Decimal(det.get("tarifa_iva") or 0)
            descuento = Decimal(det.get("descuento") or 0)

            base = (cantidad * precio_unitario)
            base_desc = base - descuento
            iva = base_desc * tarifa
            total_linea = base_desc + iva

            descuento_total += descuento
            subtotal_general += base_desc
            if tarifa == Decimal("0.15"):
                subtotal_15 += base_desc
                iva_15 += iva
            elif tarifa == Decimal("0.05"):
                subtotal_5 += base_desc
                iva_5 += iva
            else:
                subtotal_0 += base_desc

            detalles_out.append(
                {
                    "producto_id": det.get("producto_id"),
                    "marca": det.get("marca"),
                    "codigo": det.get("codigo"),
                    "descripcion": det.get("descripcion"),
                    "cantidad": int(cantidad),
                    "precio_unitario": precio_unitario,
                    "tarifa_iva": tarifa,
                    "descuento": descuento,
                    "valor_total": total_linea,
                }
            )

        total_pagar = subtotal_general + iva_15 + iva_5
        abono = Decimal(header.get("abono") or 0)
        saldo = total_pagar - abono

        header_out = {
            "numero_factura": header.get("numero_factura"),
            "ruc_ci": header.get("ruc_ci"),
            "fecha_pedido": header.get("fecha_pedido"),
            "fecha_pago": header.get("fecha_pago"),
            "forma_pago": header.get("forma_pago"),
            "plazo_pago": header.get("plazo_pago"),
            "notas": header.get("notas"),
            "subtotal_general": subtotal_general,
            "subtotal_tarifa_15": subtotal_15,
            "subtotal_tarifa_5": subtotal_5,
            "subtotal_tarifa_0": subtotal_0,
            "descuento_total": descuento_total,
            "iva_15": iva_15,
            "iva_5": iva_5,
            "total_pagar": total_pagar,
            "abono": abono,
            "saldo": saldo,
            "elaborado_codigo": header.get("elaborado_codigo"),
            "elaborado_nombre": header.get("elaborado_nombre"),
            "autorizado_codigo": header.get("autorizado_codigo"),
            "autorizado_nombre": header.get("autorizado_nombre"),
            "recibido_codigo": header.get("recibido_codigo"),
            "recibido_nombre": header.get("recibido_nombre"),
            "estado": header.get("estado") or "borrador",
        }

        return {"header": header_out, "detalles": detalles_out}
