# Propuesta de Inversión: VeraMarket
**"La Super-App de la Economía Universitaria en LatAm"**

---

**Fase:** Pre-Seed / Validación de MVP.
**Ubicación:** Colombia.
**Equipo:** Ingeniería de Software (Founding Team).
**Documento:** Investment Memo & Technical Validation.
**Fecha:** Febrero de 2026.

---

## 1. Resumen Ejecutivo

**VeraMarket** es una plataforma Web Progresiva (PWA) diseñada para ser la vitrina digital de los emprendedores institucionales. Nuestra operación física está radicada en Cali. Al aliarnos con Sinapsis UAO, resolvemos la falta de canales de venta directos.

Nacida como una iniciativa de ingeniería con arquitectura **Open Source** para validación a costo cero ($0 COP), VeraMarket ha evolucionado hacia un modelo de negocio escalable. Nuestra propuesta de valor conecta la oferta hiper-local (comida, tutorías, productos de segunda mano) con una demanda cautiva de miles de estudiantes, resolviendo los problemas de confianza y logística que plataformas generalistas como Facebook Marketplace o Rappi no logran atender en este nicho.

Buscamos capital semilla para transformar nuestro MVP validado tecnológicamente en una operación comercial sostenible, migrando de infraestructura local a Cloud-Native para soportar 5,000+ usuarios activos mensuales.

## 2. Oportunidad de Mercado

El mercado universitario en Colombia es un reflejo de la economía nacional, caracterizado por una alta informalidad y un fuerte espíritu emprendedor.

* **Espíritu Emprendedor:** El estudio GUESSS Colombia (EAFIT) indica que el 28.8% de los estudiantes tiene intención de fundar empresa, pero carecen de herramientas digitales profesionales para empezar [2].
* **Validación de Demanda:** Un campus promedio (ej. Universidad Nacional, Univalle) tiene una población flotante de +20,000 personas diarias. Capturar solo el 10% en un campus valida un mercado de 2,000 usuarios recurrentes.

## 3. Panorama Competitivo y Ventaja Única

A diferencia de los competidores, VeraMarket ofrece **Confianza de Nicho** (verificación estudiantil) y **Georreferenciación de Campus**.

| Competidor | Tipo | Debilidad Crítica | La Solución VeraMarket |
| :--- | :--- | :--- | :--- |
| **Grupos de WhatsApp** | Directo | Caos, spam, sin historial, efímero. | Catálogo estructurado y búsqueda semántica. |
| **Instagram Stores** | Directo | Difícil descubrimiento hiper-local. | Mapa interactivo del campus (OpenStreetMap). |
| **Rappi / Food Apps** | Indirecto | Comisiones altas (15-30%) y logística compleja. | Modelo P2P sin intermediación logística. |
| **Facebook Marketplace** | Directo | Inseguro, sin filtro de comunidad. | **Entorno seguro:** Solo correos institucionales. |

## 4. Solución Técnica y Estrategia de Escalabilidad

Actualmente contamos con un MVP funcional basado en soberanía tecnológica (Self-Hosted). Para la fase de inversión, ejecutaremos una migración estratégica a servicios Cloud para garantizar estabilidad y reducción de costos operativos (OpEx).

### 4.1. Arquitectura Actual (MVP - Fase de Validación)
* **Frontend:** PWA con Next.js 14 (App Router) + TypeScript + Tailwind CSS para acceso universal sin tiendas de apps.
* **Backend:** FastAPI (Python 3.11+) con SQLAlchemy 2.0 (async) + Pydantic v2.
* **Base de Datos:** PostgreSQL 15 + PostGIS (geolocalización).
* **Mapas:** OpenStreetMap + Leaflet.js (Gratuito).
* **IA:** OpenAI GPT-4o-mini para búsqueda semántica (Adapter Pattern, Sprint 3).
* **Infraestructura:** Free Tiers — Vercel (frontend), Render.com (backend), Supabase/Neon (DB), Cloudflare (DNS/SSL).

### 4.2. Validación de Escalabilidad Financiera (Cloud Migration)
Hemos analizado el costo de escalar a **5,000 Usuarios Activos Mensuales (MAU)** y **100,000 peticiones de IA**. La migración de modelos locales (Llama en GPU propia) a APIs comerciales (OpenAI/Groq) es crítica para la eficiencia del capital.

**Tabla Comparativa de Costos Mensuales (Proyección):**

