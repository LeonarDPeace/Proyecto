# Guía de Presentación: VeraMarket — Sprint 3

**Gestión del Catálogo P2P, Navegación y Mejoras de UX**

---

## Resumen del Sprint

El Sprint 3 se centra en la **Épica EP-03: Gestión del Catálogo P2P**, convirtiendo a VeraMarket de un marketplace con infraestructura base a una plataforma donde los vendedores verificados pueden **gestionar activamente** sus publicaciones. Adicionalmente, se implementó un **menú de navegación global** que unifica la experiencia PWA.

---

## HU 3.1 — Publicación de Productos

**Como** vendedor verificado (Sinapsis),
**quiero** crear publicaciones de productos con nombre, descripción, precio, categoría e imágenes,
**para** ofrecer mis productos a la comunidad universitaria.

### Funciones Implementadas

| Función | Endpoint | Método |
| :--- | :--- | :--- |
| Crear producto | `/api/v1/products/` | `POST` |
| Listar productos (con filtros) | `/api/v1/products/?category=X&limit=N` | `GET` |

### Detalles Técnicos
- **Validación de rol**: Solo usuarios con rol `vendedor` pueden crear productos (Error 403 para compradores).
- **Validación de precio**: El precio debe ser mayor a 0 (COP). Pydantic rechaza valores negativos con Error 422.
- **Límite de imágenes**: Máximo 5 URLs de imagen por producto. Exceder este límite retorna Error 422.
- **Paginación**: El listado soporta `limit` (1–100) y `offset` para navegar resultados grandes.
- **Filtro por categoría**: Se puede filtrar por categoría con el query param `?category=comida`.

### Demostración Paso a Paso
1. **Postman / API**:
   - Autenticarse como vendedor (usar flujo OTP del Sprint 2).
   - Ejecutar `POST /api/v1/products/` con el body:
     ```json
     {
       "name": "Empanada Casera",
       "description": "Deliciosa empanada con relleno tradicional",
       "price": 2500,
       "category": "comida",
       "image_urls": ["https://ejemplo.com/empanada.jpg"]
     }
     ```
   - **Qué decir**: "El vendedor verificado puede publicar productos con validación automática de precio, categoría e imágenes."

2. **Frontend (Navegador)**:
   - Navegar a `/products/new` usando el menú de navegación.
   - Llenar el formulario con Drag & Drop de imágenes.
   - Verificar en la consola que la compresión reduce el peso antes de la subida.
   - **Qué decir**: "La interfaz comprime las imágenes en el dispositivo del usuario antes de subirlas, protegiendo contra archivos pesados."

### Pruebas Automatizadas Relacionadas
- `test_create_product_vendedor` — Verifica la creación exitosa (HTTP 201).
- `test_create_product_comprador_forbidden` — Verifica restricción por rol (HTTP 403).
- `test_create_product_invalid_price` — Valida precio > 0 (HTTP 422).
- `test_create_product_max_images` — Valida límite de 5 imágenes (HTTP 422).

---

## HU 3.2 — Edición de Productos e Inventario

**Como** vendedor,
**quiero** editar mis publicaciones y marcar un producto como "agotado",
**para** mantener mi catálogo actualizado sin eliminar publicaciones.

### Funciones Implementadas

| Función | Endpoint | Método |
| :--- | :--- | :--- |
| Actualizar producto | `/api/v1/products/{id}` | `PUT` |
| Alternar estado (Activo/Pausado) | `/api/v1/products/{id}/status` | `PATCH` |

### Detalles Técnicos
- **Propiedad**: Solo el dueño del producto puede editarlo. El servicio verifica `seller_id == current_user.id`.
- **Campos parciales**: `ProductUpdate` permite actualizar campos individuales (`name`, `description`, `price`, `category`, `image_urls`, `is_active`).
- **Toggle de estado**: El endpoint `PATCH /status` alterna `is_active` entre `true` y `false` sin necesidad de enviar un body.

### Demostración Paso a Paso
1. **Postman / API**:
   - Ejecutar `PUT /api/v1/products/{product_id}` con:
     ```json
     {
       "name": "Empanada Casera Edición Especial",
       "price": 3000
     }
     ```
   - Luego: `PATCH /api/v1/products/{product_id}/status` para marcar como inactivo.
   - **Qué decir**: "El vendedor puede actualizar campos individuales. El toggle permite pausar un producto sin eliminarlo."

