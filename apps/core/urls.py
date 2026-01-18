from django.urls import path

from . import views

app_name = "routes"

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.home, name="health"),
    path("inventario/", views.inventario, name="inventario"),
    path("registrar-venta/", views.registrar_venta_redirect, name="registrar_venta"),
    path("historial-ventas/", views.historial_ventas_redirect, name="historial_ventas"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
