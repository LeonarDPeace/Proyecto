"""Service — Email / OTP (HU 1.1).

Genera y envía códigos OTP al correo institucional del usuario.
En entorno de desarrollo, imprime el OTP en consola sin enviar email.
"""

import random
import string
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage

import aiosmtplib
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.otp import OTPCode


def _generate_otp(length: int | None = None) -> str:
    """Genera un código OTP numérico aleatorio."""
    otp_len = length or settings.OTP_LENGTH
    return "".join(random.choices(string.digits, k=otp_len))


async def create_otp(db: AsyncSession, email: str) -> OTPCode:
    """Crea un nuevo código OTP para un email.

    Invalida cualquier OTP activo previo del mismo email.

    Args:
        db: Sesión de base de datos.
        email: Correo institucional del usuario.

    Returns:
        El OTPCode creado.
    """
    # Invalidar OTPs previos no usados de este email
    await db.execute(
        update(OTPCode)
        .where(OTPCode.email == email, OTPCode.is_used == False)  # noqa: E712
        .values(is_used=True)
    )

    code = _generate_otp()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)

    otp = OTPCode(
        email=email,
        code=code,
        expires_at=expires_at,
    )
    db.add(otp)
    await db.flush()

    return otp


async def verify_otp(db: AsyncSession, email: str, code: str) -> bool:
    """Verifica un código OTP.

    Incrementa el contador de intentos en cada verificación.
    Marca el OTP como usado si es correcto.

    Args:
        db: Sesión de base de datos.
        email: Correo del usuario.
        code: Código OTP ingresado.

    Returns:
        True si el código es válido; False en caso contrario.
    """
    result = await db.execute(
        select(OTPCode)
        .where(
            OTPCode.email == email,
            OTPCode.is_used == False,  # noqa: E712
            OTPCode.expires_at > datetime.now(UTC),
        )
        .order_by(OTPCode.created_at.desc())
        .limit(1)
    )
    otp = result.scalar_one_or_none()

    if not otp:
        return False

    # Incrementar intentos
    otp.attempts += 1

    if otp.attempts >= 3:
        otp.is_used = True  # Bloquear tras 3 intentos
        await db.flush()
        return False

    if otp.code != code:
        await db.flush()
        return False

    # Código correcto — marcar como usado
    otp.is_used = True
    await db.flush()
    return True


async def send_otp_email(email: str, code: str) -> None:
    """Envía el código OTP por email.

    En desarrollo, imprime el código en consola.
    En producción, envía vía SMTP.

    Args:
        email: Correo destino.
        code: Código OTP a enviar.
    """
    if settings.ENVIRONMENT == "development" or not settings.SMTP_USER:
        print(f"\n{'=' * 50}")
        print(f"📧 OTP para {email}: {code}")
        print(f"{'=' * 50}\n")
        return

    msg = EmailMessage()
    msg["Subject"] = f"VeraMarket — Tu código de acceso: {code}"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = email
    msg.set_content(
        f"Hola,\n\n"
        f"Tu código de acceso a VeraMarket es: {code}\n\n"
        f"Este código expira en {settings.OTP_EXPIRATION_MINUTES} minutos.\n"
        f"Si no solicitaste este código, ignora este mensaje.\n\n"
        f"— Equipo VeraMarket 🛒"
    )
    msg.add_alternative(
        f"""
        <html>
        <body style="font-family: 'Inter', Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #2563eb; margin: 0;">Vera<span style="color: #3b82f6;">Market</span></h1>
            </div>
            <div style="background: #f8fafc; border-radius: 12px; padding: 30px; text-align: center;">
                <p style="color: #475569; margin-top: 0;">Tu código de acceso es:</p>
                <div style="font-size: 32px; font-weight: 700; letter-spacing: 8px; color: #1e293b; margin: 20px 0;">
                    {code}
                </div>
                <p style="color: #94a3b8; font-size: 14px;">
                    Expira en {settings.OTP_EXPIRATION_MINUTES} minutos
                </p>
            </div>
            <p style="color: #94a3b8; font-size: 12px; text-align: center; margin-top: 20px;">
                Si no solicitaste este código, ignora este mensaje.
            </p>
        </body>
        </html>
        """,
        subtype="html",
    )

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )


async def send_transactional_email(email: str, subject: str, body: str) -> None:
    """Envía un correo transaccional (HU 8.2 — notificaciones de estado de pedido).

    En desarrollo, imprime en consola. En producción, envía vía SMTP.
    """
    if settings.ENVIRONMENT == "development" or not settings.SMTP_USER:
        print(f"\n{'=' * 50}")
        print(f"📧 [{subject}] → {email}")
        print(f"   {body}")
        print(f"{'=' * 50}\n")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = email
    msg.set_content(body)
    msg.add_alternative(
        f"""
        <html>
        <body style="font-family: 'Inter', Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #2563eb; margin: 0;">Vera<span style="color: #3b82f6;">Market</span></h1>
            </div>
            <div style="background: #f8fafc; border-radius: 12px; padding: 30px; text-align: center;">
                <h2 style="color: #1e293b; margin-top: 0;">{subject}</h2>
                <p style="color: #475569;">{body}</p>
            </div>
            <p style="color: #94a3b8; font-size: 12px; text-align: center; margin-top: 20px;">
                — Equipo VeraMarket 🛒
            </p>
        </body>
        </html>
        """,
        subtype="html",
    )

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