2. **Frontend (Navegador)**:
   - Ir a `/profile` → Panel "Mis Productos".
   - Hacer clic en "Editar" para abrir el formulario de edición pre-cargado.
   - Usar el Toggle Switch para cambiar entre "Disponible" y "Agotado".
   - **Qué decir**: "El panel del vendedor ofrece control instantáneo sobre el inventario con un simple interruptor visual."

### Pruebas Automatizadas Relacionadas
- `test_update_product_success` — Verifica actualización exitosa (HTTP 200).
- `test_toggle_status_product` — Verifica el cambio de `is_active` (HTTP 200).

---

## HU 3.3 — Borrado Lógico y Pausa Temporal

**Como** vendedor,
**quiero** eliminar mis publicaciones de forma lógica (soft-delete),
**para** que dejen de aparecer en el catálogo pero se conserve el historial.

### Funciones Implementadas

| Función | Endpoint | Método |
| :--- | :--- | :--- |
| Borrado lógico (soft-delete) | `/api/v1/products/{id}` | `DELETE` |

### Detalles Técnicos
- **Soft-delete**: El producto no se borra de la base de datos. Se marca con `is_active = false` y deja de aparecer en `GET /products/`.
- **Retención de datos**: El historial se conserva para reportes y analíticas futuras.
- **Respuesta clara**: El endpoint retorna `{ "message": "Producto eliminado exitosamente" }`.

### Demostración Paso a Paso
1. **Postman / API**:
   - Ejecutar `DELETE /api/v1/products/{product_id}`.
   - Verificar con `GET /api/v1/products/` que el producto ya no aparece en la lista.
   - **Qué decir**: "Borrado lógico: el producto sale del catálogo pero retenemos el registro para auditoría y analíticas. Ley 1581 compliant."

2. **Frontend (Navegador)**:
   - En `/profile` → Panel "Mis Productos", presionar el botón rojo "Eliminar".
   - Confirmar la acción en el diálogo.
   - Verificar que el producto desaparece del catálogo (`/products`).
   - **Qué decir**: "La eliminación es irreversible desde la perspectiva del usuario, pero conservamos los datos internamente."

### Pruebas Automatizadas Relacionadas
- `test_delete_product` — Verifica soft-delete exitoso (HTTP 200) y mensaje de confirmación.

---

## Mejora Transversal — Menú de Navegación Global

**Como** usuario de la aplicación,
**quiero** un menú de navegación persistente,
**para** desplazarme fácilmente entre las secciones de VeraMarket.

### Funciones Implementadas
- **Desktop**: Barra superior fija con logo, enlaces y efecto `backdrop-blur` (glassmorphism).
- **Mobile**: Barra inferior (bottom-tab) estilo PWA nativa con iconos y labels.
- **Comportamiento adaptativo**:
  - Muestra "Publicar" solo para vendedores autenticados.
  - Muestra "Entrar" solo para usuarios no autenticados.
  - Muestra "Perfil" solo para usuarios autenticados.
- **Indicador activo**: La ruta actual se resalta con fondo `vera-50` y texto `vera-700`.

### Demostración Paso a Paso
1. **Desktop**: Abrir el navegador en resolución ≥ 768px.
   - Navegar entre Inicio → Catálogo → Mapa → Perfil.
   - **Qué decir**: "La barra superior persiste en todas las páginas con efecto de transparencia y blur."

2. **Mobile (DevTools)**: Abrir DevTools (F12) → Toggle Device Toolbar → iPhone.
   - La barra inferior aparece con iconos.
   - **Qué decir**: "En móvil, la navegación sigue el patrón de bottom-tabs estándar de apps nativas como Instagram y Twitter."

### Archivo Implementado
- `frontend/components/layout/NavigationMenu.tsx` — Componente integrado en `layout.tsx`.

---

## Validación Completa con Postman (Sprints 1 al 3)

Para una demostración interactiva de toda la API, se creó una colección y entorno de Postman corregidos a fondo:

