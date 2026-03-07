"""VeraMarket — Utilidades de seguridad: JWT, hashing y OAuth.

Usa bcrypt para hashing de contraseñas y python-jose para JWT.
Los correos deben terminar en .edu.co (validación institucional).
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Genera un hash bcrypt de la contraseña."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crea un token JWT firmado.

    Args:
        data: Payload del token (debe incluir 'sub' con el user id).
        expires_delta: Duración personalizada; por defecto usa JWT_EXPIRATION_MINUTES.

    Returns:
        Token JWT codificado.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decodifica y valida un token JWT.

    Returns:
        Payload decodificado o None si el token es inválido/expirado.
    """
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Validación institucional
# ---------------------------------------------------------------------------


def is_institutional_email(email: str) -> bool:
    """Verifica que el correo pertenezca a un dominio institucional (.edu.co)."""
    return email.strip().lower().endswith(".edu.co")
