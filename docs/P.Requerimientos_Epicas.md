**Requerimientos (F + NF) y Épicas**

- 

- Eduard Criollo Yule (Cod: 2220335)

- Juan Sebastián Delgado (Cod: 2216223)

- Felipe Charria Caicedo (Cod: 2216033)

- Valentina Velastegui López (Cod: 2226725)

**Épicas (Scrum)**

**Sprint 0: HU 0.1, HU 0.2, HU 0.3**

- **EP-00: Arquitectura Base y Flujos del Sistema**

  - **HU 0.1: Inicialización del monorepo y configuración del pipeline CI/CD.**

> **Descripción:** Como Desarrollador, quiero tener un monorepo configurado con Next.js y FastAPI, integrado con un pipeline de CI/CD, para poder desplegar cambios automáticamente y sin errores en los entornos de nube gratuitos.
>
> **Criterios de Aceptación:**

- Estructura de carpetas /frontend y /backend creada.

- GitHub Actions configurado (deploy.yml).

- Un *push* a la rama main dispara automáticamente el *linting* y el despliegue en Vercel (Frontend) y Render.com (Backend).

<!-- -->

- **HU 0.2: Modelado y despliegue del esquema de base de datos relacional con soporte espacial (PostGIS).**

> **Descripción:** Como Arquitecto de Datos, quiero desplegar el esquema en PostgreSQL habilitando PostGIS, para almacenar usuarios, productos y coordenadas geográficas de forma segura.
>
> **Criterios de Aceptación:**

- Instancia creada en capa gratuita (Supabase/Neon).

- Extensión PostGIS activada.

- Políticas *Row-Level Security (RLS)* habilitadas en todas las tablas por cumplimiento de la Ley 1581.

<!-- -->

- **HU 0.3: Configuración de dominios, certificados SSL y entornos.**

> **Descripción:** Como DevOps, quiero configurar los dominios y el SSL, para garantizar que toda la transferencia de datos (especialmente la geolocalización de la PWA) viaje cifrada.

- **Criterios de Aceptación:**

- Dominio veramarket.app configurado en Cloudflare.

- Tráfico HTTP forzado a HTTPS.

- Archivos .env segregados (Local, Staging, Producción) sin subir secretos al repositorio.

**Sprint 1: HU 1.1, HU 1.2, HU 1.3, HU 1.4, HU 1.5, HU 2.1, HU 2.2, HU 2.3**

- **EP-01: Autenticación Segura y Perfilamiento (Privacy-First)**

  - **HU 1.1: Inicio de sesión con código de un solo uso (OTP).**

**Descripción:** Como Usuario, quiero ingresar con mi correo y recibir un código temporal, para acceder a la app sin tener que memorizar otra contraseña.

**Criterios de Aceptación:**

- El sistema solo acepta correos concordante a los registros dados por sinapsis

- El correo llega en menos de 30 segundos.

- Se genera un token JWT seguro tras la validación exitosa.

<!-- -->

- **HU 1.2: Creación de perfil de usuario (por defecto: Rol Comprador).**

**Descripción:** Como Sistema, quiero registrar automáticamente al nuevo usuario con el rol de \"Comprador\", para delimitar sus permisos iniciales.

**Criterios de Aceptación:**

- Se crea el registro en la tabla users al validar el primer OTP.

- Solo se capturan datos mínimos (ID institucional, rol base).

<!-- -->

- **HU 1.3: Configuración de privacidad (Ocultar contacto).**

**Descripción:** Como Usuario, quiero un interruptor en mi perfil para ocultar mi número de teléfono, para proteger mi privacidad hasta que decida compartirlo.

**Criterios de Aceptación:**

- El toggle por defecto está en Oculto (Privacy by Design).

- Si está oculto, el backend enmascara o elimina el campo de contacto en la respuesta JSON pública.

<!-- -->

- **HU 1.4: Solicitud de Rol Vendedor con código de Sinapsis.**

**Descripción:** Como Comprador, quiero ingresar mi código de emprendedor de Sinapsis, para solicitar permisos de publicación en el marketplace.

**Criterios de Aceptación:**

- Formulario simple de 1 campo en el perfil del usuario.

- El estado de la solicitud queda marcado en la BD como \"Pendiente\".

<!-- -->

- **HU 1.5: Validación Sinapsis (Whitelist).**

**Descripción:** Como Sistema, quiero cruzar el código ingresado con la base de datos de Sinapsis, para aprobar el rol de Vendedor automáticamente sin intervención humana.

**Criterios de Aceptación:**

- Lectura exitosa del CSV/Endpoint de validación.

