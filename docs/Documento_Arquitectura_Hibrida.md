# Arquitectura Híbrida de Búsqueda (Gemini 1.5 Flash + Typesense)

## Integración con Entregables Universitarios

### 1. Proyecto Informático: Arquitectura Híbrida de Dos Capas

La solución técnica diseñada se fundamenta en desacoplar el procesamiento del lenguaje natural de la ejecución de la consulta a la base de datos para asegurar el cumplimiento del RNF-01 (Latencia <100ms).

#### Diseño del Pipeline
1. **Capa NLU (Gemini 1.5 Flash)**: Actúa como router y traductor. Cuando el estudiante universitario ingresa un modismo como *"algo pa picar barato"*, en vez de consultar esto con coincidencia léxica, Gemini extrae:
   ```json
   { "query_clean": "barato", "tags": ["snack", "postre", "mecato"], "category": "comida" }
   ```
2. **Pre-Filtering**: El backend inyecta la "category" extraída para asegurar que un postre nunca se empareje con artículos de belleza (alucinación mitigada).
3. **Typesense Search Engine**: Intercepta el vector estructurado y lo ejecuta a través de su motor residente en RAM, proveyendo filtrado por geolocalización de radio dinámico (`GeoSearch`).

### 2. Formulación y Evaluación de Proyectos: Impacto Económico y Costos

Integrar inteligencia artificial acarrea costos variables inciertos. Por esto, la sustentación de escalabilidad del negocio está protegida por:
- **Fallback Tolerante a Fallos**: Si un usuario sobrepasa el límite de cuota inteligente o si la API falla, Typesense retoma instantáneamente como motor FTS libre de cargos de API.
- **Cuota de 10 Búsquedas/Día**: Controla matemáticamente el techo máximo de costos de tokens por usuario activo (CAC - Costo Adquisición y Mantenimiento de Cliente), resultando en operaciones económicamente predecibles y aptas.

### 3. Gestión de la Innovación: El "Océano Azul" del Marketplace Local

El componente innovador radica en la **democratización semántica hiperlocal**. Los marketplaces genéricos exigen al usuario dominar las palabras clave exactas del vendedor (ej. "empanada horneada"). Al incorporar Gemini 1.5 con instrucciones enfocadas en los campus colombianos, VeraMarket rompe esa asimetría de información:
- Permite a los estudiantes buscar cómo hablan ("mecato", "algo dulce").
- Eleva las métricas de conversión gracias a las **Recomendaciones Cruzadas (VeraMatch)**.
- Combina estas búsquedas con la geolocalización dentro del campus, resolviendo el elemento más friccional del e-commerce: el costo y tiempo logístico.
