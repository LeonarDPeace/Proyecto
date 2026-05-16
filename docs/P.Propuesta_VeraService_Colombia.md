# Propuesta de Inversión: VeraMarket
**"La Super-App de la Economía Universitaria en LatAm"**

---

**Fase:** Pre-Seed / Validación de MVP.  
**Ubicación:** Cali, Valle del Cauca, Colombia.  
**Sede de Operaciones:** Esquema híbrido (Home Office del equipo fundador y espacio de Coworking en el Centro de Innovación Sinapsis UAO).  
**Equipo:** Ingeniería de Software (Founding Team): Eduard Criollo Yule, Juan Sebastián Delgado, Felipe Charria Caicedo, Valentina Velastegui López.  
**Documento:** Investment Memo, Technical Validation & Project Charter.  
**Fecha:** Febrero de 2026.

---

## 1. Resumen Ejecutivo

**VeraMarket** es una plataforma Web Progresiva (PWA) diseñada para ser la vitrina digital de los emprendedores institucionales. Nuestra operación física está radicada en Cali. Al aliarnos con el Centro de Innovación (Sinapsis) de la UAO, resolvemos la falta de canales de venta directos.

Nacida como una iniciativa de ingeniería con arquitectura **Open Source** para validación a costo cero ($0 COP), VeraMarket ha evolucionado hacia un modelo de negocio escalable. Nuestra propuesta de valor conecta la oferta hiper-local (comida, tutorías, productos de segunda mano) con una demanda cautiva de miles de estudiantes, resolviendo los problemas de confianza y logística que plataformas generalistas no logran atender.

Buscamos capital semilla para transformar nuestro MVP validado tecnológicamente en una operación comercial sostenible, migrando de infraestructura local a Cloud-Native para soportar 5,000+ usuarios activos mensuales.

## 2. El Problema a Resolver

Los emprendimientos formales nacidos dentro de la universidad y apoyados por los centros de innovación carecen de un canal de comercialización digital centralizado y exclusivo para la comunidad universitaria. Aunque estos emprendedores reciben formación, enfrentan el "valle de la muerte" al intentar vender sus productos dependiendo de grupos de WhatsApp ineficientes o compitiendo en desventaja en plataformas genéricas, lo que limita su visibilidad institucional.

## 3. Oportunidad de Mercado

El mercado universitario en Colombia es un reflejo de la economía nacional, caracterizado por una alta informalidad y un fuerte espíritu emprendedor.

* **Espíritu Emprendedor:** El estudio GUESSS Colombia (EAFIT) indica que el 28.8% de los estudiantes tiene intención de fundar empresa, pero carecen de herramientas digitales profesionales para empezar [2].
* **Validación de Demanda:** Un campus promedio tiene una población flotante de +20,000 personas diarias. Capturar solo el 10% en un campus valida un mercado de 2,000 usuarios recurrentes.

## 4. Panorama Competitivo y Ventaja Única

A diferencia de los competidores, VeraMarket ofrece **Confianza de Nicho** (verificación mediante correo institucional) y **Georreferenciación de Campus**.

| Competidor | Tipo | Debilidad Crítica | La Solución VeraMarket |
| :--- | :--- | :--- | :--- |
| **Grupos de WhatsApp** | Directo | Caos, spam, sin historial, efímero. | Catálogo estructurado y búsqueda semántica. |
| **Instagram Stores** | Directo | Difícil descubrimiento hiper-local. | Mapa interactivo del campus (OpenStreetMap). |
| **Rappi / Food Apps** | Indirecto | Comisiones altas (15-30%) y logística compleja. | Modelo P2P sin intermediación logística. |
| **Facebook Marketplace** | Directo | Inseguro, sin filtro de comunidad. | **Entorno seguro:** Solo correos institucionales. |

## 5. Solución Técnica y Estrategia de Escalabilidad

Una Progressive Web App (PWA) de comercio P2P enfocada en la actualización de datos en tiempo real mediante conexión constante. La plataforma centralizará la oferta y demanda, permitiendo búsquedas inteligentes asistidas por Google Gemini 1.5 Flash + Typesense y gestión de catálogos sin consumir almacenamiento nativo del dispositivo.

Actualmente contamos con un MVP funcional basado en soberanía tecnológica (Self-Hosted). Para la fase de inversión, ejecutaremos una migración estratégica a servicios Cloud para garantizar estabilidad y reducción de costos operativos (OpEx).

### 5.1. Arquitectura Actual (MVP - Fase de Validación)
* **Frontend:** PWA con Next.js 14 (App Router) + TypeScript + Tailwind CSS.
* **Backend:** FastAPI (Python 3.11+) con SQLAlchemy 2.0 (async).
* **Base de Datos:** PostgreSQL 15 + PostGIS (geolocalización).
* **Mapas:** OpenStreetMap + Leaflet.js (Gratuito).
* **IA:** Google Gemini 1.5 Flash para NLU + Typesense para búsqueda full-text.
* **Infraestructura:** Free Tiers — Vercel, Render.com, Supabase/Neon, Cloudflare.

### 5.2. Validación de Escalabilidad Financiera (Cloud Migration)
Hemos analizado el costo de escalar a **5,000 Usuarios Activos Mensuales (MAU)** y **100,000 peticiones de IA**. 

