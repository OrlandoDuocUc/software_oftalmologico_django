from django.urls import path

from . import views

app_name = "medical"

urlpatterns = [
    path("pacientes-medicos/", views.pacientes, name="pacientes"),
    path("pacientes/nuevo/", views.nuevo_paciente, name="nuevo_paciente"),
    # Alias sin prefijo "medical" usado por templates legacy
    path("pacientes/nuevo", views.nuevo_paciente),
    path("pacientes/<int:paciente_id>/", views.ver_paciente, name="ver_paciente"),
    path("pacientes/<int:paciente_id>/editar/", views.editar_paciente, name="editar_paciente"),
    # Alias para rutas legacy /medical/pacientes-medicos/<id>/editar/
    path(
        "pacientes-medicos/<int:paciente_id>/editar/",
        views.editar_paciente,
        name="editar_paciente_medico",
    ),
    path(
        "pacientes-medicos/<int:paciente_id>/historial/",
        views.historial_paciente,
        name="historial_paciente",
    ),
    path("consultas-nuevo/", views.consultas, name="consultas"),
    path("consultas/nueva/", views.nueva_consulta, name="nueva_consulta"),
    path("consultas/<int:consulta_id>/", views.ver_consulta, name="ver_consulta"),
    path("consultas/<int:consulta_id>/editar/", views.editar_consulta, name="editar_consulta"),
    path("dashboard-medico/", views.dashboard_medico, name="dashboard_medico"),
    path("ficha-clinica-nuevo/", views.ficha_clinica_view, name="ficha_clinica"),
    path("biomicroscopia-nuevo/", views.biomicroscopia_nuevo, name="biomicroscopia_nuevo"),
    path("certificado/<int:consulta_id>/", views.certificado_view, name="certificado"),
    path(
        "examen-oftalmologico/<int:consulta_id>/",
        views.examen_oftalmologico_view,
        name="examen_oftalmologico",
    ),
    path("api/fichas-clinicas/", views.api_fichas_clinicas, name="api_fichas_clinicas"),
    path("api/fichas-clinicas/<int:ficha_id>/", views.api_ficha_clinica_by_id, name="api_ficha_clinica_by_id"),
    path(
        "api/fichas-clinicas/<int:ficha_id>/examenes/",
        views.api_examenes_por_ficha,
        name="api_examenes_por_ficha",
    ),
    path("api/biomicroscopia/<int:ficha_id>/", views.api_biomicroscopia_detail, name="api_biomicroscopia_detail"),
    path("api/biomicroscopia/", views.api_biomicroscopia_save, name="api_biomicroscopia_save"),
    path("api/personas/", views.api_get_personas, name="api_personas"),
    path("api/clientes/<int:cliente_id>/", views.api_get_cliente, name="api_cliente"),
    path("api/pacientes-medicos/", views.api_pacientes_medicos, name="api_pacientes_medicos"),
    # Alias legacy por peticiones relativas mal formadas desde editar_paciente
    path("api/pacientes-medicos/pacientes-medicos/", views.api_pacientes_medicos),
    path(
        "api/pacientes-medicos/<int:paciente_id>/",
        views.api_get_paciente_medico,
        name="api_get_paciente_medico",
    ),
    path("api/consultas/", views.api_consultas, name="api_consultas"),
    path("api/pacientes-medicos/search/", views.api_search_pacientes_medicos, name="api_search_pacientes_medicos"),
    path(
        "api/pacientes-medicos/<int:paciente_id>/consultas/",
        views.api_paciente_consultas,
        name="api_paciente_consultas",
    ),
]
