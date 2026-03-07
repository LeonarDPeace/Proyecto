"""Utilidades de validación compartidas."""

import re
import uuid


def is_valid_uuid(value: str) -> bool:
    """Verifica si un string es un UUID v4 válido."""
    try:
        uuid.UUID(value, version=4)
        return True
    except ValueError:
        return False


def is_valid_colombian_phone(phone: str) -> bool:
    """Valida un número de teléfono colombiano (10 dígitos, empieza con 3)."""
    pattern = r"^3\d{9}$"
    return bool(re.match(pattern, phone.strip()))


def sanitize_string(value: str) -> str:
    """Limpia un string de caracteres potencialmente peligrosos (XSS básico)."""
    return value.replace("<", "&lt;").replace(">", "&gt;").strip()
