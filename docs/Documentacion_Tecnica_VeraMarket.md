# Documentación Técnica — VeraMarket (Sprint 5)

## 1. Visión General
VeraMarket es una plataforma PWA de comercio P2P hiper-local diseñada para campus universitarios. Utiliza una arquitectura híbrida para búsqueda y una gestión de estado robusta para las negociaciones entre compradores y vendedores.

## 2. Stack Tecnológico
*   **Backend:** FastAPI (Python 3.11), SQLAlchemy 2.0 (Async), Pydantic v2.
*   **Base de Datos:** PostgreSQL 15 + PostGIS (Geolocalización), alojada en Supabase/Neon.
*   **Motores de Búsqueda:** 
    *   **Typesense:** Búsqueda full-text y facetada ultra-rápida.
    *   **Gemini 1.5 Flash:** Procesamiento de lenguaje natural (NLU) para consultas semánticas.
*   **Frontend:** React (Next.js 14 App Router), TypeScript, Tailwind CSS, Zustand, Framer Motion.
*   **Seguridad:** JWT (Stateless), OTP (Correo institucional).

## 3. Arquitectura del Sistema (Vista General)
El sistema está compuesto por tres capas principales que interactúan mediante el **Patrón API Gateway (Reverse Proxy)** para garantizar seguridad y control de tráfico:

1.  **Capa Cliente (PWA Shell):** Implementa Service Workers para estrategias Network-only (catálogo) y Background Sync, brindando una experiencia "app-like" en navegadores móviles. Se apoya en estado global gestionado con Zustand.
2.  **Capa de Servicios (Backend):** Múltiples módulos funcionales (Auth, Catalog, Search & AI, Chat) desarrollados en FastAPI que exponen una API RESTful versionada (`/api/v1`).
3.  **Capa de Datos:** Clúster de PostgreSQL central para transacciones relacionales, apoyado por almacenamiento de objetos para imágenes (CDN) e índices en memoria (Typesense) para búsqueda en tiempo real.

## 4. Módulos Desarrollados a Profundidad

El backend está construido bajo una arquitectura modular tipo *MVC-like* con *Dependency Injection* nativa de FastAPI y un *Service Layer* que aísla la lógica de negocio de los enrutadores.

### 4.1 Módulo de Autenticación y Usuarios (`auth.py`, `users.py`)
*   **Flujo Passwordless:** Implementa autenticación mediante OTP (One-Time Password) enviados asíncronamente (vía `aiosmtplib`) al correo institucional.
*   **Polimorfismo de Roles:** Manejo de estados de vendedor (`pending`, `approved`, `rejected`) mediante enums en PostgreSQL, con validación de "lista blanca" proveniente de Sinapsis UAO.
*   **Cumplimiento Legal:** Integración estricta con la Ley 1581/2012 mediante *Row-Level Security (RLS)* en la base de datos y *flags* configurables (`show_email`, `show_phone`) que enmascaran el payload saliente del usuario.

### 4.2 Módulo de Catálogo y Sistema de Cupones (`products.py`, `coupons.py`)
*   **Catálogo P2P:** Los productos incluyen soporte espacial guardando latitud/longitud como `GEOMETRY(Point)` a través de `geoalchemy2` para consultas `ST_DWithin` georreferenciadas.
*   **Soft-Delete:** Patrón de borrado lógico (`is_deleted=True`) para preservar el historial auditable y asegurar la integridad referencial en transacciones pasadas.
*   **Relación M2M de Promociones:** El sistema de cupones (HU 8.9) maneja validaciones complejas en la capa `coupon_service`. Un cupón puede ser "Global" o estar restringido a productos específicos (tabla de enlace `coupon_products`), afectando dinámicamente el precio a nivel de la API sin mutar el precio base del producto.

### 4.3 Módulo de Negociaciones y Transacciones (`negotiations.py`)
*   **Máquina de Estados Finita:** Implementa transiciones estrictas (`PENDING` → `ACCEPTED` → `DELIVERED` o `REJECTED`/`CANCELLED`).
*   **Optimistic Locking & Bloqueo Transaccional:** El sistema restringe el paso al estado `COMPLETED` hasta que ambas partes (comprador y vendedor) hayan acordado de forma bidireccional (*Double Opt-in*) un método de pago ("Efectivo" o "Transferencia").
*   **Integridad del GMV:** Al marcar la entrega, un trigger consolida el precio final de cierre y las cantidades (HU 8.3) para aislar la métrica financiera del catálogo vivo.

