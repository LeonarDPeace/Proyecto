"""Service — NLU con Gemini para normalizar consultas de búsqueda."""

import json
import re
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings


class NLUQueryResult(BaseModel):
    """Salida estructurada que alimenta la búsqueda en Typesense."""

    query_clean: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    category: str | None = None


def _extract_json_block(raw_text: str) -> dict[str, Any]:
    """Extrae JSON de la respuesta, incluso si hay texto adicional."""
    raw_text = raw_text.strip()

    if raw_text.startswith("{") and raw_text.endswith("}"):
        return json.loads(raw_text)

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("La respuesta NLU no contiene un objeto JSON válido")

    return json.loads(match.group(0))


def _normalize_tags(raw_tags: list[Any] | None) -> list[str]:
    if not raw_tags:
        return []

    seen: set[str] = set()
    tags: list[str] = []
    for item in raw_tags:
        if not isinstance(item, str):
            continue
        value = item.strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        tags.append(value)
    return tags


async def parse_semantic_query(user_query: str) -> NLUQueryResult:
    """Interpreta una consulta libre y devuelve JSON controlado para filtrado/search."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY no configurada")

    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
        f"?key={settings.GEMINI_API_KEY}"
    )

    prompt = (
        "Eres un normalizador de consultas para un gran marketplace. "
        "Responde SOLO con JSON válido y sin texto adicional. "
        "No inventes categorías fuera de: "
        "comida, tecnologia, moda, hogar, deportes, belleza, academico, entretenimiento, servicios, vehiculos, otros. "
        "Devuelve exactamente este esquema: "
        '{"query_clean":"...","tags":["..."],'
        '"category":"comida|tecnologia|moda|hogar|deportes|belleza|academico|entretenimiento|servicios|vehiculos|otros|null"}. '
        "Si no identificas la categoría principal, usa null. "
        "IMPORTANTE: Las subcategorías finas (ej. 'audífonos', 'snacks', 'pantalones') debes inyectarlas en el arreglo de 'tags'. "
        "Mantén query_clean corto y útil para búsqueda. "
        f"Consulta del usuario: {user_query}"
    )

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "topP": 0.1,
            "maxOutputTokens": 200,
            "response_mime_type": "application/json",
        },
    }

    timeout = httpx.Timeout(timeout=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Respuesta inesperada de Gemini") from exc

    parsed = _extract_json_block(raw_text)
    query_clean = str(parsed.get("query_clean", "")).strip() or user_query.strip()

    category_raw = parsed.get("category")
    category = (
        category_raw.strip().lower()
        if isinstance(category_raw, str) and category_raw.strip()
        else None
    )

    allowed_categories = {
        "comida",
        "tecnologia",
        "moda",
        "hogar",
        "deportes",
        "belleza",
        "academico",
        "entretenimiento",
        "servicios",
        "vehiculos",
        "otros",
    }
    if category not in allowed_categories:
        category = None

    return NLUQueryResult(
        query_clean=query_clean,
        tags=_normalize_tags(parsed.get("tags")),
        category=category,
    )
