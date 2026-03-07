***

# Manual de Workflow y Estándares de Desarrollo - Equipo VeraMarket

**Proyecto:** VeraMarket - Marketplace P2P Universitario  
**Fase:** Migración a Cloud-Native y Escalabilidad

***

## 1. Introducción

Este documento define los protocolos de trabajo, herramientas y estándares de calidad para el equipo de desarrollo de **VeraMarket**, la plataforma PWA (Progressive Web App) de comercio P2P hiper-local diseñada para campus universitarios en Colombia. El objetivo es orquestar al equipo de 4 integrantes para mantener una alta velocidad de ejecución ("Velocity") en el desarrollo web, preparando el terreno para la migración a infraestructura Cloud-Native, integración de IA y escalabilidad a 5,000 usuarios activos mensuales (MAU).

### 1.1. Contexto del Proyecto

VeraMarket es el canal de comercialización oficial para emprendimientos universitarios validados por instituciones como Sinapsis UAO que actualmente opera en grupos caóticos de WhatsApp, ofreciendo:
- **Geolocalización:** Mapas interactivos con OpenStreetMap para ubicar vendedores dentro del campus
- **Búsqueda Semántica:** IA (OpenAI GPT-4o-mini) para conectar oferta y demanda inteligentemente
- **Confianza:** Verificación cruzada de vendedores con la base de datos de emprendedores de Sinapsis y sistema de reputación
- **Modelo P2P:** Sin intermediación logística ni comisiones abusivas

***

## 2. Estructura del Equipo y Herramientas

### 2.1. Roles del Equipo (4 Integrantes)

Cada miembro tiene un rol primario, pero en un equipo pequeño la colaboración es transversal (T-shaped skills).

1. **Project Manager / Tech Lead (PM/TL) - Nelson Andrés Duque**
   - **Responsabilidad:** Guardián de la arquitectura Cloud-Native, administrador del tablero Jira, aprobador final de Pull Requests críticos, desbloqueador del equipo y gestor de infraestructura (Vercel, Render, Supabase/Neon)
   - **Enfoque:** 50% Gestión (Scrum Master), 50% Código (Arquitectura/DevOps)
   - **Stack:** Python, FastAPI, Vercel, Render.com, Docker, CI/CD

2. **Backend Developer Lead (BE) - Eduard Criollo Yule**
   - **Responsabilidad:** Arquitectura de FastAPI, diseño de Base de Datos (PostgreSQL + PostGIS), lógica Core, seguridad, integración de APIs externas (OpenAI, OpenStreetMap, OAuth 2.0)
   - **Enfoque:** Servicios backend, endpoints RESTful, tareas asíncronas
   - **Stack:** Python, FastAPI, SQLAlchemy, Pydantic, PostgreSQL

3. **Frontend Developer Lead (FE) - Julián Montoya**
   - **Responsabilidad:** Arquitectura en React.js/Next.js, implementación de UI responsiva Mobile-First, consumo de APIs, gestión de estado, integración de mapas (OpenStreetMap/Leaflet)
   - **Enfoque:** Experiencia de usuario, PWA, optimización de rendimiento
   - **Stack:** React/Next.js, TypeScript, Tailwind CSS, Zustand/Context API

4. **UI/UX Designer & QA Tester (Design/QA) - Edwin David Correa**
   - **Responsabilidad:** Prototipos en Figma, redacción de User Stories (lado usuario), pruebas manuales exhaustivas (búsqueda de bugs), validación de criterios de aceptación
   - **Enfoque:** Diseño centrado en el usuario universitario, testing funcional
   - **Stack:** Figma, herramientas de testing manual, documentación

### 2.2. Stack Tecnológico

#### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Base de Datos:** PostgreSQL 15 + PostGIS (Supabase / Neon.tech Free Tier → AWS RDS en fase de inversión)
- **ORM:** SQLAlchemy 2.0 (async) con Type Hints + Alembic para migraciones
- **Validación:** Pydantic v2
- **IA:** OpenAI API (GPT-4o-mini) para búsqueda semántica (Sprint 3, Adapter Pattern)
- **Auth:** JWT (python-jose) + bcrypt, validación de correos .edu.co
- **Infraestructura:** Render.com (Free Tier) → AWS EC2 en fase de inversión

