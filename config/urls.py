from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.medical import views as medical_api_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("apps.core.urls", "routes"), namespace="routes")),
    path("", include(("apps.accounts.urls", "user_html"), namespace="user_html")),
    path("productos/", include(("apps.inventory.urls", "product_html"), namespace="product_html")),
    path("ventas/", include(("apps.sales.urls", "sale_html"), namespace="sale_html")),
    path("medical/", include(("apps.medical.urls", "medical"), namespace="medical")),
    path("api/", include(("apps.api.urls", "api"), namespace="api")),
]

legacy_medical_api_patterns = [
    path("api/personas/", medical_api_views.api_get_personas),
    path("api/pacientes-medicos/", medical_api_views.api_pacientes_medicos),
    path("api/pacientes-medicos/search/", medical_api_views.api_search_pacientes_medicos),
    path("api/pacientes-medicos/<int:paciente_id>/", medical_api_views.api_get_paciente_medico),
    path(
        "api/pacientes-medicos/<int:paciente_id>/consultas/",
        medical_api_views.api_paciente_consultas,
    ),
    path("api/consultas/", medical_api_views.api_consultas),
    path("api/clientes/<int:cliente_id>/", medical_api_views.api_get_cliente),
    path("api/fichas-clinicas/", medical_api_views.api_fichas_clinicas),
    path("api/fichas-clinicas/<int:ficha_id>/", medical_api_views.api_ficha_clinica_by_id),
    path(
        "api/fichas-clinicas/<int:ficha_id>/examenes/",
        medical_api_views.api_examenes_por_ficha,
    ),
    path("api/biomicroscopia/<int:ficha_id>/", medical_api_views.api_biomicroscopia_detail),
    path("api/biomicroscopia/", medical_api_views.api_biomicroscopia_save),
]

urlpatterns += legacy_medical_api_patterns

legacy_medical_view_patterns = [
    path("pacientes-medicos/", medical_api_views.pacientes),
    path("pacientes-medicos/nuevo/", medical_api_views.nuevo_paciente),
    path("pacientes-medicos/<int:paciente_id>/", medical_api_views.ver_paciente),
    path("pacientes-medicos/<int:paciente_id>/editar/", medical_api_views.editar_paciente),
    path("pacientes-medicos/<int:paciente_id>/historial/", medical_api_views.historial_paciente),
    path("historial-paciente/<int:paciente_id>/", medical_api_views.historial_paciente),
    path("consultas/", medical_api_views.consultas),
    path("consultas-nuevo/", medical_api_views.consultas),
    path("consultas/<int:consulta_id>/", medical_api_views.ver_consulta),
    path("consultas/<int:consulta_id>/editar/", medical_api_views.editar_consulta),
]

urlpatterns += legacy_medical_view_patterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
