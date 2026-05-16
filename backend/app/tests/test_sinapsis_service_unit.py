"""Tests — Sinapsis Service.

Cobertura de:
- load_sinapsis_whitelist (file not found, error parsing, successful read)
- request_vendor_role (invalid code, valid code but wrong email)
"""

import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from fastapi import HTTPException

from app.models.user import User
from app.services import sinapsis_service


def test_load_sinapsis_whitelist_not_found():
    """Retorna dict vacío si no existe el CSV."""
    with patch("pathlib.Path.exists", return_value=False):
        result = sinapsis_service.load_sinapsis_whitelist("fake_path.csv")
        assert result == {}


def test_load_sinapsis_whitelist_success():
    """Lee el CSV y retorna dict con códigos activos."""
    csv_content = "codigo,email,estado\nVAL-123,test@uao.edu.co,activo\nVAL-999,test2@uao.edu.co,inactivo\n"
    with patch("pathlib.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=csv_content)):
            result = sinapsis_service.load_sinapsis_whitelist("fake_path.csv")
            assert "VAL-123" in result
            assert result["VAL-123"] == "test@uao.edu.co"
            assert "VAL-999" not in result


def test_load_sinapsis_whitelist_exception():
    """Maneja excepciones al leer."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch("builtins.open", side_effect=Exception("Read error")):
            result = sinapsis_service.load_sinapsis_whitelist("fake_path.csv")
            assert result == {}


@pytest.mark.asyncio
async def test_request_vendor_role_invalid_code():
    """Rechaza si el código no está en el dict (o inactivo)."""
    db = AsyncMock()
    user = MagicMock(spec=User)
    user.role = "comprador"
    user.vendor_status = "pending"
    user.email = "test@uao.edu.co"

    with patch("app.services.sinapsis_service.load_sinapsis_whitelist") as mock_load:
        mock_load.return_value = {"VAL-123": "test@uao.edu.co"}
        with pytest.raises(HTTPException) as exc:
            await sinapsis_service.request_vendor_role(db, user, "INVALID")
        assert exc.value.status_code == 400
        assert user.vendor_status == "rejected"


@pytest.mark.asyncio
async def test_request_vendor_role_wrong_email():
    """Rechaza si el email del usuario no coincide con el del CSV."""
    db = AsyncMock()
    user = MagicMock(spec=User)
    user.role = "comprador"
    user.vendor_status = "pending"
    user.email = "hacker@uao.edu.co"

    with patch("app.services.sinapsis_service.load_sinapsis_whitelist") as mock_load:
        mock_load.return_value = {"VAL-123": "test@uao.edu.co"}
        with pytest.raises(HTTPException) as exc:
            await sinapsis_service.request_vendor_role(db, user, "VAL-123")
        assert exc.value.status_code == 403
        assert user.vendor_status == "rejected"