#### Frontend
- **Framework:** Next.js 14 con App Router
- **Lenguaje:** TypeScript
- **Estilo:** Tailwind CSS
- **Mapas:** Leaflet.js + OpenStreetMap
- **Estado:** Zustand
- **PWA:** @ducanh2912/next-pwa
- **Service Workers:** Almacenamiento en caché de activos estáticos (JS, CSS) para mejorar el First Contentful Paint (FCP < 3s)

#### Infraestructura y DevOps
- **Cloud Provider (Fase 1 — Free Tier):** Vercel (frontend), Render.com (backend), Supabase/Neon.tech (DB)
- **Cloud Provider (Fase inversión):** AWS (EC2, RDS, S3, CloudFront)
- **CDN / DNS / SSL:** Cloudflare (Free Tier)
- **Contenedores:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Monitoreo:** Sentry (errores frontend/backend)

### 2.3. Stack de Herramientas

- **Gestión de Proyecto:** **Jira Software** (Metodología Scrum)
- **Control de Versiones:** **GitHub** (Repositorio Privado: `veramarket/platform`)
- **Comunicación:** Discord con canales especializados:
  - `#general`: Anuncios y stand-ups
  - `#dev-backend`: Discusiones de API, DB y arquitectura
  - `#dev-frontend`: Discusiones de UI, UX e integración
  - `#bugs-and-qa`: Reportes de QA y hotfixes
  - `#devops`: Infraestructura, deploys y monitoreo
- **Documentación:** 
  - Markdown en repositorio (`/docs`)
  - Wiki de Confluence vinculada a Jira
  - Swagger/OpenAPI para documentación de API
- **Diseño:** Figma (prototipados colaborativos)
- **API Testing:** Postman con colecciones compartidas

***

## 3. Metodología Ágil (Scrum con Jira)

Trabajaremos en **Sprints de 2 Semanas** (10 días hábiles), con alta cadencia de entrega para validar hipótesis rápidamente en el mercado universitario.

### 3.1. Ceremonias Estándar

1. **Sprint Planning (Lunes Semana 1 - 9:00 AM - 2 horas máx)**
   - El equipo selecciona historias del *Backlog Refinado* priorizadas por el PM
   - Se asignan puntajes de esfuerzo con **Planning Poker** (Story Points: 1, 2, 3, 5, 8, 13)
   - **Meta:** Definir el "Sprint Goal" claro, alcanzable y alineado al roadmap de inversión
   - **Capacidad del Equipo:** 40-50 Story Points por sprint (ajustar según velocity histórico)

2. **Daily Standup (Diario - 9:00 AM - 15 min máx)**
   - Formato obligatorio:
     - ¿Qué hice ayer?
     - ¿Qué haré hoy?
     - ¿Tengo bloqueos? (impediments)
   - **Regla:** Prohibido resolver problemas técnicos profundos aquí. Se agendan "VeraTalks" (sesiones técnicas) aparte en Discord
   - **Moderador:** PM/TL rota semanalmente para evitar centralización

3. **Sprint Review (Viernes Semana 2 - 2:00 PM - 1.5 horas)**
   - **Demo en vivo** del producto funcionando en entorno **Staging** (staging.veramarket.app)
   - Audiencia: Tech Lead, Stakeholders simulados (compañeros de clase, profesores)
   - Feedback documentado en Jira como nuevos tickets

4. **Sprint Retrospective (Viernes Semana 2 - 3:30 PM - 1 hora)**
   - **Matriz retrospectiva:**
     - **Start** (Empezar a hacer)
     - **Stop** (Dejar de hacer)
     - **Continue** (Seguir haciendo)
   - Resultado: Action Items asignados como tareas de mejora continua

### 3.2. Configuración del Tablero Jira

El tablero Scrum tendrá las siguientes **columnas** para visualizar el flujo de valor:

