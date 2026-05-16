"""Servicio de validación de códigos Sinapsis y gestión del rol vendedor."""

import csv
import logging
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)


def load_sinapsis_whitelist(csv_path: str | Path | None = None) -> dict[str, str]:
    """Lee el CSV de Sinapsis y retorna un dict {codigo: email} válidos.

    Solo se incluyen los registros con estado 'activo'.
    """
    if csv_path is None:
        csv_path = settings.SINAPSIS_CSV_PATH

    path = Path(csv_path)
    valid_map = {}

    if not path.exists():
        logger.warning(f"Archivo Sinapsis CSV no encontrado en: {path}")
        return valid_map

    try:
        with open(path, encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                codigo = row.get("codigo", "").strip()
                email = row.get("email", "").strip().lower()
                estado = row.get("estado", "").strip().lower()

                if codigo and email and estado == "activo":
                    valid_map[codigo] = email

    except Exception as e:
        logger.error(f"Error cargando Sinapsis CSV: {e}")

    return valid_map


async def request_vendor_role(
    db: AsyncSession, user: User, sinapsis_code: str
) -> tuple[str, str]:
    """Valida el código Sinapsis y el EMAIL del usuario.
    
    Ambos deben coincidir con la base de datos de Sinapsis para otorgar el rol.
    """
    code = sinapsis_code.strip()

    if user.role == "vendedor" or user.vendor_status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene el rol de vendedor aprobado.",
        )

    valid_map = load_sinapsis_whitelist()

    # 1. Verificar si el código existe y está activo
    if code not in valid_map:
        user.vendor_status = "rejected"
        user.sinapsis_code = code
        await db.commit()
        await db.refresh(user)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código Sinapsis inválido o inactivo.",
        )

    # 2. Verificar si el email del usuario coincide con el del código
    expected_email = valid_map[code]
    if user.email.lower() != expected_email:
        user.vendor_status = "rejected"
        user.sinapsis_code = code
        await db.commit()
        await db.refresh(user)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Este código pertenece a {expected_email}. Tu correo no está autorizado.",
        )

    # Código y Email válidos: transicionar a vendedor
    user.role = "vendedor"
    user.vendor_status = "approved"
    user.sinapsis_code = code

    await db.commit()
    await db.refresh(user)

    return user.vendor_status, user.role
