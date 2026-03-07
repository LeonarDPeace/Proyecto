"""VeraMarket API — Punto de entrada principal.

PWA de comercio P2P hiper-local para campus universitarios en Cali, Colombia.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, health, products, users


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="VeraMarket API",
    description=(
        "API REST para VeraMarket — Marketplace P2P hiper-local "
        "para campus universitarios en Cali, Colombia."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — Configuración dinámica según entorno
# ---------------------------------------------------------------------------
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------------------------------------------------------------------------
# Routers — Versionados bajo /api/v1
# ---------------------------------------------------------------------------
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