1. **Backlog:** Historias futuras, no priorizadas para este sprint
2. **Ready for Sprint:** Refinadas y listas para selección en Planning
3. **To Do:** Seleccionadas para el sprint actual
4. **In Progress:** Se está trabajando activamente
   - **Regla WIP (Work In Progress):** Máximo 1 tarea "In Progress" por desarrollador para evitar multitasking
5. **Code Review:** Pull Request (PR) abierto en GitHub, esperando aprobación
6. **QA / Testing:** Desplegado en Staging; Edwin está ejecutando pruebas funcionales
7. **Done:** Código mergeado a `main`, probado, aprobado y desplegado a Producción

### 3.3. Estándar de Tickets (User Stories)

Cada ticket en Jira debe seguir este formato para evitar ambigüedades:

**Ejemplo de User Story:**

```
Título: [BE] Endpoint de creación de productos con validación de imágenes

Descripción:
Como **vendedor universitario** quiero **publicar productos con hasta 5 fotos** 
para **mostrar mi oferta de forma atractiva y aumentar mis ventas**.

Criterios de Aceptación (AC):
- [ ] El endpoint POST /api/v1/products permite subir hasta 5 imágenes (formato JPG/PNG)
- [ ] Las imágenes se comprimen automáticamente antes de guardar en S3 (max 500KB c/u)
- [ ] Si falla la carga, devuelve error 400 con mensaje "Intente nuevamente"
- [ ] La validación rechaza formatos no permitidos (GIF, WEBP) con error descriptivo
- [ ] Se guarda metadatos de imágenes (URL S3, tamaño, timestamp) en BD

Story Points: 5
Etiquetas: Backend, API, Storage, P1-Critical
Asignado: Eduard Criollo
Sprint: Sprint 3 - Fase MVP
```

**Tipos de Etiquetas:**
- **Área:** `Backend`, `Frontend`, `DevOps`, `Design`
- **Tipo:** `Feature`, `Bug`, `Hotfix`, `TechDebt`, `Spike`
- **Prioridad:** `P0-Blocker`, `P1-Critical`, `P2-High`, `P3-Medium`, `P4-Low`

***

## 4. Gestión de Código (GitHub Workflow)

### 4.1. Estrategia de Ramas (Gitflow Simplificado)

Para un equipo de 4 personas, Gitflow completo sería burocrático. Usamos una versión adaptada:

- **`main`:** Rama de **Producción**. Intocable. Solo recibe merges desde `develop` tras aprobación del PM/TL. Cada merge a `main` genera un deploy automático a producción vía GitHub Actions
- **`develop`:** Rama de **Integración** y Staging. Todo el código nuevo llega aquí primero. Deploy automático a `staging.veramarket.app`
- **Ramas de Feature:** Creadas desde `develop`
  - Nomenclatura: `feature/VERA-{ID}-{descripcion-corta}`
  - Ejemplos: 
    - `feature/VERA-12-login-oauth-google`
    - `feature/VERA-45-map-veraspot-markers`
    - `feature/VERA-67-ai-semantic-search`
- **Ramas de Fix:** Para corregir bugs detectados
  - Nomenclatura: `fix/VERA-{ID}-{descripcion}` (bugs en develop)
  - `hotfix/{descripcion}` (bugs urgentes en producción, se crean desde `main`)

### 4.2. Flujo de Trabajo Diario

```bash
# 1. Sincronizar con la última versión de develop
git checkout develop
git pull origin develop

# 2. Crear rama de feature vinculada a ticket de Jira
git checkout -b feature/VERA-10-create-product-endpoint

# 3. Desarrollar con commits frecuentes y atómicos
git add .
git commit -m "feat: agrega validación de precios en endpoint de productos"

# 4. Push a repositorio remoto
git push origin feature/VERA-10-create-product-endpoint

# 5. Abrir Pull Request en GitHub con plantilla estándar
```

### 4.3. Conventional Commits (Obligatorio)

Todos los mensajes de commit deben seguir el estándar **Conventional Commits**:

**Formato:**
```
<tipo>(<scope>): <descripción breve>

[cuerpo opcional con más detalles]

[footer opcional: Closes VERA-10]
```