**Tabla Comparativa de Costos Mensuales (Proyección):**

| Concepto | Opción A: Self-Hosted (Llama 3 en AWS EC2 GPU) | **Opción B: Cloud Native (Recomendada - Google Gemini)** |
| :--- | :--- | :--- |
| **Infraestructura IA** | Requiere instancia GPU dedicada 24/7 (AWS g4dn.xlarge). | Serverless / Pago por token (Gemini API). |
| **Costo Base** | ~$384 USD/mes (Fijo). | $0 USD (Variable, Free Tier generoso). |
| **Costo Operativo** | Alto (DevOps, mantenimiento de drivers, updates). | Nulo (API Key management). |
| **Escalabilidad** | Limitada (Cuello de botella si sube la concurrencia). | Infinita (Auto-scaling). |
| **Costo Total Estimado** | **~$884 USD / mes** | **~$10 - $30 USD / mes** |

> **Decisión Estratégica:** Migrar a APIs comerciales reduce el OpEx en un **97%**, permitiendo destinar los fondos de inversión a adquisición de usuarios y no a mantenimiento de servidores [4].

## 6. Modelos de Monetización

Nuestra estrategia de ingresos evita cobrar comisiones por transacción (Take-rate) en etapas tempranas para eliminar fricción.

1.  **Modelo "VeraPlus" (SaaS B2C - Freemium):** Premium ($5.000 - $10.000 COP/mes) para "Power Sellers". Incluye: Pines dorados en el mapa, analíticas de ventas avanzadas y re-publicación automática en WhatsApp.
2.  **Publicidad Hiper-Local (Ad Tech):** Negocios aledaños al campus pagan por visibilidad geolocalizada ante un público segmentado.
3.  **Monetización de Datos (B2B - Largo Plazo):** Reportes de tendencias de consumo universitario para marcas de consumo masivo (anonimizado).

## 7. Análisis de Riesgos y Mitigación

* **Protección de Datos (Ley 1581 de 2012):** Cumplimiento estricto del Habeas Data. Implementación de T&C y RLS en la base de datos [2].
* **Normativa Fintech (Captación Masiva):** **Modelo de Mandato de Cobro.** VeraMarket no toca el dinero. Los pagos son P2P directos (Efectivo/Nequi/DaviPlata).
* **Seguridad Física:** Implementación de "VeraSpots" (Zonas de Intercambio Seguro) dentro del campus.
* **Complejidad IA y Latencia:** Implementación del **Patrón Adapter**. Si la API de Gemini falla, el sistema hace un *fallback* automático a Typesense (Full-Text Search en RAM).

## 8. Project Charter: Objetivos y Criterios de Éxito del Piloto

El alcance del MVP (11 Semanas) abarca el "Happy Path" del comercio P2P: Publicar, Encontrar (búsqueda IA), Contactar y Acordar entrega.

### 8.1 Objetivos SMART
* **Negocio:** Alcanzar 100 usuarios activos y 50 transacciones registradas al finalizar la semana 11, garantizando la centralización y seguridad de la información.
* **Técnico:** Desplegar una PWA instalable con latencia de carga inicial < 3 segundos y un motor de búsqueda semántica (Gemini + Typesense) 100% operativo.

### 8.2 Criterios de Éxito
1. **Criterio Técnico (Disponibilidad):** Uptime mínimo del **99.0%** durante el piloto.
2. **Criterio de Adopción (Tracción):** Adquisición de **500 usuarios registrados** y validados en el primer mes de operación comercial.
3. **Criterio de Negocio (Volumen P2P):** Alcanzar un promedio de **200 transacciones completadas por día** al finalizar el piloto extendido.
4. **Criterio Financiero (GMV):** Volumen de mercancía bruta proyectado de **$15.000.000 COP/mes**.
5. **Criterio de Calidad Comunitaria:** El **90%** de las calificaciones post-transacción deben ser iguales o superiores a 4.0 estrellas.

## 9. Roadmap de Inversión (Hitos)

* **Fase 1: Validación Técnica (Meses 1-3)**
    * Despliegue a costo $0 COP usando Free Tiers. Piloto cerrado y exclusivo con emprendedores de Sinapsis UAO.
* **Fase 2: Tracción Pre-Seed (Meses 4-8)**
    * Migración a servicios en la nube pagos (AWS/Render) para soportar el escalamiento tras el éxito del piloto.
* **Fase 3: Ronda de Inversión (Mes 9+)**
    * Expansión B2B2C: Integración con Centros de Innovación de otras universidades (ej. Javeriana, ICESI, Andes) para anexar sus emprendedores a nuestra red.

---

### Referencias y Fuentes

1.  **DANE (2025).** Gran Encuesta Integrada de Hogares (GEIH) - Mercado Laboral e Informalidad.
2.  **Secretaría del Senado.** Ley Estatutaria 1581 de 2012 (Régimen General de Protección de Datos Personales).
3.  **Superintendencia Financiera de Colombia.** Normativa sobre captación masiva y pasarelas de pago.
4.  **Google AI & AWS Pricing.** Documentación oficial de precios Gemini API y EC2 On-Demand (Feb 2026).