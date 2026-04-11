"""Adapter — OpenAI (stub para Sprint 3).

Implementará búsqueda semántica con GPT-4o-mini y embeddings.
Actualmente lanza NotImplementedError para todas las operaciones.
"""

from app.adapters.base import IAIAdapter


class OpenAIAdapter(IAIAdapter):
    """Adaptador para la API de OpenAI.

    Sprint 3: Conectará con GPT-4o-mini para búsqueda semántica
    y recomendaciones personalizadas.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def semantic_search(self, query: str, context: dict) -> list[dict]:
        """Búsqueda semántica — pendiente Sprint 3."""
        raise NotImplementedError(
            "OpenAI semantic_search será implementado en Sprint 3. Usa filtros tradicionales por ahora."
        )

    async def generate_recommendation(self, user_id: str) -> list[dict]:
        """Recomendaciones personalizadas — pendiente Sprint 3."""
        raise NotImplementedError(
            "OpenAI generate_recommendation será implementado en Sprint 3."
        )
