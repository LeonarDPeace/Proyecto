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
    subcategory: str | None = None
    condition: str | None = None
    brand: str | None = None
    has_free_shipping: bool | None = None
    min_price: float | None = None
    max_price: float | None = None
    availability: str | None = None
    seller_rating_min: float | None = None
    seller_rating_max: float | None = None
    discount_only: bool | None = None
    warranty: str | None = None
    payment_methods: list[str] | None = None


def _extract_json_block(raw_text: str) -> dict[str, Any]:
    """Extrae JSON de la respuesta, incluso si hay texto adicional."""
    raw_text = raw_text.strip()

    def _safe_load(value: str) -> dict[str, Any]:
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("La respuesta NLU no contiene JSON valido") from exc

    if raw_text.startswith("{") and raw_text.endswith("}"):
        return _safe_load(raw_text)

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("La respuesta NLU no contiene un objeto JSON válido")

    return _safe_load(match.group(0))


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


def _normalize_optional_str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip().lower()
    return cleaned or None


def _coerce_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_prompt(user_query: str, ui_filters: dict[str, Any] | None) -> str:
    prompt = (
        "Eres un analizador semantico para un marketplace universitario estilo Amazon/MercadoLibre. "
        "Responde SOLO con JSON valido y sin texto adicional. "
        "Tu objetivo es extraer filtros especificos de la consulta del usuario. "
        "Devuelve exactamente este esquema JSON:\n"
        '{"query_clean": "str (consulta principal sin los filtros explicitos)", '
        '"category": "str | null (ej. tecnologia, moda, libros, etc)", '
        '"subcategory": "str | null", '
        '"condition": "str | null (nuevo, usado, reacondicionado)", '
        '"brand": "str | null", '
        '"has_free_shipping": "bool | null (true si pide envio gratis)", '
        '"min_price": "number | null", '
        '"max_price": "number | null", '
        '"availability": "str | null (in_stock)", '
        '"seller_rating_min": "number | null", '
        '"seller_rating_max": "number | null", '
        '"discount_only": "bool | null (true si pide con descuento)", '
        '"warranty": "str | null (has_warranty si pide con garantia)", '
        '"payment_methods": ["str"] | null, '
        '"tags": ["str", "str"]}\n'
        "Reglas:\n"
        "- Extrae la marca (brand) si se menciona explicitamente (ej. apple, nike, samsung).\n"
        "- Extrae condition si dicen 'usado', 'nuevo', 'segunda mano'.\n"
        "- Extrae min_price/max_price si dicen 'menos de X', 'entre X y Y'.\n"
        "- Extrae discount_only si mencionan 'descuento', 'oferta', 'rebaja'.\n"
        "- Extrae seller_rating_min si mencionan 'mejores vendedores', "
        "'confiables' (ej. 4.0).\n"
        "- query_clean debe ser el nombre base del producto a buscar, sin los filtros. "
        "Ej. 'busco un iphone usado barato' -> "
        "query_clean='iphone', condition='usado'.\n"
    )

    if ui_filters:
        filters_json = json.dumps(ui_filters, ensure_ascii=True)
        prompt += (
            "Filtros UI confirmados (no los contradigas, "
            "solo complementa si falta algo):\n"
            f"{filters_json}\n"
        )

    prompt += f"Consulta del usuario: {user_query}"
    return prompt


def _parse_nlu_payload(parsed: dict[str, Any], fallback_query: str) -> NLUQueryResult:
    query_clean = str(parsed.get("query_clean", "")).strip() or fallback_query.strip()

    payload = {
        "query_clean": query_clean,
        "tags": _normalize_tags(parsed.get("tags")),
        "category": _normalize_optional_str(parsed.get("category")),
        "subcategory": _normalize_optional_str(parsed.get("subcategory")),
        "condition": _normalize_optional_str(parsed.get("condition")),
        "brand": _normalize_optional_str(parsed.get("brand")),
        "has_free_shipping": _coerce_bool(parsed.get("has_free_shipping")),
        "min_price": _coerce_float(parsed.get("min_price")),
        "max_price": _coerce_float(parsed.get("max_price")),
        "availability": _normalize_optional_str(parsed.get("availability")),
        "seller_rating_min": _coerce_float(parsed.get("seller_rating_min")),
        "seller_rating_max": _coerce_float(parsed.get("seller_rating_max")),
        "discount_only": _coerce_bool(parsed.get("discount_only")),
        "warranty": _normalize_optional_str(parsed.get("warranty")),
        "payment_methods": _normalize_tags(parsed.get("payment_methods")),
    }

    return NLUQueryResult.model_validate(payload)


async def _execute_nlu(
    user_query: str, ui_filters: dict[str, Any] | None
) -> NLUQueryResult:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY no configurada")

    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
        f"?key={settings.GEMINI_API_KEY}"
    )

    prompt = _build_prompt(user_query, ui_filters)

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "topP": 0.1,
            "maxOutputTokens": 300,
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
    return _parse_nlu_payload(parsed, user_query)


async def parse_semantic_query(user_query: str) -> NLUQueryResult:
    """Interpreta una consulta libre y devuelve JSON controlado para filtrado/search."""
    return await _execute_nlu(user_query, None)


async def parse_semantic_query_with_filters(
    user_query: str, ui_filters: BaseModel | dict[str, Any]
) -> NLUQueryResult:
    """Interpreta consulta libre con filtros UI confirmados."""
    if isinstance(ui_filters, BaseModel):
        raw_filters = ui_filters.model_dump()
    else:
        raw_filters = dict(ui_filters)

    filters_payload = {
        key: value
        for key, value in raw_filters.items()
        if value not in (None, [], {}, "")
    }
    return await _execute_nlu(user_query, filters_payload)
