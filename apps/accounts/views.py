import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from .models import LegacyUser
from .services import LegacyUserService


user_service = LegacyUserService()
RESET_TOKEN_TTL = getattr(settings, "PASSWORD_RESET_TOKEN_TTL", 60 * 30)


def _reset_cache_key(token: str) -> str:
    return f"password-reset:{token}"


class LegacyLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        role = self.request.session.get("rol", "")
        if role == "Administrador":
            return reverse("product_html:dashboard")
        return reverse("routes:registrar_venta")


class LegacyLogoutView(LogoutView):
    next_page = reverse_lazy("user_html:login")

    def dispatch(self, request, *args, **kwargs):
        request.session.pop("legacy_user_id", None)
        request.session.pop("rol", None)
        return super().dispatch(request, *args, **kwargs)


def _require_admin(request):
    if request.session.get("rol") != "Administrador":
        messages.error(request, "Acceso denegado.")
        return redirect("user_html:login")
    return None


@login_required
def usuarios(request):
    redirect_response = _require_admin(request)
    if redirect_response:
        return redirect_response
    users = user_service.get_all_users()
    return render(request, "usuarios.html", {"users": users})


@login_required
def toggle_estado_usuario(request, usuario_id: int):
    redirect_response = _require_admin(request)
    if redirect_response:
        return redirect_response
    user = get_object_or_404(LegacyUser, usuario_id=usuario_id)
    user.estado = not user.estado
    user.save(update_fields=["estado"])
    messages.success(request, f"Estado del usuario {user.username} actualizado.")
    return redirect("user_html:usuarios")


@login_required
def editar_usuario(request, usuario_id: int):
    redirect_response = _require_admin(request)
    if redirect_response:
        return redirect_response
    if request.method != "POST":
        return redirect("user_html:usuarios")
    user_service.update_user(
        usuario_id,
        nombre=request.POST.get("nombre"),
        ap_pat=request.POST.get("ap_pat"),
        ap_mat=request.POST.get("ap_mat"),
        username=request.POST.get("username"),
        email=request.POST.get("email"),
    )
    messages.success(request, "Usuario actualizado correctamente.")
    return redirect("user_html:usuarios")


@login_required
def eliminar_usuario(request, usuario_id: int):
    redirect_response = _require_admin(request)
    if redirect_response:
        return redirect_response
    if request.method != "POST":
        return redirect("user_html:usuarios")
    exito = user_service.delete_user(usuario_id)
    if exito:
        messages.success(request, "Usuario eliminado físicamente.")
    else:
        messages.warning(
            request,
            "No se pudo eliminar (ventas asociadas). El usuario fue desactivado.",
        )
    return redirect("user_html:usuarios")


def request_reset(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        context["email"] = email

        if not email:
            messages.error(request, "Ingresa un correo electronico valido.")
        else:
            user = LegacyUser.objects.filter(email__iexact=email).first()
            messages.success(
                request,
                "Si el correo existe, recibiras un enlace para restablecer tu contrasena en los proximos minutos.",
            )
            if user:
                token = secrets.token_urlsafe(32)
                cache.set(_reset_cache_key(token), user.usuario_id, RESET_TOKEN_TTL)
                reset_url = request.build_absolute_uri(
                    reverse("user_html:reset_password", args=[token])
                )
                if settings.DEBUG:
                    context["debug_reset_link"] = reset_url

    return render(request, "request_reset.html", context)


def reset_password(request, token: str):
    cache_key = _reset_cache_key(token)
    user_id = cache.get(cache_key)
    if not user_id:
        messages.error(request, "El enlace de recuperacion no es valido o expiro.")
        return redirect("user_html:request_reset")

    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not password or not confirm_password:
            messages.error(request, "Debes ingresar y confirmar la nueva contrasena.")
        elif password != confirm_password:
            messages.error(request, "Las contrasenas no coinciden.")
        elif len(password) < 6:
            messages.error(request, "La contrasena debe tener al menos 6 caracteres.")
        else:
            user_service.update_user(user_id, password=password)
            cache.delete(cache_key)
            messages.success(request, "Tu contrasena fue actualizada. Ahora puedes iniciar sesion.")
            return redirect("user_html:login")

    return render(request, "reset_password.html")
