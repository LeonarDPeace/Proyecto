"""VeraMarket — Configuración centralizada con Pydantic Settings.

Las variables se cargan desde el archivo .env en la raíz de /backend.
NUNCA hardcodear secretos en el código.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de entorno de la aplicación."""

    # --- Base de Datos ---
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/veramarket"

    # --- Seguridad / JWT ---
    JWT_SECRET: str = "CHANGE-ME"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 horas

    # --- CORS ---
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- Entorno ---
    ENVIRONMENT: str = "development"
    TZ: str = "America/Bogota"

    # --- Email / OTP (Sprint 1 — HU 1.1) ---
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@veramarket.co"
    OTP_EXPIRATION_MINUTES: int = 10
    OTP_LENGTH: int = 6

    # --- Integraciones (Sprint 3) ---
    OPENAI_API_KEY: str = ""
    SENTRY_DSN: str = ""

    # --- OAuth ---
    OAUTH_CLIENT_ID: str = ""
    OAUTH_CLIENT_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