**Tipos permitidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formateo, espacios (sin cambios funcionales)
- `refactor`: Refactorización de código sin cambiar funcionalidad
- `perf`: Mejoras de performance
- `test`: Agregar o corregir tests
- `chore`: Tareas de mantenimiento (deps, config)

**Ejemplos:**
```bash
feat(api): agrega endpoint para crear producto con geolocalización
fix(auth): corrige validación de tokens JWT expirados
docs(readme): actualiza instrucciones de instalación local
style(backend): aplica correcciones de Ruff en servicios
refactor(frontend): optimiza re-renders en ProductCard con React.memo
perf(db): agrega índice GiST en columna location para queries espaciales
test(api): agrega tests unitarios para servicio de productos
chore(deps): actualiza FastAPI a v0.110.0
```

### 4.4. Pull Requests (PR) y Code Reviews

El control de calidad comienza aquí. **Sin Code Review, no hay merge.**

#### Reglas de Pull Requests:

1. **Regla de Oro:** Nadie aprueba ni mergea su propio PR
2. **Vinculación a Jira:** El título o descripción del PR debe incluir el ticket: `Closes VERA-10` o `Fixes VERA-45`
3. **Plantilla de PR:** Usar la plantilla `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Descripción
Breve descripción de los cambios realizados

## Ticket de Jira
Closes VERA-XX

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Refactorización
- [ ] Actualización de documentación

## Checklist
- [ ] El código sigue los estándares del proyecto (Ruff/ESLint)
- [ ] He realizado una auto-revisión de mi código
- [ ] He agregado tests que prueban mi funcionalidad
- [ ] Los tests existentes pasan exitosamente
- [ ] He actualizado la documentación relevante

## Screenshots (si aplica)
```

4. **Revisión (Code Review) - Checklist del Revisor:**
   - ✅ Lógica correcta y segura
   - ✅ Sin credenciales hardcodeadas (¡Alerta de Seguridad!)
   - ✅ Cumplimiento de estándares de estilo (Ruff, ESLint)
   - ✅ Tests cubren casos edge y errores
   - ✅ Documentación actualizada (docstrings, README)
   - ✅ Performance adecuado (queries N+1, re-renders innecesarios)

5. **Aprobación:** Se requiere **mínimo 1 aprobación** (preferible del Tech Lead o Peer Senior) para mergear a `develop`

6. **Comentarios Constructivos:** En los Code Reviews, comentar sobre el código, nunca sobre la persona. Usar tono constructivo:
   - ✅ "Sugiero cambiar esto por... porque mejora la legibilidad"
   - ❌ "Esto está mal hecho"

***

## 5. Estándares Técnicos de Desarrollo

### 5.1. Backend (Python FastAPI)

El backend es el núcleo de la inteligencia del sistema.

