# Informe de Exposicion - Sprint 3

## 1. Estado general real del Sprint 3

Estado actual: implementacion funcional completa del alcance definido (HU 4.1, 4.2, 5.1, 5.2, 5.3), con pendientes operativos de despliegue y hardening.

Completado en codigo:
- Busqueda hibrida con NLU + cuota + fallback.
- Geolocalizacion de vendedor en perfil.
- Mapa interactivo con consumo de resultados geo.
- Sincronizacion de indice Typesense en CRUD de productos.
- Pruebas unitarias nuevas para busqueda, cuota y ubicacion.

Pendiente para cierre total:
- Configurar GEMINI_API_KEY real y API key segura de Typesense por ambiente.
- Ejecutar validacion final de migraciones en ambiente limpio y con datos existentes.
- Implementar o documentar proceso de reindexado inicial (backfill) hacia Typesense.

## 2. Funciones agregadas por historia de usuario

HU 4.1 - Busqueda tradicional y filtros:
- Endpoint principal de busqueda: /api/v1/products/search.
- Implementacion en [backend/app/routers/products.py](backend/app/routers/products.py#L93).
- Soporta query, categoria y limite.
- Fallback textual PostgreSQL en [backend/app/services/product_service.py](backend/app/services/product_service.py#L126).

HU 4.2 - Busqueda semantica con fallback:
- NLU con Gemini en [backend/app/services/nlu_service.py](backend/app/services/nlu_service.py#L52).
- Consumo de cuota diaria en [backend/app/services/quota_service.py](backend/app/services/quota_service.py#L55).
- Recuperacion principal en Typesense en [backend/app/services/typesense_service.py](backend/app/services/typesense_service.py#L203).
- Regla de fallback por no autenticado, cuota agotada o fallo NLU/Typesense en [backend/app/routers/products.py](backend/app/routers/products.py#L93).
- Cuota consultable en /api/v1/users/me/search-quota desde [backend/app/routers/users.py](backend/app/routers/users.py#L117).

HU 5.1 - Visualizacion de mapa interactivo:
- Pantalla de mapa en [frontend/app/map/page.tsx](frontend/app/map/page.tsx#L27).
- Componente de mapa dinamico en [frontend/components/MapView.tsx](frontend/components/MapView.tsx#L34).
- Render Leaflet en [frontend/components/map/LeafletMap.tsx](frontend/components/map/LeafletMap.tsx#L50).

HU 5.2 - Asignacion de ubicacion del vendedor:
- Endpoints /api/v1/locations/me en [backend/app/routers/locations.py](backend/app/routers/locations.py#L19).
- Servicio de persistencia geo en [backend/app/services/location_service.py](backend/app/services/location_service.py).
- UI en perfil vendedor en [frontend/app/profile/page.tsx](frontend/app/profile/page.tsx#L103).

HU 5.3 - Filtro por radio y proximidad:
- Parametros lat, lng y radius_meters en busqueda en [backend/app/routers/products.py](backend/app/routers/products.py#L93).
- Filtro geoespacial Typesense por radio en [backend/app/services/typesense_service.py](backend/app/services/typesense_service.py#L203).
- Consumo desde vista mapa en [frontend/app/map/page.tsx](frontend/app/map/page.tsx#L51).

Sincronizacion de indice:
- Inicializacion de coleccion en startup en [backend/app/main.py](backend/app/main.py#L24).
- Sync al crear/editar/pausar producto en [backend/app/routers/products.py](backend/app/routers/products.py#L224).
- Sync al actualizar estado y eliminar en [backend/app/routers/products.py](backend/app/routers/products.py#L273).

## 3. Pruebas automatizadas nuevas

Cobertura nueva en backend:
- Busqueda hibrida en [backend/app/tests/test_search_hybrid.py](backend/app/tests/test_search_hybrid.py#L27).
- Ubicacion vendedor en [backend/app/tests/test_locations.py](backend/app/tests/test_locations.py#L28).
- Cuota diaria de busqueda en [backend/app/tests/test_users.py](backend/app/tests/test_users.py#L253).

## 4. Pruebas Postman incluidas para Sprint 3

Coleccion actualizada y lista para importar/ejecutar.
Archivo actual: [docs/postman/VeraMarket_Sprints_1_2_3.postman_collection.json](docs/postman/VeraMarket_Sprints_1_2_3.postman_collection.json).

Actualizacion aplicada en este repositorio:
- Se agrego la carpeta 5. Sprint 3 Hibrido (Busqueda + Geo) en [docs/postman/VeraMarket_Sprints_1_2_3.postman_collection.json](docs/postman/VeraMarket_Sprints_1_2_3.postman_collection.json#L600).
- Se agregaron variables de entorno para busqueda y geo en [docs/postman/VeraMarket_Sprints_1_2_3.postman_environment.json](docs/postman/VeraMarket_Sprints_1_2_3.postman_environment.json#L48).
- Ambos archivos JSON fueron validados por parseo local exitoso.

Carpeta incluida en Postman: 5. Sprint 3 Hibrido (Busqueda + Geo)

Prueba 5.1 - Obtener cuota diaria:
- Metodo: GET
- URL: {{base_url}}/api/v1/users/me/search-quota
- Header: Authorization Bearer {{token}}
- Tests sugeridos:
  - status 200
  - existe daily_limit
  - existe searches_used
  - existe remaining
  - guardar remaining como variable quota_remaining

Prueba 5.2 - Configurar ubicacion vendedor:
- Metodo: PUT
- URL: {{base_url}}/api/v1/locations/me
- Header: Authorization Bearer {{token}}
- Body ejemplo:
  - lat: 3.3516
  - lng: -76.5320
  - campus: UAO
  - label: Cafeteria Central
- Tests sugeridos:
  - status 200
  - lat y lng existen
  - campus es UAO

Prueba 5.3 - Consultar ubicacion vendedor:
- Metodo: GET
- URL: {{base_url}}/api/v1/locations/me
- Header: Authorization Bearer {{token}}
- Tests sugeridos:
  - status 200
  - respuesta null o objeto
  - si hay objeto, validar user_id

Prueba 5.4 - Busqueda semantica autenticada:
- Metodo: GET
- URL: {{base_url}}/api/v1/products/search?q=busco algo pa picar&limit=20
- Header: Authorization Bearer {{token}}
- Tests sugeridos:
  - status 200
  - existe meta.search_mode
  - existe meta.quota_remaining
  - items es arreglo

Prueba 5.5 - Busqueda full-text forzada:
- Metodo: GET
- URL: {{base_url}}/api/v1/products/search?q=audifonos&use_semantic=false
- Header: Authorization Bearer {{token}}
- Tests sugeridos:
  - status 200
  - meta.search_mode no debe ser semantic

Prueba 5.6 - Busqueda con radio geoespacial:
- Metodo: GET
- URL: {{base_url}}/api/v1/products/search?q=snack&lat=3.3516&lng=-76.5320&radius_meters=300&limit=50
- Header: Authorization Bearer {{token}}
- Tests sugeridos:
  - status 200
  - items es arreglo
  - si hay distance_meters, debe ser <= 300

Prueba 5.7 - Validacion fallback sin token:
- Metodo: GET
- URL: {{base_url}}/api/v1/products/search?q=mecato
- Sin Authorization
- Tests sugeridos:
  - status 200
  - meta.search_mode es fallback_fulltext
  - meta.reason es unauthenticated

Prueba 5.8 - Eliminar ubicacion vendedor:
- Metodo: DELETE
- URL: {{base_url}}/api/v1/locations/me
- Header: Authorization Bearer {{token}}
- Tests sugeridos:
  - status 200
  - deleted true o false

## 5. Variables nuevas incluidas en Postman Environment

Archivo: [docs/postman/VeraMarket_Sprints_1_2_3.postman_environment.json](docs/postman/VeraMarket_Sprints_1_2_3.postman_environment.json).

Variables agregadas:
- search_query_semantic = busco algo pa picar
- search_query_fulltext = audifonos
- search_lat = 3.3516
- search_lng = -76.5320
- search_radius = 300
- quota_remaining =
- location_label = Cafeteria Central

## 6. Que falta configurar para cierre completo

Infraestructura y entorno:
- Definir GEMINI_API_KEY real en despliegue local/staging/prod.
- Cambiar API key default de Typesense por una segura.
- Confirmar que Typesense levanta en Docker Compose con volumen persistente en [docker-compose.yml](docker-compose.yml#L36).

Variables de entorno:
- Variables de Sprint 3 ya documentadas en [backend/.env.example](backend/.env.example) y [.env.example](.env.example).
- Variables actuales en settings si existen en [backend/app/core/config.py](backend/app/core/config.py#L39).

Datos y migraciones:
- Ejecutar migracion Sprint 3 en [backend/alembic/versions/20260409_01_sprint3_hybrid_search_baseline.py](backend/alembic/versions/20260409_01_sprint3_hybrid_search_baseline.py).
- Confirmar consistencia entre base nueva y base ya existente.

Operacion de indice:
- Falta proceso formal de reindexado inicial de productos historicos hacia Typesense.
- Hoy existe sync por eventos, pero no comando de backfill declarado para inicializacion masiva.

Documentacion y demo:
- Validar que el equipo use la coleccion Postman actualizada con carpeta de Sprint 3 hibrido.
- Alinear guion de demo con historias 4.1, 4.2, 5.1, 5.2 y 5.3.

Alcance academico:
- HU 4.3 (recomendaciones VeraMatch) no esta implementada en endpoints; si la catedra exige HU 4.3 dentro de Sprint 3, aun queda pendiente.

## 7. Guion de exposicion - prueba una por una (historia por historia)

Bloque HU 4.1 - Busqueda y filtros:
1. Mostrar endpoint de busqueda en [backend/app/routers/products.py](backend/app/routers/products.py#L93).
2. Ejecutar Postman 5.5 (full-text forzada).
3. Mostrar respuesta con items y meta.search_mode.
4. Mensaje de exposicion: se garantiza busqueda util aun sin IA.

Bloque HU 4.2 - Semantica + cuota + fallback:
1. Ejecutar Postman 5.1 para leer cuota.
2. Ejecutar Postman 5.4 semantica autenticada.
3. Verificar meta.search_mode y quota_remaining.
4. Ejecutar Postman 5.7 sin token para mostrar fallback.
5. Mensaje de exposicion: control de costos con continuidad operativa.

Bloque HU 5.2 - Setup ubicacion vendedor:
1. Ejecutar Postman 5.2 (PUT ubicacion).
2. Ejecutar Postman 5.3 (GET ubicacion).
3. Mostrar en perfil frontend que carga coordenadas desde [frontend/app/profile/page.tsx](frontend/app/profile/page.tsx#L103).

Bloque HU 5.1 y HU 5.3 - Mapa y radio:
1. Ejecutar Postman 5.6 con radio de 300m.
2. Abrir vista mapa en [frontend/app/map/page.tsx](frontend/app/map/page.tsx#L27).
3. Mostrar que el mapa consume /products/search y refleja pines dentro de radio.

Cierre tecnico del sprint:
1. Mostrar pruebas automatizadas en [backend/app/tests/test_search_hybrid.py](backend/app/tests/test_search_hybrid.py#L27), [backend/app/tests/test_locations.py](backend/app/tests/test_locations.py#L28) y [backend/app/tests/test_users.py](backend/app/tests/test_users.py#L253).
2. Mostrar documento arquitectonico en [docs/Documento_Arquitectura_Hibrida.md](docs/Documento_Arquitectura_Hibrida.md).
3. Mostrar pendientes de cierre operativo (llaves reales por ambiente + validacion migraciones + reindex).
