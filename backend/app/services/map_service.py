"""Service — Lógica de geolocalización con OpenStreetMap / PostGIS.

Sprint 0: Estructura base. Implementación completa en Sprint 1.
Coordenadas por defecto: UAO, Cali (3.3516, -76.5320).
"""

# Coordenadas del campus piloto
UAO_LAT = 3.3516
UAO_LNG = -76.5320
DEFAULT_CAMPUS = "UAO"


async def get_nearby_sellers(
    lat: float = UAO_LAT,
    lng: float = UAO_LNG,
    radius_meters: int = 500,
) -> list:
    """Busca vendedores cercanos a una coordenada.

    Usa PostGIS ST_DWithin para delimitar el radio.

    Args:
        lat: Latitud del punto de búsqueda.
        lng: Longitud del punto de búsqueda.
        radius_meters: Radio de búsqueda en metros.

    Returns:
        Lista de vendedores dentro del radio.

    TODO (Sprint 1): Implementar con SQLAlchemy + GeoAlchemy2.
    """
    return []