#### 5.1.1. Estructura de Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de FastAPI
│   ├── core/
│   │   ├── config.py        # Variables de entorno (Pydantic Settings)
│   │   ├── security.py      # JWT, OAuth, hashing
│   │   └── database.py      # Conexión a PostgreSQL
│   ├── models/              # Modelos SQLAlchemy (BD)
│   │   ├── user.py
│   │   ├── product.py
│   │   └── transaction.py
│   ├── schemas/             # Esquemas Pydantic (validación)
│   │   ├── user.py
│   │   ├── product.py
│   │   └── response.py
│   ├── routers/             # Endpoints REST
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── users.py
│   │   └── search.py
│   ├── services/            # Lógica de negocio
│   │   ├── product_service.py
│   │   ├── ai_service.py    # Integración OpenAI
│   │   └── map_service.py   # OpenStreetMap
│   ├── utils/
│   │   ├── validators.py
│   │   └── helpers.py
│   └── tests/
│       ├── test_products.py
│       └── test_auth.py
├── alembic/                 # Migraciones de BD
├── requirements.txt
├── Dockerfile
└── README.md
```

#### 5.1.2. Estándares de Código Backend

1. **Linter/Formateo:** Uso obligatorio de **Ruff** (reemplaza Flake8 + Black)
   ```bash
   # .ruff.toml
   line-length = 88
   target-version = "py311"
   select = ["E", "F", "I", "N", "W"]
   ```

2. **Type Hints:** Uso estricto de anotaciones de tipo
   ```python
   from typing import List, Optional
   from pydantic import BaseModel
   
   def get_products(
       campus_id: int, 
       limit: int = 10, 
       offset: int = 0
   ) -> List[ProductSchema]:
       """Obtiene productos filtrados por campus con paginación"""
       ...
   ```

3. **Docstrings:** Formato Google Style para funciones públicas
   ```python
   def create_product(product_data: ProductCreate, user_id: int) -> Product:
       """Crea un nuevo producto en el sistema.
       
       Args:
           product_data: Datos del producto a crear
           user_id: ID del usuario vendedor
           
       Returns:
           Producto creado con ID asignado
           
       Raises:
           ValueError: Si el precio es negativo
           PermissionError: Si el usuario no está verificado
       """
   ```

4. **Gestión de Errores:**
   ```python
   from fastapi import HTTPException, status
   
   # Usar HTTPException con códigos semánticos
   raise HTTPException(
       status_code=status.HTTP_400_BAD_REQUEST,
       detail="El precio debe ser mayor a 0"
   )
   ```

5. **Variables de Entorno:** Usar Pydantic Settings (nunca hardcodear)
   ```python
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       DATABASE_URL: str
       OPENAI_API_KEY: str
       JWT_SECRET: str
       
       class Config:
           env_file = ".env"
   ```

6. **Tests:** `pytest` con cobertura mínima del **70%** en servicios críticos
   ```python
   # tests/test_products.py
   def test_create_product_success(client, auth_headers):
       response = client.post(
           "/api/v1/products",
           json={"name": "Almuerzo", "price": 8000},
           headers=auth_headers
       )
       assert response.status_code == 201
       assert response.json()["name"] == "Almuerzo"
   ```

#### 5.1.3. Base de Datos (PostgreSQL + PostGIS)

- **Migraciones:** Usar **Alembic** para versionado de esquema
- **Índices:** Agregar índices en columnas de búsqueda frecuente
  ```sql
  CREATE INDEX idx_products_campus ON products(campus_id);
  CREATE INDEX idx_products_location USING GIST(location);
  ```
- **Queries Geoespaciales:** Usar PostGIS para búsquedas por proximidad
  ```python
  # Buscar productos a menos de 500 metros
  query = select(Product).where(
      func.ST_DWithin(
          Product.location,
          func.ST_MakePoint(lon, lat),
          500  # metros
      )
  )
  ```

### 5.2. Frontend (Next.js 14)

El frontend debe ser rápido, Mobile-First y optimizado como PWA.

#### 5.2.1. Estructura de Proyecto

```
frontend/
├── app/                     # Next.js 14 App Router
│   ├── layout.tsx
│   ├── page.tsx             # Home
│   ├── products/
│   │   ├── page.tsx         # Catálogo
│   │   └── [id]/page.tsx    # Detalle producto
│   ├── map/
│   │   └── page.tsx         # Mapa interactivo
│   └── api/                 # API Routes (opcional)
├── components/
│   ├── ui/                  # Componentes reutilizables
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Input.tsx
│   ├── ProductCard.tsx
│   ├── MapView.tsx
│   └── SearchBar.tsx
├── lib/
│   ├── api.ts               # Cliente HTTP (fetch/axios)
│   ├── auth.ts              # Gestión de tokens
│   └── utils.ts
├── hooks/
│   ├── useProducts.ts
│   └── useAuth.ts
├── store/                   # Zustand stores
│   └── authStore.ts
├── styles/
│   └── globals.css
├── public/
│   ├── icons/
│   └── manifest.json        # PWA manifest
├── package.json
└── next.config.js
```

#### 5.2.2. Estándares de Código Frontend

1. **Linter/Formateo:** ESLint + Prettier
   ```json
   // .eslintrc.json
   {
     "extends": ["next/core-web-vitals", "prettier"],
     "rules": {
       "no-console": "warn",
       "prefer-const": "error"
     }
   }
   ```

2. **TypeScript:** Obligatorio en todos los archivos
   ```typescript
   interface Product {
     id: string;
     name: string;
     price: number;
     seller: User;
     location: Coordinates;
   }
   
   const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
     return <div>{product.name}</div>;
   };
   ```

3. **Naming Conventions:**
   - **Componentes:** `PascalCase` (ej. `ProductCard.tsx`)
   - **Funciones/Variables:** `camelCase` (ej. `handleSubmit`)
   - **Constantes:** `UPPER_SNAKE_CASE` (ej. `API_BASE_URL`)
   - **Archivos de utilidades:** `kebab-case` (ej. `format-date.ts`)

4. **Componentes Funcionales + Hooks:**
   ```typescript
   'use client'; // Obligatorio para componentes con interactividad
   
   import { useState, useEffect } from 'react';
   
   export default function SearchBar() {
     const [query, setQuery] = useState('');
     
     useEffect(() => {
       // Side effects
     }, [query]);
     
     return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
   }
   ```

5. **CSS:** Tailwind CSS para estilos utility-first
   ```tsx
   <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg">
     Publicar Producto
   </button>
   ```

6. **Estado Global:** Zustand para estados complejos
   ```typescript
   // store/authStore.ts
   import create from 'zustand';
   
   interface AuthState {
     user: User | null;
     token: string | null;
     login: (token: string) => void;
     logout: () => void;
   }
   
   export const useAuthStore = create<AuthState>((set) => ({
     user: null,
     token: null,
     login: (token) => set({ token }),
     logout: () => set({ user: null, token: null }),
   }));
   ```

7. **Performance:**
   - Usar `React.memo()` para componentes pesados
   - Implementar lazy loading con `next/dynamic`
   - Optimizar imágenes con `next/image`

#### 5.2.3. PWA (Progressive Web App - Conectividad Persistente)

- **Service Worker:** Configurado en `next.config.js` con `next-pwa`
- **Manifest:** `/public/manifest.json` con iconos y metadata

***

## 6. Definición de "Done" (DoD)

Una tarea o historia de usuario **NO está terminada** hasta que cumpla **todos** los siguientes puntos:

- [ ] **Código completo** pusheado a GitHub en rama de feature
- [ ] **Pull Request** creado con plantilla completa
- [ ] **Code Review** aprobado por al menos 1 peer (preferible PM/TL)
- [ ] **Tests unitarios** escritos y pasando exitosamente (Backend: pytest, Frontend: Jest)
- [ ] **Merge** a `develop` completado sin conflictos
- [ ] **Deploy automático** a Staging ejecutado correctamente
- [ ] **Criterios de Aceptación** del ticket de Jira verificados por QA Tester
- [ ] **QA Tester** (Edwin) ha dado el "✅ Aprobado" en Jira tras pruebas funcionales
- [ ] **Documentación** actualizada (README, Swagger, comentarios en código)

**Solo cuando todos los checkboxes estén marcados, el ticket se mueve a "Done".**

***

## 7. Integración Continua y Despliegue (CI/CD)

### 7.1. Pipeline de GitHub Actions

**Workflow automatizado en `.github/workflows/ci-cd.yml`:**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run Ruff
        run: ruff check .
      - name: Run tests
        run: pytest --cov=app

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run ESLint
        run: npm run lint
      - name: Run tests
        run: npm test

  deploy-staging:
    needs: [backend-tests, frontend-tests]
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render (Staging) + Vercel (Preview)
        run: |
          # Deploy hooks de Render + auto-deploy Vercel desde develop

  deploy-production:
    needs: [backend-tests, frontend-tests]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render (Production) + Vercel (Production)
        run: |
          # Deploy hooks de Render + auto-deploy Vercel desde main
```

