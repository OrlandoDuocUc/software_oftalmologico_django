from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from decimal import Decimal

from apps.inventory.services import ProductService
from apps.sales.services import SaleService

product_service = ProductService()
sale_service = SaleService()


def _attach_precio_iva(productos):
    iva_factor = Decimal("1.15")
    for p in productos:
        base = p.costo_unitario or Decimal(0)
        p.precio_iva = (base * iva_factor).quantize(Decimal("0.01"))
    return productos


@login_required
def home(request):
    role = request.session.get("rol")
    if role == "Administrador":
        return redirect("product_html:dashboard")
    return redirect("sale_html:registrar_venta_page")


@login_required
def inventario(request):
    products = list(product_service.list_products(include_deleted=True))
    _attach_precio_iva(products)
    total_stock = sum(p.cantidad or 0 for p in products)
    stock_bajo = len([p for p in products if (p.cantidad or 0) < 10])
    categorias = sorted({p.tipo_armazon for p in products if p.tipo_armazon})
    marcas = sorted({p.marca for p in products if p.marca})
    stats = {
        "total_productos": len(products),
        "total_stock": total_stock,
        "stock_bajo": stock_bajo,
        "categorias": len(categorias),
    }
    return render(
        request,
        "inventario.html",
        {
        "productos": products,
        "stats": stats,
        "categorias": categorias,
        "marcas": marcas,
    },
)


@login_required
def registrar_venta_redirect(request):
    if request.session.get("rol") not in ("Administrador", "Vendedor"):
        messages.error(request, "Acceso denegado.")
        return redirect("user_html:login")
    return redirect("sale_html:registrar_venta_page")


@login_required
def historial_ventas_redirect(request):
    if request.session.get("rol") not in ("Administrador", "Vendedor"):
        messages.error(request, "Acceso denegado.")
        return redirect("user_html:login")
    return redirect("sale_html:historial_ventas_page")


@login_required
def dashboard(request):
    productos = list(product_service.list_products(include_deleted=False))
    _attach_precio_iva(productos)
    ventas = list(sale_service.get_all_sales_with_details()[:5])
    return render(
        request,
        "dashboard.html",
        {
            "productos_en_stock": len(productos),
            "total_ventas_hoy": 0,
            "ventas_recientes": ventas,
        },
    )
