"""Servicio de validación de códigos Sinapsis y gestión del rol vendedor."""

import csv
import logging
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)


def load_sinapsis_whitelist(csv_path: str | Path | None = None) -> set[str]:
    """Lee el CSV de Sinapsis y retorna un set con los códigos válidos.

    Solo se incluyen los códigos con estado 'activo'.
    """
    if csv_path is None:
        csv_path = settings.SINAPSIS_CSV_PATH

    path = Path(csv_path)
    valid_codes = set()

    if not path.exists():
        logger.warning(f"Archivo Sinapsis CSV no encontrado en: {path}")
        return valid_codes

    try:
        with open(path, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                codigo = row.get("codigo", "").strip()
                estado = row.get("estado", "").strip().lower()

                if codigo and estado == "activo":
                    valid_codes.add(codigo)

    except Exception as e:
        logger.error(f"Error cargando Sinapsis CSV: {e}")

    return valid_codes


async def request_vendor_role(
    db: AsyncSession, user: User, sinapsis_code: str
) -> tuple[str, str]:
    """Valida el código Sinapsis del usuario y cambia su rol a vendedor si es válido.

    Args:
        db: Sesión de BD asíncrona.
        user: El usuario autenticado que solicita el rol.
        sinapsis_code: El código que ingresó el usuario.

    Returns:
        Tupla (status_code de la operación, nuevo rol).

    Raises:
        HTTPException si el código es inválido.
    """
    code = sinapsis_code.strip()

    if user.role == "vendedor" or user.vendor_status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene el rol de vendedor aprobado.",
        )

    valid_codes = load_sinapsis_whitelist()

    if code not in valid_codes:
        user.vendor_status = "rejected"
        user.sinapsis_code = code
        await db.commit()
        await db.refresh(user)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código Sinapsis inválido o inactivo.",
        )

    # Código válido: transicionar a vendedor
    user.role = "vendedor"
    user.vendor_status = "approved"
    user.sinapsis_code = code

    await db.commit()
    await db.refresh(user)

    return user.vendor_status, user.role
