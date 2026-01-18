from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


def _format_amount(amount: Decimal) -> str:
    """
    Format numbers using Chilean-style separators (dot for thousands, comma for decimals).
    """
    formatted = f"{amount:,.2f}"
    # Replace thousands/decimal separators so 12,345.67 -> 12.345,67
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


@register.filter(name="currency")
def currency(value, symbol: str = "$") -> str:
    """
    Render numeric values as currency strings (default CLP style).
    """
    if value in (None, ""):
        return f"{symbol}0"

    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return f"{symbol}0"

    return f"{symbol}{_format_amount(amount)}"