- Si hay coincidencia, el rol cambia a \"Vendedor\" inmediatamente.

<!-- -->

- **EP-02: Core PWA y Experiencia de Usuario Móvil**

  - **HU 2.1: Instalación de la aplicación en la pantalla de inicio.**

**Descripción:** Como Usuario móvil, quiero ver un botón para agregar VeraMarket a mi pantalla de inicio, para usarla como una app nativa sin consumir espacio de almacenamiento.

**Criterios de Aceptación:**

- manifest.json configurado correctamente (iconos, colores de tema).

- El navegador dispara el *prompt* nativo de \"Añadir a pantalla de inicio\".

<!-- -->

- **HU 2.2: Skeleton loaders y manejo de errores sin red.**

**Descripción:** Como Usuario en un campus con mala señal, quiero ver una pantalla de carga esquelética o un mensaje amigable si pierdo conexión, para no ver una pantalla rota o en blanco.

**Criterios de Aceptación:**

- Los componentes de Next.js muestran animaciones \"Skeleton\" mientras el Fetch de datos resuelve.

- Si la API da *timeout* o no hay internet, se muestra un banner de \"Sin conexión a internet\" interceptado por el Service Worker.

<!-- -->

- **HU 2.3: Configuración de notificaciones push web.**

**Descripción:** Como Vendedor, quiero recibir notificaciones push en mi celular cuando alguien me escriba, para no perder oportunidades de venta.

**Criterios de Aceptación:**

- Solicitud de permisos de notificación al usuario.

- El Service Worker es capaz de recibir y renderizar una alerta push en el dispositivo.

**Sprint 2: HU 3.1, HU 3.2, HU 3.3**

- **EP-03: Gestión del Catálogo P2P**

  - **HU 3.1: Creación de publicaciones (imágenes, categoría y precio en COP).**

**Descripción:** Como Vendedor, quiero subir un producto con foto, descripción y precio, para que los compradores lo vean en el catálogo.

**Criterios de Aceptación:**

- El precio solo permite formato numérico y asume moneda local (COP).

- La imagen se optimiza y sube a un bucket (ej. Supabase Storage) con límite de peso (ej. 2MB).

<!-- -->

- **HU 3.2: Edición y actualización de inventario.**

**Descripción:** Como Vendedor, quiero cambiar el estado de mi producto a \"Agotado\", para que los usuarios no me contacten si ya no me quedan empanadas o cupos.

**Criterios de Aceptación:**

- Botón de cambio de estado rápido (Disponible / Agotado).

- Solo el dueño del producto (validado por JWT) puede editarlo.

<!-- -->

- **HU 3.3: Eliminación o pausa temporal de publicaciones.**

**Descripción:** Como Vendedor, quiero ocultar o eliminar un producto de la vitrina sin borrar mi historial de ventas.

**Criterios de Aceptación:**

- Se implementa un *Soft-Delete* (ej. campo is_active = false en la BD) en lugar de un DELETE real.

- El producto desaparece instantáneamente del catálogo público.

**Sprint 3: HU 4.1, HU 4.2, HU 4.3, HU 5.1, HU 5.2, HU 5.3**

- **EP-04: Búsqueda Inteligente (MVP - Motor Open Source / Fallback)**

  - **HU 4.1: Búsqueda tradicional y filtros.**

**Descripción:** Como Comprador, quiero usar una barra de búsqueda para buscar productos exactos o filtrar por categorías, para encontrar lo que quiero rápido.

**Criterios de Aceptación:**

- Implementación de *Full-Text Search* usando tsvector en PostgreSQL.

- Latencia de respuesta menor a 1 segundo.

<!-- -->

- **HU 4.2: Búsqueda semántica usando el motor IA.**

