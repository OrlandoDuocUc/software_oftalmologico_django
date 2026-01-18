from django.urls import path

from .views import (
    LegacyLoginView,
    LegacyLogoutView,
    editar_usuario,
    eliminar_usuario,
    request_reset,
    reset_password,
    toggle_estado_usuario,
    usuarios,
)

app_name = "user_html"

urlpatterns = [
    path("login/", LegacyLoginView.as_view(), name="login"),
    path("logout/", LegacyLogoutView.as_view(), name="logout"),
    path("usuarios/", usuarios, name="usuarios"),
    path("usuarios/toggle/<int:usuario_id>/", toggle_estado_usuario, name="toggle_estado_usuario"),
    path("usuarios/edit/<int:usuario_id>/", editar_usuario, name="editar_usuario"),
    path("usuarios/delete/<int:usuario_id>/", eliminar_usuario, name="eliminar_usuario"),
    path("reset-password/", request_reset, name="request_reset"),
    path("reset-password/<str:token>/", reset_password, name="reset_password"),
]
