from django.urls import path

from . import views

app_name = "sale_html"

urlpatterns = [
    path("registrar-venta/", views.registrar_venta_page, name="registrar_venta_page"),
    path("revisar-venta/", views.revisar_venta_page, name="revisar_venta_page"),
    path("finalizar-venta-definitiva/", views.finalizar_venta_definitiva, name="finalizar_venta_definitiva"),
    path("boleta/<int:venta_id>/", views.boleta_page, name="boleta_page"),
    path("historial-ventas/", views.historial_ventas_page, name="historial_ventas_page"),
    path("historial-ventas/exportar-excel/", views.exportar_historial_excel, name="exportar_historial_excel"),
]
