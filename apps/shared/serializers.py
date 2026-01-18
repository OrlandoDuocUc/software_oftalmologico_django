from datetime import date, datetime, time
from typing import Any, Dict

from django.db import models


def model_to_legacy_dict(instance: models.Model) -> Dict[str, Any]:
    """
    Convierte un modelo Django (generalmente managed=False) en un diccionario
    usando los nombres de columna heredados para mantener compatibilidad con
    las respuestas del sistema Flask.
    """
    data: Dict[str, Any] = {}
    for field in instance._meta.concrete_fields:
        value = getattr(instance, field.attname)
        if isinstance(value, (datetime, date, time)):
            data[field.attname] = value.isoformat()
        else:
            data[field.attname] = value
    return data


def sanitize_model_payload(model: type[models.Model], payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Devuelve un nuevo diccionario que sólo contiene los campos válidos
    definidos en el modelo indicado. Útil para operaciones de update_or_create.
    """
    allowed = {
        field.name
        for field in model._meta.get_fields()
        if isinstance(field, models.Field) and not field.auto_created and field.name not in {"id"}
    }
    clean: Dict[str, Any] = {}
    for key, value in (payload or {}).items():
        if key in allowed:
            clean[key] = value
    return clean
