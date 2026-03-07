"""Service — Lógica de negocio para Productos.

Separa la lógica de los routers para facilitar testing y reutilización.
Sprint 0: Estructura base. Implementación completa en Sprint 1.
"""


async def get_active_products(limit: int = 20, offset: int = 0) -> list:
    """Obtiene productos activos con paginación.

    Args:
        limit: Máximo de resultados por página.
        offset: Desplazamiento para paginación.

    Returns:
        Lista de productos activos.

    TODO (Sprint 1): Implementar query a BD con filtros.
    """
    return []


async def get_products_by_campus(
    campus: str, lat: float, lng: float, radius_meters: int = 500
) -> list:
    """Busca productos de vendedores cercanos a una coordenada.

    Usa PostGIS ST_DWithin para queries geoespaciales.

    Args:
        campus: Nombre del campus (ej: 'UAO').
        lat: Latitud del punto de búsqueda.
        lng: Longitud del punto de búsqueda.
        radius_meters: Radio de búsqueda en metros.

    Returns:
        Lista de productos dentro del radio.

    TODO (Sprint 1): Implementar query geoespacial con PostGIS.
    """
    return []