1. **Archivos a Importar** (ubicados en `docs/postman/`):
   - `VeraMarket_Sprints_1_2_3.postman_collection.json`
   - `VeraMarket_Sprints_1_2_3.postman_environment.json`

2. **Configuración Inicial**:
   - Selecciona el ambiente **"VeraMarket - Sprints 1 a 3 Local"** en la esquina superior derecha de tu cliente Postman.
   - Variables pre-cargadas: `base_url`, `test_email`, `otp_code`, `sinapsis_code` (= `SINAPSIS-TEST-001`).
   - Variables dinámicas (se llenan con Scripts de Test): `token`, `user_id`, `product_id`.

3. **Flujo de Demostración Paso a Paso**:
   - **Carpeta 1 - Auth** (bajo `/api/v1/auth/`):
     - `1.1 Solicitar OTP` → Envía el código al correo.
     - `1.2 Verificar OTP` → Recibe JWT y lo guarda como `{{token}}`.
     - `1.3 Completar Perfil` → Registra nombre e ID institucional. Guarda `{{user_id}}`.
     - `1.4 Actualizar Perfil` → Modifica nombre o teléfono (`PUT /api/v1/auth/profile`).
     - `1.5 Solicitar Rol Vendedor (Sinapsis)` → Usa campo `sinapsis_code` con valor `{{sinapsis_code}}` (`POST /api/v1/auth/vendor/request`). **Vital para Sprint 3.**
   - **Carpeta 2 - Users & Privacy** (bajo `/api/v1/users/`):
     - `2.1 Mi Perfil` → `GET /me` con datos privados completos.
     - `2.2 Perfil Público` → `GET /{{user_id}}` con enmascaramiento según privacidad.
     - `2.3 Obtener Config. Privacidad` → `GET /me/privacy`.
     - `2.4 Actualizar Config. Privacidad` → `PUT /me/privacy` con body `{show_email, show_phone}`.
   - **Carpeta 3 - Catálogo P2P** (bajo `/api/v1/products/`):
     - `3.1 Crear Producto` → `POST /` con body JSON. Guarda `{{product_id}}`.
     - `3.2 Listar Productos` → `GET /?limit=20&offset=0`.
     - `3.3 Listar por Categoría` → `GET /?category=tecnologia`.
     - `3.4 Obtener por ID` → `GET /{{product_id}}`.
     - `3.5 Editar Producto` → `PUT /{{product_id}}` con campos parciales.
     - `3.6 Alternar Estado` → `PATCH /{{product_id}}/status` (sin body).
     - `3.7 Eliminar` → `DELETE /{{product_id}}` (soft-delete).
   - **Carpeta 4 - Push** (bajo `/api/v1/push/`):
     - `4.1 Suscribir Push` → `POST /subscribe` con `{endpoint, keys}`.

> [!TIP]
> Cada petición tiene un **Test Script** que valida el status HTTP y propaga automáticamente las variables (`token`, `user_id`, `product_id`). Puedes ejecutar la demo completa con "1 clic por petición" sin copiar/pegar.

---

## Ejecución de Pruebas (Comandos)

```bash
# Backend: Ejecutar suite completa de pruebas
cd backend
pytest app/tests/test_products.py -v

# Frontend: Verificar compilación y lint
cd frontend
npm run lint
npm run build
```

### Resultados Esperados
- **Backend**: 8 pruebas pasan en `test_products.py` (creación, edición, borrado, toggle, validaciones).
- **Frontend**: Build exitoso sin errores de TypeScript ni warnings de ESLint.

---

## Conclusión y Próximos Pasos

### Entregado en Sprint 3
- ✅ Publicación de productos (CRUD completo con validaciones)
- ✅ Gestión de inventario (Agotado / Disponible vía toggle)
- ✅ Borrado lógico (Soft-Delete con retención de historial)
- ✅ Menú de navegación global responsive (Desktop + Mobile)
- ✅ Colección Postman actualizada (16 endpoints con test scripts)

### Pendiente para Sprint 4+
- 🔜 Búsqueda avanzada y filtros por geolocalización (PostGIS)
- 🔜 Chat P2P entre comprador y vendedor
- 🔜 Sistema de calificaciones y reseñas
- 🔜 Pasarela de pagos integrada
