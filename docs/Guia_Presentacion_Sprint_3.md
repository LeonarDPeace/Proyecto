# Guion de Presentación - Sprint 3: Catálogo Inteligente y Geolocalización (Arquitectura Híbrida)

## 📌 Introducción (1 minuto)
**Objetivo:** Mostrar cómo VeraMarket soluciona el problema de descubrimiento de productos locales mediante búsqueda de Inteligencia Artificial limitada financieramente, cruce de sugerencias y geolocalización.

---

## 🚀 Historia de Usuario 4.1: Búsqueda Tradicional y Filtros
**Exposición:** "Los usuarios necesitan encontrar específicamente lo que buscan con menos de 100 milisegundos de latencia. Por esto implementamos Typesense como nuestro motor de búsqueda en RAM."
* **Acción en App:** 
  1. Entra a "Catálogo".
  2. Digita una palabra clave exacta o presiona los filtros rápidos de categoría (ej. "Comida").
  3. Observa la velocidad de carga frente al Sprint anterior (Typesense interceptando la petición).

## 🚀 Historia de Usuario 4.2: Búsqueda Semántica con IA
**Exposición:** "No todos buscan de la misma forma. Si alguien en la central necesita mecato, no buscará 'Dulce horneado'. Usamos **Gemini 1.5 Flash (Capa NLU)** para extraer etiquetas y entender modismos colombianos. Para mantener el negocio rentable, implementamos un candado lógico: máximo 10 búsquedas al día."
* **Acción en App:**
  1. Ingresa a "Catálogo".
  2. Escribe una frase informal (ej. "algo pa picar", "mecato dulce").
  3. Muestra cómo el frontend te notifica "Búsqueda inteligente activada".
  4. Muestra cómo el contador de límite ("Quedan X búsquedas") se actualiza automáticamente protegiendo la base de costos.

## 🚀 Historia de Usuario 4.3: VeraMatch (Recomendaciones)
**Exposición:** "La segunda fricción de compra es la falta de descubrimiento. La plataforma ahora sugiere orgánicamente productos cruzados dependiendo del contexto del que visualizamos."
* **Acción en App:**
  1. Haz clic sobre un producto cualquiera para ver su detalle completo.
  2. Haz scroll hasta la parte inferior de la página.
  3. Muestra la nueva sección **✨ VeraMatch**, exponiendo que estos elementos secundarios comparten directamente relación con la categoría de visualización principal.

## 🚀 Historia de Usuario 5.1 & 5.2: Mapa Interactivo y Asignación de Ubicación
**Exposición:** "El concepto de P2P hiperlocal se resume en encontrar a quién comprarle a pasos de distancia. El vendedor ahora puede notificar su paradero dentro de la universidad."
* **Acción en App:**
  1. Ve a "Mi Perfil" como Vendedor.
  2. En "Ubicación en Campus", abre el mapa interactivo nativo (Leaflet/OSM).
  3. Arrastra el cursor o cliquea directamente un punto del mapa y pulsa guardar (Se enviarán las coordenadas `ST_Point` a nuestra base de datos).

## 🚀 Historia de Usuario 5.3: Filtrado por Radio de Cercanía
**Exposición:** "El paso definitivo ocurre cuando el comprador filtra todo el marketplace usando las coordenadas cargadas en Typesense para ver resultados puramente cercanos en espacio."
* **Acción en App:**
  1. Accede a la pantalla de "Mapa de Campus" (`/map`).
  2. Usa el menú desplegable de "Radio" y redúcelo (ej. a 100m).
  3. Demuestra cómo solo quedan visibles los productos/vendedores que cumplan esa proximidad espacial gracias a Typesense/PostGIS.

---
## 🏁 Conclusión y Postman Analytics
* Abrir momentáneamente Postman o un visor de Base de datos (DBeaver) para mostrar la tabla `location` (cómo figuran los Puntos en PostGIS) y cómo en la API el endpoint maneja el fallback textual en caso de falla con IA, sustentando la Arquitectura tolerante a fallos evaluada en "Formulación de proyectos".