| Concepto | Opción A: Self-Hosted (Llama 3 en AWS EC2 GPU) | **Opción B: Cloud Native (Recomendada - OpenAI/Groq)** |
| :--- | :--- | :--- |
| **Infraestructura IA** | Requiere instancia GPU dedicada 24/7 (AWS g4dn.xlarge). | Serverless / Pago por token. |
| **Costo Base** | ~$384 USD/mes (Fijo). | $0 USD (Variable). |
| **Costo Operativo** | Alto (DevOps, mantenimiento de drivers, updates). | Nulo (API Key management). |
| **Escalabilidad** | Limitada (Cuello de botella si sube la concurrencia). | Infinita (Auto-scaling). |
| **Costo Total Estimado** | **~$884 USD / mes** | **~$19 - $50 USD / mes** |

> **Decisión Estratégica:** Migrar a APIs comerciales reduce el OpEx en un **97%**, permitiendo destinar los fondos de inversión a adquisición de usuarios y no a mantenimiento de servidores [4].

## 5. Modelos de Monetización

Nuestra estrategia de ingresos evita cobrar comisiones por transacción (Take-rate) en etapas tempranas para eliminar fricción.

1.  **Modelo "VeraPlus" (SaaS B2C - Freemium):**
    * *Gratis:* Publicar productos, chat básico.
    * *Premium ($5.000 - $10.000 COP/mes):* Para "Power Sellers" (vendedores de almuerzos/postres). Incluye: Pines dorados en el mapa, analíticas de ventas y re-publicación automática en grupos de WhatsApp vía Bot.
2.  **Publicidad Hiper-Local (Ad Tech):**
    * Negocios aledaños al campus (fotocopiadoras, bares, papelerías) pagan por visibilidad geolocalizada ante un público 100% segmentado.
3.  **Monetización de Datos (B2B - Largo Plazo):**
    * Reportes de tendencias de consumo universitario para marcas de consumo masivo (siempre anonimizado).

## 6. Análisis de Riesgos y Mitigación

### 6.1. Riesgos Legales y Regulatorios
* **Protección de Datos (Ley 1581 de 2012):** Cumplimiento estricto del Habeas Data. Implementación de T&C con aceptación explícita y registro de bases de datos ante la SIC al superar los umbrales de activos [2].
* **Normativa Fintech (Captación Masiva):**
    * *Riesgo:* Retener dinero de usuarios (Escrow) sin licencia financiera.
    * *Mitigación:* **Modelo de Mandato de Cobro.** VeraMarket no toca el dinero. Los pagos son P2P directos (Efectivo/Nequi/DaviPlata) o a través de pasarelas aliadas certificadas (Wompi/ePayco) en el futuro. Referencia: Decreto 2555 de 2010 [3].

### 6.2. Riesgo Operativo y Seguridad
* **Seguridad Física:** Implementación de "VeraSpots" (Zonas de Intercambio Seguro) dentro del campus, ubicados cerca de vigilancia privada o cafeterías centrales.
* **Responsabilidad Civil:** Cláusulas claras en el Estatuto del Consumidor definiendo a VeraMarket como intermediario tecnológico, no distribuidor.

## 7. Roadmap de Inversión (Hitos)

Para preparar la compañía para una ronda de inversión Ángel (Ticket: $50k - $100k USD), establecemos los siguientes hitos:

* **Fase 1: Validación Técnica (Meses 1-3)**
    * "Despliegue a costo $0 COP usando Free Tiers. Piloto cerrado y exclusivo con la base de datos de emprendedores de Sinapsis UAO."
* **Fase 2: Tracción Pre-Seed (Meses 4-8)**
    * "Migración a servicios en la nube pagos y escalables de mejor calidad tras el éxito del piloto."
* **Fase 3: Ronda de Inversión (Mes 9+)**
    * "Expansión B2B2C: Integración de la plataforma con Centros de Emprendimiento e Innovación de otras universidades (ej. Javeriana, ICESI, Andes) para anexar sus emprendedores a nuestra red."

---

### Referencias y Fuentes

1.  **DANE (2025).** Gran Encuesta Integrada de Hogares (GEIH) - Mercado Laboral e Informalidad. Recuperado de: [https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral)
2.  **Secretaría del Senado.** Ley Estatutaria 1581 de 2012 (Régimen General de Protección de Datos Personales). Recuperado de: [http://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html](http://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html)
3.  **Superintendencia Financiera de Colombia.** Normativa sobre captación masiva y pasarelas de pago. Recuperado de: [https://www.superfinanciera.gov.co/](https://www.superfinanciera.gov.co/)
4.  **OpenAI & AWS Pricing.** Documentación oficial de precios API y EC2 On-Demand (Feb 2026). Recuperado de: [https://openai.com/api/pricing/](https://openai.com/api/pricing/) y [https://aws.amazon.com/ec2/pricing/on-demand/](https://aws.amazon.com/ec2/pricing/on-demand/)