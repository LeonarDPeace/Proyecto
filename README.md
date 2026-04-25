# VeraMarket

**Marketplace universitario geolocalizado** para la compra y venta de productos entre estudiantes, con mapa interactivo del campus, negociación directa y recomendaciones por IA.

> Campus piloto: **Universidad Autónoma de Occidente (UAO)** — Cali, Colombia 🇨🇴

---

## Tabla de contenidos

- [VeraMarket](#veramarket)
  - [Tabla de contenidos](#tabla-de-contenidos)
  - [Stack tecnológico](#stack-tecnológico)
  - [Estructura del monorepo](#estructura-del-monorepo)
  - [Requisitos previos](#requisitos-previos)
  - [Instalación y desarrollo local](#instalación-y-desarrollo-local)
    - [Opción 1 — Docker Compose (recomendada)](#opción-1--docker-compose-recomendada)
    - [Opción 2 — Manual](#opción-2--manual)
      - [Backend](#backend)
      - [Frontend](#frontend)
  - [Variables de entorno](#variables-de-entorno)
  - [Flujo de trabajo Git](#flujo-de-trabajo-git)
    - [Convención de commits](#convención-de-commits)
  - [CI/CD](#cicd)
  - [Despliegue](#despliegue)
    - [Configuración Cloudflare](#configuración-cloudflare)
  - [Roadmap](#roadmap)
  - [Licencia](#licencia)
  - [👥 Equipo](#-equipo)

---

## Stack tecnológico

| Capa          | Tecnología                                      |
|---------------|--------------------------------------------------|
| **Frontend**  | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| **Estado**    | Zustand                                          |
| **Mapa**      | Leaflet.js + OpenStreetMap                       |
| **PWA**       | @ducanh2912/next-pwa                             |
| **Backend**   | FastAPI (Python 3.11+), Pydantic v2              |
| **Búsqueda**  | Typesense 27 (Full-Text + Facets + GeoSearch)    |
| **NLU**       | Gemini 1.5 Flash (JSON estructurado)             |
| **ORM**       | SQLAlchemy 2.0 (async) + Alembic                 |
| **Base de datos** | PostgreSQL 15 + PostGIS                      |
| **Auth**      | JWT (python-jose) + bcrypt                       |
| **CI/CD**     | GitHub Actions                                   |
| **Deploy**    | Vercel (frontend) · Render.com (backend) · Supabase/Neon (DB) |
| **DNS/SSL**   | Cloudflare (Free Tier)                           |

---

## Estructura del monorepo

```
Proyecto/
├── .github/
│   ├── workflows/ci-cd.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/
│   ├── app/
│   │   ├── adapters/          # Adapter Pattern para IA
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # SQLAlchemy 2.0 models
│   │   ├── routers/           # FastAPI endpoints
│   │   ├── schemas/           # Pydantic v2 schemas
│   │   ├── services/          # Lógica de negocio
│   │   ├── tests/             # pytest
│   │   ├── utils/             # Validators, helpers
│   │   └── main.py            # Entry point
│   ├── alembic/               # Migraciones
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .ruff.toml
├── frontend/
│   ├── app/                   # Next.js App Router (páginas)
│   ├── components/            # Componentes UI + dominio
│   ├── hooks/                 # Custom React hooks
│   ├── lib/                   # API client, auth, utils
│   ├── store/                 # Zustand stores
│   ├── styles/                # CSS global
│   ├── public/                # Assets + PWA manifest
│   ├── Dockerfile
│   └── package.json
├── database/
│   └── init.sql               # Schema PostGIS + RLS + índices
├── docs/
│   ├── P.Propuesta_VeraService_Colombia.md
│   ├── P.WORKFLOW_EQUIPO.md
│   └── DiagramaArquitectura/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Requisitos previos

| Herramienta    | Versión mínima |
|----------------|---------------|
| Python         | 3.11+         |
| Node.js        | 20 LTS        |
| PostgreSQL     | 15 + PostGIS  |
| Docker         | 24+           |
| Docker Compose | 2.20+         |
| Git            | 2.40+         |

---

## Instalación y desarrollo local

### Opción 1 — Docker Compose (recomendada)

```bash
# Clonar el repositorio
git clone https://github.com/<tu-org>/veramarket.git
cd veramarket_proyecto

# Copiar variables de entorno
cp .env.example .env

# Levantar todos los servicios
docker compose up -d

# Verificar estado
docker compose ps
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000
- API docs: http://localhost:8000/docs

### Opción 2 — Manual

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables
cp .env.example .env
# Editar .env con tu DATABASE_URL local

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Copiar variables
cp .env.example .env.local

# Iniciar dev server
npm run dev
```

---

## Variables de entorno

Ver archivos `.env.example` en la raíz, `backend/` y `frontend/` para la lista completa de variables.

Variables críticas:

| Variable          | Descripción                              |
|-------------------|------------------------------------------|
| `DATABASE_URL`    | Conexión PostgreSQL (asyncpg)            |
| `JWT_SECRET`      | Clave secreta para tokens JWT            |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos                 |
| `NEXT_PUBLIC_API_URL` | URL de la API para el frontend       |
| `GEMINI_API_KEY`  | API key para interpretación NLU           |
| `TYPESENSE_API_KEY` | API key del motor de búsqueda Typesense |
| `TYPESENSE_HOST`  | Host de Typesense (docker: `typesense`)   |
| `TYPESENSE_PORT`  | Puerto de Typesense (por defecto `8108`)  |

---

## Flujo de trabajo Git

- **`main`** — Producción. Solo recibe merges de `develop` vía PR.
- **`develop`** — Staging / integración. Rama base para features.
- **`feat/<nombre>`** — Ramas de feature desde `develop`.

### Convención de commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(scope): descripción

tipos: feat | fix | docs | refactor | test | chore | ci | style
```

Ejemplos:
```
feat(auth): add JWT login endpoint
fix(products): correct price validation for COP
docs: update README with setup instructions
```

---

## CI/CD

El pipeline de GitHub Actions [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) implementa una estrategia de integración y despliegue continuo robusta:

1.  **Triggers Inteligentes**:
    -   `push feature/*`: Ejecuta solo tests unitarios y linting del backend (feedback rápido).
    -   `pull_request` (hacia `develop` o `main`): Ejecuta el CI completo (Backend + Frontend Build/Lint).
    -   `push main`: Dispara el flujo completo de CI y el despliegue automático (CD) a producción.
2.  **Calidad del Backend**:
    -   **Linting**: Uso de `Ruff` para garantizar estándares de código Python.
    -   **Testing**: Ejecución de `pytest` con servicios de PostgreSQL y PostGIS.
    -   **Quality Gate**: Cobertura mínima obligatoria del **70%** (configurada vía `pytest-cov`).
3.  **Calidad del Frontend**:
    -   **Linting**: ESLint para mantener la consistencia en Next.js.
    -   **Validation**: Verificación de tipos y build de producción exitoso.
4.  **Despliegue Continuo (CD)**:
    -   **Backend**: Despliegue automático a **Render.com** mediante webhooks.
    -   **Frontend**: Despliegue a **Vercel** mediante CLI/Webhook.

---

## Despliegue

| Servicio     | Plataforma     | Tier    | Notas                              |
|-------------|----------------|---------|-------------------------------------|
| Frontend    | Vercel         | Free    | Auto-deploy desde GitHub            |
| Backend     | Render.com     | Free    | Deploy hooks configurados           |
| Base de datos | Supabase / Neon | Free  | PostgreSQL 15 + PostGIS             |
| DNS / SSL   | Cloudflare     | Free    | Proxy DNS, SSL Full (Strict)        |

### Configuración Cloudflare

1. Registrar dominio en Cloudflare
2. Apuntar DNS a Vercel (frontend) y Render (backend API)
3. Activar SSL **Full (Strict)**
4. Activar caché para assets estáticos

---

## Roadmap

| Sprint | Entregable                                           | Estado    |
|--------|------------------------------------------------------|-----------|
| 0      | Setup monorepo, modelos, esqueletos, CI/CD           | ✅ Finalizado |
| 1      | Auth (OTP, Sinapsis), CRUD productos, perfil usuario | ✅ Finalizado |
| 2      | Core PWA, notificaciones push, UX Offline loaders    | ✅ Finalizado |
| 3      | Catálogo inteligente híbrido + mapa interactivo       | 🟡 En curso |
| 4      | Recomendaciones IA (VeraMatch) + mejoras de ranking   | 🔲        |
| 5      | QA, tests E2E, deploy producción, reputación         | 🔲        |

---

## Licencia

Proyecto académico — **Universidad Autónoma de Occidente**, 8vo Semestre, 2025.

---

## 👥 Equipo

VeraService Colombia — Proyecto Informático 2025-1