### 4.4 Dashboard Analítico (`analytics.py`)
*   **Motor de Agregación:** Utiliza *Window Functions* y agregaciones asíncronas de SQLAlchemy para generar resúmenes temporales de ingresos y volumen de transacciones en la vista del vendedor, agrupando por día o mes según los parámetros de la consulta (HU 8.7).

## 5. Arquitectura Híbrida de Búsqueda (Gemini + Typesense)

El sistema de búsqueda es el núcleo tecnológico (RNF-01: Latencia <100ms) y resuelve el descubrimiento en el ecosistema universitario.

1.  **Capa NLU (Gemini 1.5 Flash):** El servicio `nlu_service.py` actúa mediante el patrón *Adapter*. Procesa el modismo universitario (ej. *"algo pa picar barato"*), y mediante ingeniería de *prompts* estructurada, fuerza una salida estricta en JSON validada con Pydantic.
2.  **Pre-Filtering:** Se extraen *tags*, categoría (`comida`) e intención, inyectándolos en la consulta de Typesense. Esto mitiga alucinaciones y evita mezclar resultados (ej. repuestos vs comida).
3.  **Typesense Search Engine:** Ejecuta la búsqueda de texto completo y facetada (`category`, `condition`) sobre un índice en memoria. Soporta filtros secundarios (precio, radio geográfico) con latencias <20ms.
4.  **Fallback Resiliente (*Circuit Breaker*):** Si la cuota de la API de Google (10/día/usuario) se agota, el proveedor colapsa, o devuelve un JSON malformado, el sistema interrumpe el intento e invoca instantáneamente un enrutamiento por coincidencia léxica hacia Typesense y la base de datos `tsvector` de PostgreSQL, manteniendo el Uptime sin sacrificar UX.

## 6. Proceso DevOps y Escalabilidad (CI/CD)

VeraMarket sigue un enfoque *Cloud-Native* basado en repositorios únicos o monorepos con despliegue automatizado.

### 6.1 Infraestructura como Servicio (IaaS) / Free Tiers
*   **Frontend (Next.js):** Desplegado en **Vercel** o **Netlify**. Brinda un CDN global automático en el borde (Edge), lo que optimiza la entrega estática de los *Service Workers* y la Shell de la PWA.
*   **Backend (FastAPI):** Alojamientos como **Render.com**. Se ejecuta mediante `uvicorn` asíncrono con despliegues activados por *webhooks* desde GitHub.
*   **Base de Datos (Supabase/Neon):** Clúster Serverless de PostgreSQL que separa la capa de computación del almacenamiento, escalando a cero en inactividad y proveyendo un pooler de conexiones (PgBouncer nativo) indispensable para la naturaleza multi-hilo de FastAPI.

### 6.2 Integración y Despliegue Continuo (GitHub Actions)
La automatización se rige por un pipeline de `.github/workflows/deploy.yml`:
1.  **Validación Continua (CI):** Ante cada PR hacia `develop`, se ejecutan trabajos de *Linting* (Ruff/Flake8 para Python, ESLint para TypeScript) y pruebas automatizadas (pytest) que validan servicios como JWT y OTP.
2.  **Despliegue Continuo (CD):** Tras un *merge* en la rama `main`, la acción dispara la compilación (Build) y sincroniza con los servicios en la nube a través de claves de API (Secrets), actualizando producción (Zero-Downtime Deploy) en escasos minutos.

### 6.3 Manejo de Entornos y Seguridad de Secretos
El proyecto aísla la inyección de dependencias ambientales:
*   Los entornos locales se sirven vía `.env`.
*   El código fuente nunca almacena información sensible; todo se maneja desde el panel de Variables de Entorno de Render/Vercel (ej. `DATABASE_URL`, `JWT_SECRET`, `GEMINI_API_KEY`).
*   Se utiliza CORS configurado exclusivamente para aceptar tráfico cruzado desde el dominio de Vercel y `localhost` durante el desarrollo.

---
*Documentación revisada y extendida para auditoría técnica — Mayo 2026.*
