from __future__ import annotations

import json
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name="tojson")
def tojson(value, ensure_ascii: bool = False):
    """
    Serialize Python objects to JSON so templates coming from Flask
    (which used the `tojson` filter) keep working.
    """
    try:
        data = json.dumps(value, ensure_ascii=ensure_ascii)
    except TypeError:
        data = "null"
    return mark_safe(data)
