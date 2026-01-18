from django.conf import settings
from django.urls import NoReverseMatch, reverse


ALIAS_MAP = {
    "proveedores:lista_proveedores": "product_html:lista_proveedores",
}


def flask_url_for(name: str, **kwargs):
    """
    Interpreta los nombres estilo Flask (blueprint.view) y los convierte
    en namespaces de Django (blueprint:view).
    """
    if "." in name:
        django_name = name.replace(".", ":")
    else:
        django_name = name

    django_name = ALIAS_MAP.get(django_name, django_name)

    try:
        return reverse(django_name, kwargs=kwargs)
    except NoReverseMatch:
        # Último recurso: intenta con el nombre original
        try:
            return reverse(name, kwargs=kwargs)
        except NoReverseMatch:
            return "#"


def global_settings(request):
    """
    Expose commonly-used settings to all templates.
    """
    return {
        "PROJECT_NAME": "Oftalmetyc",
        "DEBUG": settings.DEBUG,
        "session": request.session,
        "url_for": flask_url_for,
    }
