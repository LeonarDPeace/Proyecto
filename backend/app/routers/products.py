"""Router — Products (CRUD del catálogo P2P).

Endpoints RESTful para gestión de productos.
Sprint 0: Estructura base con stubs. Lógica completa en Sprint 1.
"""

from fastapi import APIRouter, status

from app.schemas.product import ProductCreate, ProductRead
from app.schemas.response import MessageResponse

router = APIRouter()


@router.get("/", response_model=list[ProductRead])
async def list_products():
    """Lista productos activos del catálogo.

    TODO (Sprint 1): Implementar con BD, paginación y filtros.
    """
    return []


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: str):
    """Obtiene el detalle de un producto por ID.

    TODO (Sprint 1): Implementar con BD.
    """
    return MessageResponse(message="Pendiente Sprint 1")


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(product: ProductCreate):
    """Crea un nuevo producto en el catálogo.

    Args:
        product: Datos del producto a crear.

    TODO (Sprint 1): Implementar con BD + autenticación.
    """
    return MessageResponse(
        message=f"Producto '{product.name}' — creación pendiente Sprint 1"
    )


@router.put("/{product_id}", response_model=MessageResponse)
async def update_product(product_id: str):
    """Actualiza un producto existente.

    TODO (Sprint 1): Implementar con BD + autorización (solo el dueño).
    """
    return MessageResponse(message="Actualización pendiente Sprint 1")


@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_product(product_id: str):
    """Elimina (soft-delete) un producto.

    TODO (Sprint 1): Implementar soft-delete (is_active = false).
    """
    return MessageResponse(message="Eliminación pendiente Sprint 1")