### 7.2. Ambientes

1. **Local:** Desarrollo en máquinas locales con Docker Compose
2. **Staging:** `staging.veramarket.app` (deploy automático desde `develop`)
3. **Production:** `veramarket.app` (deploy automático desde `main` tras aprobación)

***

## 8. Seguridad y Mejores Prácticas

### 8.1. Gestión de Secretos

- **Nunca** commitear archivos `.env` o credenciales
- Usar **GitHub Secrets** para CI/CD
- Variables de entorno en producción gestionadas en paneles de Vercel/Render (Fase 1) y AWS Systems Manager Parameter Store (fase inversión)

### 8.2. Autenticación y Autorización

- **OAuth 2.0** con correos institucionales (`.edu.co`)
- **JWT tokens** con expiración de 24 horas
- **Refresh tokens** para renovación automática
- **HTTPS** obligatorio en producción (certificado SSL de Cloudflare)

### 8.3. Protección de Datos

- **Cumplimiento Ley 1581/2012** (Habeas Data Colombia)
- Encriptación de contraseñas con bcrypt
- Sanitización de inputs para prevenir SQL Injection y XSS

### 8.4. Monitoreo y Logging

- **Sentry** para tracking de errores en tiempo real (frontend y backend)
- **Render Logs / Vercel Logs** para logs de infraestructura (Fase 1)
- **AWS CloudWatch** para logs de infraestructura (fase inversión)
- **Alertas** en Discord para errores críticos (P0/P1)

