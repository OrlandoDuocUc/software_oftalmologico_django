from __future__ import annotations

import json

from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from openpyxl import Workbook

from apps.inventory.services import ProductService

from .services import SaleService

product_service = ProductService()
sale_service = SaleService()


def _require_seller(request):
    if request.session.get("rol") not in ("Administrador", "Vendedor"):
        messages.error(request, "Acceso denegado.")
        return redirect("user_html:login")
    return None


def _serialize_products():
    data = []
    for product in product_service.list_products():
        price = product.costo_venta_1 or product.costo_unitario or 0
        data.append(
            {
                "producto_id": product.producto_id,
                "nombre": product.nombre,
                "precio_unitario": float(price),
                "codigo": product.codigo or "",
            }
        )
    return json.dumps(data, ensure_ascii=False)


@login_required
def registrar_venta_page(request: HttpRequest) -> HttpResponse:
    redirect_response = _require_seller(request)
    if redirect_response:
        return redirect_response
    products_json = _serialize_products()
    return render(
        request,
        "registrar_venta.html",
        {"products_json": products_json, "today": timezone.now().date().isoformat()},
    )


@login_required
def revisar_venta_page(request: HttpRequest) -> HttpResponse:
    redirect_response = _require_seller(request)
    if redirect_response:
        return redirect_response
    if request.method != "POST":
        return redirect("sale_html:registrar_venta_page")
    try:
        items = json.loads(request.POST.get("pedido_items", "[]"))
    except json.JSONDecodeError:
        items = []
    if not items:
        messages.warning(request, "Debes agregar al menos 1 producto antes de continuar.")
        return redirect("sale_html:registrar_venta_page")

    total_general = sum(float(item.get("total_linea", item.get("subtotal", 0))) for item in items)

    request.session["venta_header"] = {
        "numero_factura": request.POST.get("numero_factura") or "",
        "ciudad": request.POST.get("ciudad") or "",
        "observaciones": request.POST.get("observaciones") or "",
        "metodo_pago": request.POST.get("metodo_pago") or "efectivo",
        "abono": request.POST.get("abono") or "0",
    }
    request.session["venta_items"] = items
    request.session["venta_total"] = total_general
    return render(
        request,
        "confirmar_venta.html",
        {
            "items": items,
            "total_general": total_general,
            "header": request.session.get("venta_header", {}),
        },
    )


@login_required
def finalizar_venta_definitiva(request: HttpRequest) -> HttpResponse:
    redirect_response = _require_seller(request)
    if redirect_response:
        return redirect_response
    if request.method != "POST":
        return redirect("sale_html:registrar_venta_page")

    items = request.session.get("venta_items", [])
    if not items:
        messages.warning(request, "No hay ítems cargados para finalizar la venta.")
        return redirect("sale_html:registrar_venta_page")

    usuario_id = request.session.get("legacy_user_id")
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión nuevamente.")
        return redirect("user_html:login")

    cliente_data = {
        "rut": request.POST.get("cliente_rut") or "",
        "nombres": request.POST.get("cliente_nombres") or "",
        "ap_pat": request.POST.get("cliente_ap_pat") or "",
        "ap_mat": request.POST.get("cliente_ap_mat") or "",
        "telefono": request.POST.get("cliente_telefono") or "",
        "email": request.POST.get("cliente_email") or "",
        "direccion": request.POST.get("cliente_direccion") or "",
    }
    header_session = request.session.get("venta_header", {})

    metodo_pago = request.POST.get("metodo_pago") or header_session.get("metodo_pago") or "efectivo"
    numero_factura = request.POST.get("numero_factura") or header_session.get("numero_factura") or ""
    ciudad = request.POST.get("ciudad") or header_session.get("ciudad") or ""
    observaciones = request.POST.get("observaciones") or header_session.get("observaciones") or ""
    abono = request.POST.get("abono") or header_session.get("abono") or 0

    try:
        venta_id = sale_service.register_sale_from_cart(
            cart_items=items,
            usuario_id=usuario_id,
            cliente_data=cliente_data,
            metodo_pago=metodo_pago,
            observaciones=observaciones,
            numero_factura=numero_factura,
            ciudad=ciudad,
            abono=abono,
        )
    except Exception as exc:
        messages.error(request, f"Error al finalizar la venta: {exc}")
        return redirect("sale_html:registrar_venta_page")

    request.session.pop("venta_items", None)
    request.session.pop("venta_total", None)
    request.session.pop("venta_header", None)

    return redirect("sale_html:boleta_page", venta_id=venta_id)


@login_required
def boleta_page(request: HttpRequest, venta_id: int) -> HttpResponse:
    redirect_response = _require_seller(request)
    if redirect_response:
        return redirect_response
    venta = sale_service.get_sale_details_for_receipt(venta_id)
    if not venta:
        messages.warning(request, "Venta no encontrada.")
        return redirect("sale_html:registrar_venta_page")
    return render(request, "boleta.html", {"venta": venta})


@login_required
def historial_ventas_page(request: HttpRequest) -> HttpResponse:
    redirect_response = _require_seller(request)
    if redirect_response:
        return redirect_response
    ventas = sale_service.get_all_sales_with_details()
    return render(request, "historial_ventas.html", {"ventas": ventas})


@login_required
@csrf_exempt
def exportar_historial_excel(request: HttpRequest) -> HttpResponse:
    redirect_response = _require_seller(request)
    if redirect_response:
        return redirect_response

    ventas = sale_service.get_all_sales_with_details()

    wb = Workbook()
    ws = wb.active
    ws.title = "Historial de Ventas"

    headers = [
        "ID Venta",
        "Fecha",
        "Cliente",
        "Producto",
        "Cantidad",
        "Precio Unitario",
        "Subtotal",
        "Total Venta",
        "Vendedor",
        "Método de Pago",
        "Estado",
    ]
    ws.append(headers)

    for venta in ventas:
        cliente_nombre = (
            f"{venta.cliente.nombres} {venta.cliente.ap_pat or ''}".strip()
            if venta.cliente
            else ""
        )
        vendedor = venta.usuario.username if venta.usuario else ""
        fecha = venta.fecha_venta.strftime("%d/%m/%Y %H:%M") if venta.fecha_venta else ""
        for det in venta.detalles.all():
            ws.append(
                [
                    venta.venta_id,
                    fecha,
                    cliente_nombre,
                    det.producto.nombre if det.producto else "",
                    det.cantidad or 0,
                    float(det.precio_unitario or 0),
                    float(det.subtotal or 0),
                    float(venta.total or 0),
                    vendedor,
                    venta.metodo_pago or "",
                    venta.estado or "",
                ]
            )

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="historial_ventas.xlsx"'
    )
    return response
