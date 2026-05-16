"""Adapter — OpenAI (stub, deprecated in favor of Gemini).

This adapter was the original Sprint 3 plan for semantic search using
GPT-4o-mini. The actual implementation uses Google Gemini 2 Flash via
`nlu_service.py`. This stub is preserved to satisfy the Adapter Pattern
interface but is NOT used in production.

See: `app/services/nlu_service.py` for the active NLU implementation.
"""

from app.adapters.base import IAIAdapter


class OpenAIAdapter(IAIAdapter):
    """Adaptador stub para la API de OpenAI (no utilizado).

    La implementación activa usa Google Gemini 2 Flash.
    Este stub se conserva para compatibilidad con el Adapter Pattern.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def semantic_search(self, query: str, context: dict) -> list[dict]:
        """Búsqueda semántica — no implementado (usar Gemini via nlu_service)."""
        raise NotImplementedError(
            "OpenAI adapter deprecated. Use nlu_service.py (Gemini 2 Flash) instead."
        )

    async def generate_recommendation(self, user_id: str) -> list[dict]:
        """Recomendaciones personalizadas — no implementado."""
        raise NotImplementedError(
            "OpenAI adapter deprecated. Use nlu_service.py (Gemini 2 Flash) instead."
        )