***

## 9. Gestión de Conflictos y Comunicación

### 9.1. Resolución de Bloqueos

- **Regla de 60 minutos:** Si un desarrollador está atascado más de **60 minutos**, debe reportarlo inmediatamente en Discord (`#general`) o pedir ayuda al Tech Lead
- **"Levantar la mano rápido es profesional"** - No hay penalización por pedir ayuda

### 9.2. Toma de Decisiones Técnicas

- Decisiones importantes (cambio de librería, arquitectura, stack) deben:
  1. Discutirse en "VeraTalk" (reunión técnica asíncrona o síncrona)
  2. Documentarse en `DECISIONES_TECNICAS.md` del repositorio con formato:
     ```markdown
     ## [Fecha] Decisión: Migración de Llama 3 local a OpenAI API
     
     **Contexto:** MVP con GPU propia cuesta $884/mes vs $50/mes en cloud
     
     **Opciones Evaluadas:**
     1. Llama 3 en AWS EC2 GPU (g4dn.xlarge)
     2. OpenAI GPT-4o-mini API
     3. Groq API
     
     **Decisión:** OpenAI API por:
     - Reducción de OpEx en 97%
     - Escalabilidad infinita
     - Menor carga de DevOps
     
     **Consecuencias:** Dependencia de proveedor externo (mitigado con caché)
     
     **Responsables:** Nelson (PM/TL), Eduard (BE)
     ```

### 9.3. Feedback en Code Reviews

- **Tono constructivo:** "Sugiero X porque Y" en vez de "Esto está mal"
- **Evitar bike-shedding:** Enfocarse en lógica y arquitectura, no en preferencias de sintaxis menores
- **Reconocer buen trabajo:** Comentar "Nice!" o "Great approach!" cuando aplique

***

## 10. Roadmap de Desarrollo (Fases del Proyecto)

### Fase 1: Validación Técnica (Meses 1-3)
**Sprint 1-6**

- ✅ Migración de MVP local a Cloud (AWS EC2 + RDS)
- ✅ Implementación de autenticación OAuth 2.0
- ✅ CRUD de productos con geolocalización (PostGIS)
- ✅ Mapa interactivo con OpenStreetMap + Leaflet
- ✅ Sistema básico de búsqueda (filtros por categoría, precio)
- ✅ Lanzamiento piloto en Universidad Autónoma de Occidente (Cali)
- **Meta:** 500 usuarios registrados, 200 publicaciones activas

### Fase 2: Tracción Pre-Seed (Meses 4-8)
**Sprint 7-16**

- 🚧 Búsqueda semántica con OpenAI GPT-4o-mini
- 🚧 Sistema de reputación y calificaciones (5 estrellas)
- 🚧 Chat P2P en tiempo real (WebSockets con Socket.io)
- 🚧 Integración de deep links a Nequi/Daviplata
- 🚧 VeraSpots (marcadores de puntos seguros de intercambio)
- 🚧 Panel de analíticas para vendedores (VeraPlus Premium)
- **Meta:** 5,000 MAU, 50 suscriptores Premium, $500K COP GMV/mes

