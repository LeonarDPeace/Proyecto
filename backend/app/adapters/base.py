"""Interfaz abstracta — Patrón Adapter para servicios de IA.

Define el contrato que deben cumplir todos los adaptadores de IA.
Implementaciones concretas en Sprint 3 (OpenAI, Groq, modelos locales, etc.).

Ejemplo de uso futuro:
    adapter: IAIAdapter = OpenAIAdapter(api_key="...")
    results = await adapter.semantic_search("almuerzo casero", context={...})
"""

from abc import ABC, abstractmethod


class IAIAdapter(ABC):
    """Interfaz base para adaptadores de IA.

    Cualquier proveedor de IA (OpenAI, Groq, Ollama, etc.) debe
    implementar esta interfaz para ser intercambiable.
    """

    @abstractmethod
    async def semantic_search(self, query: str, context: dict) -> list[dict]:
        """Realiza una búsqueda semántica sobre el catálogo de productos.

        Args:
            query: Texto de búsqueda del usuario (ej: 'almuerzo barato').
            context: Metadata adicional (campus, categoría, ubicación, etc.).

        Returns:
            Lista de resultados rankeados por relevancia semántica.
        """
        ...

    @abstractmethod
    async def generate_recommendation(self, user_id: str) -> list[dict]:
        """Genera recomendaciones personalizadas para un usuario.

        Args:
            user_id: UUID del usuario.

        Returns:
            Lista de productos recomendados.
        """
        ...
