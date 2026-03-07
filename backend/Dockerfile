# VeraMarket Backend — Dockerfile optimizado para Render.com
# Multi-stage build: base ligera + sin archivos innecesarios.

FROM python:3.11-slim AS base

# Evitar prompts interactivos y buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Bogota

WORKDIR /app

# Instalar dependencias del sistema (PostGIS client libs)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY ./app ./app

EXPOSE 8000

# Comando de ejecución — Render espera que el puerto esté en $PORT o 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