**Descripción:** Como Comprador, quiero buscar con lenguaje natural o modismos caleños (ej. \"algo pa picar\", \"mecato\"), para que la IA me sugiera productos relevantes aunque no tengan esa palabra exacta en el título.

**Criterios de Aceptación:**

- Se envía la consulta a la API de Google Gemini (Gemini 2 Flash) para interpretación NLU, que extrae intención y categoría.

- *Arquitectura:* Si la API de Gemini falla o hay límite de uso, el sistema hace un *fallback* automático a la búsqueda tradicional de la HU 4.1 (Typesense Full-Text Search).

<!-- -->

- **HU 4.3: Visualización de recomendaciones (\"VeraMatch\").**

**Descripción:** Como Comprador, quiero ver productos similares al final del detalle de un producto, para descubrir otras opciones de emprendedores.

**Criterios de Aceptación:**

- Se muestran de 3 a 5 productos sugeridos basados en la misma categoría o etiquetas del producto actual.

<!-- -->

- **EP-05: Geolocalización Hiper-Local (Campus UAO)**

  - **HU 5.1: Visualización del mapa interactivo (OpenStreetMap).**

**Descripción:** Como Usuario, quiero ver un mapa del campus con pines marcando dónde están los vendedores, para encontrarlos fácilmente.

**Criterios de Aceptación:**

- Librería tipo *Leaflet/Mapbox* integrada con tiles de OpenStreetMap (costo \$0).

- Renderizado de pines leyendo coordenadas desde el backend.

<!-- -->

- **HU 5.2: Asignación de ubicación física a una publicación.**

**Descripción:** Como Vendedor, quiero pinchar en el mapa el lugar del campus donde me encuentro, para que los compradores puedan caminar hacia mí.

**Criterios de Aceptación:**

- Guardado de la latitud y longitud en formato GEOMETRY(Point) en PostGIS.

<!-- -->

- **HU 5.3: Filtrado del catálogo por radio de cercanía.**

**Descripción:** Como Comprador con hambre, quiero filtrar para ver solo los vendedores que estén a menos de 100 metros de mi edificio.

**Criterios de Aceptación:**

- Query espacial utilizando la función ST_DWithin de PostGIS para devolver resultados por radio en metros.

**  
**

**Sprint 4: HU 6.1, HU 6.2, HU 6.3, HU 6.4, HU 6.5**

- **EP-06: Negociación y Cierre P2P (Frictionless)**

  - **HU 6.1: Chat interno en tiempo real.**

**Descripción:** Como Usuario, quiero chatear con el vendedor dentro de la app, para negociar sin tener que darle mi número de WhatsApp.

**Criterios de Aceptación:**

- Implementación usando WebSockets (FastAPI websockets / Socket.io).

- Los mensajes se persisten en la base de datos para historial de auditoría.

<!-- -->

- **HU 6.2 y 6.3: Integración de Deep Link para Nequi / DaviPlata.**

**Descripción:** Como Comprador, quiero un botón que me abra directamente mi app de Nequi o DaviPlata con el número del vendedor, para pagar rápido sin digitar.

**Criterios de Aceptación:**

**Restricción de Arquitectura:** NO hay integración con APIs bancarias (está fuera del alcance del MVP). Solo se genera un *Deep Link* o *URI Scheme* (ej. nequi://\... o enlace web) que intenta abrir la app en el teléfono del usuario destino si el vendedor habilitó su número.

- **HU 6.4: Marcado manual de \"Transacción Completada\".**

**Descripción:** Como Vendedor y Comprador, quiero un botón en el chat para confirmar que el producto fue entregado.

**Criterios de Aceptación:**

- Ambos usuarios deben confirmar.

- El chat se cierra o cambia de estado visual a \"Completado\".

<!-- -->

- **HU 6.5: Registro automático del valor (GMV).**

**Descripción:** Como Analista de Negocio, quiero que al confirmarse la transacción (HU 6.4), el sistema guarde el valor de la venta, para poder calcular métricas financieras (GMV) sin cobrar comisiones.

**Criterios de Aceptación:**

- Un *trigger* o función backend inserta el valor transaccional en COP en una tabla de métricas en el momento en que el estado cambia a \"Completado\".

**Sprint 5: HU 7.1, HU 7.2, HU 7.3**

- **EP-07: Moderación y Reputación Comunitaria**

  - **HU 7.1: Calificación de transacciones (1 a 5 estrellas).**

**Descripción:** Como Comprador, quiero calificar al vendedor después de la entrega, para premiar el buen servicio.

**Criterios de Aceptación:**

- Se habilita un modal de calificación única y exclusivamente después de que la transacción se marque como completada (HU 6.4).

<!-- -->

- **HU 7.2: Visualización de reputación en el perfil.**

**Descripción:** Como Usuario, quiero ver el promedio de estrellas de un vendedor antes de comprarle, para generar confianza.

**Criterios de Aceptación:**

- El promedio se recalcula (o actualiza de manera asíncrona) y se muestra en la tarjeta del vendedor (ej. 4.8 / 5.0).

<!-- -->

- **HU 7.3: Sistema de reporte por comportamiento indebido.**

**Descripción:** Como Usuario, quiero un botón para denunciar un producto o perfil que incumpla las normas, para mantener seguro el campus digital.

**Criterios de Aceptación:**

- Botón \"Reportar\" con lista desplegable de razones (Spam, Ofensivo, Fraude).

- Si un producto recibe X número de reportes (ej. 3), el sistema lo oculta automáticamente (cambia is_active=false) hasta que un administrador lo revise.

- **EP-08: Gestión Avanzada de Pedidos, Analítica y Refactorización UX**

  - **HU 8.1 (Refactorización EP-06): Flujo de Estados, Seguimiento y Cancelación de Pedidos.**

**Descripción:** Como Usuario, quiero ver el historial de mi pedido y tener opciones para que sea aceptado, pausado, rechazado, cancelado o marcado como recibido, para tener control total de la logística.

**Criterios de Aceptación:**

- Implementación de máquina de estados en la tabla de transacciones (Pendiente, Aceptado, Pausado, Rechazado, Cancelado, Entregado).
- El frontend renderiza la línea de tiempo del pedido en el historial del usuario.

<!-- -->

  - **HU 8.2 (Refactorización EP-02/06): Notificaciones Transaccionales por Correo.**

**Descripción:** Como Usuario, quiero recibir una notificación por correo electrónico cada vez que el estado de mi pedido cambie (ej. "Pedido Aceptado" o "Pedido Cancelado"), para estar enterado sin tener la app abierta.

**Criterios de Aceptación:**

- Integración de un servicio de envíos transaccionales (ej. Resend o SendGrid).
- Disparadores automáticos (Triggers) en el backend ante la mutación de estado de un pedido.

<!-- -->

  - **HU 8.3 (Mejora EP-03): Parámetros Extra de Compra (Cantidad y Notas).**

**Descripción:** Como Comprador, quiero poder seleccionar la cantidad exacta del producto y añadir una nota personalizada en mi pedido antes de iniciar la negociación.

**Criterios de Aceptación:**

- Interfaz del producto incluye selector numérico de cantidad y campo de texto opcional.
- Los datos viajan en el payload inicial y se incrustan en el encabezado del chat.

<!-- -->

  - **HU 8.4 (Refactorización EP-06): Recibo Detallado y Opción de Pago en Efectivo.**

**Descripción:** Como Comprador, quiero ver una factura/recibo detallado con el subtotal y tener la opción explícita de "Pago en Efectivo", para formalizar transacciones físicas.

**Criterios de Aceptación:**

- La UI del chat renderiza una tarjeta de "Factura" (Cantidad x Precio Unitario = Total).
- Se añade el botón de Efectivo junto a los Deep Links de billeteras digitales.

<!-- -->

  - **HU 8.5 (Mejora EP-06): Bloqueo de Cierre de Negociación (Integridad Transaccional).**

**Descripción:** Como Sistema, quiero restringir la terminación de un chat o pedido sin que se haya registrado explícitamente el estado monetario, para garantizar la integridad de las métricas.

**Criterios de Aceptación:**

- El botón de "Completar Transacción" se mantiene deshabilitado hasta que se confirme un medio de pago o se clasifique como "Cancelado/Rechazado".

<!-- -->

  - **HU 8.6 (Mejora EP-01): Vistas Híbridas y Divididas (Cambio de Rol Rápido).**

**Descripción:** Como Emprendedor avalado por Sinapsis, quiero poder alternar ágilmente mi interfaz entre el modo "Mi Tienda (Vendedor)" y el modo "Catálogo (Comprador)" sin tener que cerrar sesión.

**Criterios de Aceptación:**

- Botón de "Switch Role" en el navbar/perfil.
- El cambio reconfigura inmediatamente el menú de navegación y las vistas de administración disponibles.

<!-- -->

  - **HU 8.7: Dashboard Financiero con Rangos Temporales variables.**

**Descripción:** Como Vendedor, quiero acceder a información financiera sobre mis ventas con filtros de tiempo ajustables, para analizar el rendimiento de mi emprendimiento.

**Criterios de Aceptación:**

- Visualización de métricas de ingresos y pedidos completados.
- Selectores de tiempo (Día, Semana, Mes, Semestre) ejecutando consultas agregadas en PostgreSQL.

<!-- -->

  - **HU 8.8 (Refactorización EP-03): Modos de Visualización del Catálogo y Reactividad.**

**Descripción:** Como Usuario, quiero un botón para cambiar el catálogo entre modo "Cuadrícula" y "Lista", y que la interfaz recargue los estados automáticamente al pulsar un botón sin refrescar la página.

**Criterios de Aceptación:**

- Toggle de Layout con persistencia en el dispositivo del usuario.
- Implementación de caché reactiva y mutaciones optimistas (ej. SWR / React Query) en botones de acción para actualizar el DOM instantáneamente.

<!-- -->

  - **HU 8.9: Sistema de Cupones de Descuento.**

**Descripción:** Como Vendedor, quiero poder generar códigos de descuento para compartirlos, e integrarlos en el flujo de cobro del pedido para atraer más estudiantes.

**Criterios de Aceptación:**

- CRUD administrativo de cupones (% o valor fijo).
- Campo en la factura del pedido (HU 8.4) para validar y recalcular el Total a pagar.

**Requerimientos Funcionales (F)**

- **RF-01 (Gestión de Identidad):** El sistema debe validar que los correos electrónicos ingresados en el registro pertenezcan a los registros dados por sinapsis uao (archivos .csv)

- **RF-02 (Autenticación OTP):** El sistema debe enviar un código numérico temporal al correo del usuario para autenticar su acceso, prescindiendo de contraseñas.

- **RF-03 (Publicación de Ofertas**): El sistema debe permitir a los usuarios subir hasta 3 imágenes, asignar un título, descripción, categoría y precio (COP) a sus productos o servicios.

- **RF-04 (Búsqueda y Filtrado):** El sistema debe proveer una barra de búsqueda y filtros por categoría, aplicando IA para coincidencias de lenguaje natural.

- **RF-05 (Georreferenciación):** El sistema debe renderizar un mapa interactivo local y colocar pines en las coordenadas donde el vendedor indique que entregará el producto.

- **RF-06 (Comunicación P2P):** El sistema debe facilitar una interfaz de mensajería (chat) instantánea entre el comprador y el vendedor.

- **RF-07 (Enlaces de Pago Externos):** El sistema debe generar botones que abran directamente las aplicaciones de billeteras digitales (Nequi/DaviPlata) instaladas en el dispositivo del usuario.

- **RF-08 (Calificación):** El sistema debe permitir a las partes evaluarse mutuamente (1 a 5 estrellas) una vez concluida una transacción.

- **RF-09 (Tracking de Transacciones y GMV):** El sistema debe registrar cada cambio de estado a "Transacción Completada" y almacenar en una tabla de analíticas el precio listado del producto en ese momento, permitiendo calcular el volumen total transaccionado (GMV) diario y mensual.

- **RF-10 (Gestión de Pedidos Avanzada):** El sistema debe manejar una máquina de estados estricta para los pedidos (Pendiente, Aceptado, Pausado, Rechazado, Cancelado, Entregado) e integrar un bloqueo transaccional si no se ha definido el método de pago.

- **RF-11 (Dashboard Financiero):** El sistema debe proveer un dashboard analítico para el vendedor, mostrando resúmenes financieros (ingresos, descuentos, transacciones) y gráficas temporales.

- **RF-12 (Gestión de Cupones):** El sistema debe permitir la creación, validación y redención de cupones de descuento (porcentuales o fijos en COP) en el flujo de pedidos.

**Requerimientos No Funcionales (RNF)**

- **RNF-01 (Rendimiento de Búsqueda):** El tiempo promedio de respuesta para búsquedas en el catálogo (tradicionales o semánticas) no debe exceder los 1.8 segundos.

- **RNF-02 (Concurrencia y Escalabilidad):**

La arquitectura backend (FastAPI) debe soportar 500 usuarios concurrentes y picos de hasta 1,200 usuarios/hora sin degradación de servicio. La base de datos debe soportar un catálogo de 15,000 productos activos.

- **RNF-03 (Instalabilidad PWA):**

La interfaz frontend (Next.js) debe cumplir con los estándares de Progressive Web App (Service Worker base, manifest.json) para permitir su instalación en iOS y Android.

- **RNF-04 (Latencia de Comunicación Verificable):**

Durante una prueba de carga simulando 500 usuarios concurrentes enviando mensajes simultáneamente, el sistema de WebSockets debe procesar y entregar el 95% de los mensajes (percentil p95) en un tiempo de viaje de ida y vuelta (round-trip time) inferior a 500 milisegundos.

- **RNF-05 (Seguridad y Privacidad):**

Todo dato sensible en la base de datos (PostgreSQL) debe estar encriptado. El sistema no expondrá directamente el número de teléfono del usuario a menos que este lo habilite explícitamente en su privacidad.

- **RNF-06 (Tolerancia a fallos de red):**

Si el usuario pierde la conexión a internet de la universidad, la app debe mostrar una advertencia de \"Sin conexión\" de forma controlada y no romper la interfaz gráfica de manera abrupta.

- **RNF-07 (Escalabilidad de Fases):** La arquitectura de la Fase Piloto debe operar íntegramente en servicios de capa gratuita (Free Tier). El código debe ser agnóstico a la infraestructura (Cloud-Native) para permitir la migración sin reescritura de código hacia servicios pagos (AWS RDS, Vercel Pro) una vez se confirme la escalabilidad futura.
