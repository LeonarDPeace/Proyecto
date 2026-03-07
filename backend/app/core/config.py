"""VeraMarket — Configuración centralizada con Pydantic Settings.

Las variables se cargan desde el archivo .env en la raíz de /backend.
NUNCA hardcodear secretos en el código.
"""

from pydantic_settings import BaseSettings


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

    # --- Integraciones (Sprint 3) ---
    OPENAI_API_KEY: str = ""
    SENTRY_DSN: str = ""

    # --- OAuth ---
    OAUTH_CLIENT_ID: str = ""
    OAUTH_CLIENT_SECRET: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
