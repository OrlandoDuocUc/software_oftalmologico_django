from django.urls import path

from . import views

app_name = "product_html"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.productos, name="productos"),
    path("eliminados/", views.productos_eliminados, name="productos_eliminados"),
    path("edit/<int:product_id>/", views.editar_producto, name="editar_producto"),
    path("delete/<int:product_id>/", views.eliminar_producto, name="eliminar_producto"),
    path("restore/<int:product_id>/", views.restaurar_producto, name="restaurar_producto"),
    path("proveedores/", views.lista_proveedores, name="lista_proveedores"),
    path("exportar-excel/", views.exportar_inventario_excel, name="exportar_inventario_excel"),
    path("compras/", views.compras, name="compras"),
    path("compras/<int:compra_id>/", views.detalle_compra, name="detalle_compra"),
    path("compras/exportar-excel/", views.exportar_compras_excel, name="exportar_compras_excel"),
]