### Fase 3: Ronda de Inversión (Mes 9+)
**Sprint 17+**

- 📋 Expansión a Bogotá (U. Nacional, Javeriana, Andes)
- 📋 Expansión a Medellín (U. de Antioquia, EAFIT)
- 📋 API pública para integración con comercios externos
- 📋 Modelo de publicidad hiper-local (negocios aledaños al campus)
- 📋 VeraMatch (recomendaciones predictivas con ML)
- **Meta:** 50,000 MAU, Series A funding

***

## 11. Métricas de Éxito del Equipo

### 11.1. KPIs Técnicos (Medidos en cada Sprint Review)

- **Velocity:** Story Points completados por sprint (objetivo: 40-50)
- **Code Coverage:** Cobertura de tests (objetivo: >70%)
- **Bug Leakage:** Bugs encontrados en producción vs QA (objetivo: <10%)
- **PR Cycle Time:** Tiempo desde creación de PR hasta merge (objetivo: <48 horas)
- **Deployment Frequency:** Deploys a producción por semana (objetivo: 2-3)
- **Uptime:** Disponibilidad del sistema (objetivo: 99.9%)
- **Respuesta del servidor:** < 2 segundos para el 95% de las solicitudes.
- **Cobertura de pruebas:** Mantener o subir al 70% (coincide con el rival).
- **Uptime:** Garantizar un 95% de disponibilidad durante las últimas 2 semanas.

### 11.2. KPIs de Producto (Medidos mensualmente)

- **MAU (Monthly Active Users):** Usuarios que abren la app al menos 1 vez/mes
- **DAU/MAU Ratio:** Engagement diario (objetivo: >30%)
- **Retention D7/D30:** Usuarios que vuelven en 7/30 días (objetivo: 50%/30%)
- **Time to First Publish:** Tiempo desde registro hasta primera publicación (objetivo: <5 min)
- **GMV (Gross Merchandise Value):** Volumen de transacciones facilitadas

***

## 12. Recursos y Referencias

### 12.1. Documentación Técnica

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Next.js Docs:** https://nextjs.org/docs
- **PostgreSQL + PostGIS:** https://postgis.net/documentation/
- **OpenAI API:** https://platform.openai.com/docs/api-reference
- **Tailwind CSS:** https://tailwindcss.com/docs

### 12.2. Herramientas de Desarrollo

- **GitHub Repo:** `https://github.com/veramarket/platform` (privado)
- **Jira Board:** `https://veramarket.atlassian.net`
- **Figma Designs:** `https://figma.com/veramarket`
- **Staging:** `https://staging.veramarket.app`
- **Production:** `https://veramarket.app`

### 12.3. Contactos del Equipo

| Rol | Nombre | Email | Discord |
|-----|--------|-------|---------|
| PM/TL |  |  |  |
| BE Lead |  |  |  |
| FE Lead |  |  |  |
| Design/QA |  |  |  |

***

## 13. Apéndices

### Apéndice A: Checklist de Onboarding para Nuevos Miembros

- [ ] Acceso a GitHub (repo `veramarket/platform`)
- [ ] Acceso a Jira (usuario y permisos)
- [ ] Acceso a Discord (canales del equipo)
- [ ] Acceso a Figma (proyectos de diseño)
- [ ] Configuración de entorno local (Docker + .env)
- [ ] Lectura completa de este manual
- [ ] Pair programming con un miembro senior (1 día)

### Apéndice B: Comandos Útiles

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker (stack completo)
docker-compose up -d

# Tests
pytest  # Backend
npm test  # Frontend

# Linters
ruff check .  # Backend
npm run lint  # Frontend
```

***

**Documento vigente para todas las fases del proyecto VeraMarket.**

**Última actualización: Junio de 2025.**

> **Nota:** La infraestructura de Fase 1 usa Free Tiers (Vercel, Render, Supabase/Neon, Cloudflare) para validación a $0 COP. La migración a AWS se ejecutará tras ronda de inversión Pre-Seed.
