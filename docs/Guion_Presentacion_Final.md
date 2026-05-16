# Guion y Estructura: Sustentación Final VeraMarket
**Duración Total:** 30 Minutos
**Enfoque:** Resultados, Métricas y Aprendizajes.

---

## 1. Contexto y Problema (Duración: 5 Minutos)

**Objetivo:** Establecer por qué existe VeraMarket y para quién se construyó.

*   **Slide 1: El Título**
    *   *Visual:* Logo de VeraMarket y los nombres del equipo.
    *   *Discurso:* "Buenos días. Somos el equipo detrás de VeraMarket, la vitrina digital de economía universitaria hiperlocal."
*   **Slide 2: El "Valle de la Muerte" Universitario**
    *   *Visual:* Gráfico simple o íconos que muestren el ecosistema (Centro de Innovación/Sinapsis -> Emprendedor -> ? -> Estudiante).
    *   *Discurso:* "Durante nuestro análisis inicial, detectamos un problema claro: los emprendimientos formales nacidos dentro del campus, a pesar del apoyo de Sinapsis, enfrentan un 'valle de la muerte' al momento de vender. Carecen de un canal directo y exclusivo, dependiendo del caos de los grupos de WhatsApp o compitiendo en desventaja en plataformas genéricas como Facebook Marketplace o Instagram."
*   **Slide 3: La Solución (La Promesa de Valor)**
    *   *Visual:* 3 pilares: Exclusividad (Correo institucional), Proximidad (Mapa), Inteligencia (IA).
    *   *Discurso:* "Nuestra respuesta fue construir VeraMarket: una plataforma construida específicamente para el ecosistema cerrado de la universidad, garantizando transacciones seguras mediante verificación institucional, reduciendo la fricción logística mediante geolocalización de campus, y democratizando el descubrimiento a través de búsqueda asistida por IA."

---

## 2. Demo del Sistema (Duración: 10 Minutos)

**Objetivo:** Mostrar que el sistema resuelve el problema propuesto a través de un "Happy Path" (Flujo Ideal). *Evitar mostrar código en esta fase.*

*   **Slide 4 / Pantalla Compartida: El Flujo del Usuario**
    *   *Acción:* **Paso 1 (Autenticación):** Mostrar el inicio de sesión *passwordless*. Explicar brevemente que solo acepta dominios de la universidad (garantía de seguridad).
    *   *Acción:* **Paso 2 (Descubrimiento):** Usar la barra de búsqueda con IA. Escribir un modismo (ej. *"busco algo pa picar barato"*). 
    *   *Discurso:* "Aquí entra nuestra integración con Gemini. El sistema no busca literalmente 'algo pa picar', sino que extrae la intención y filtra por la categoría correcta."
    *   *Acción:* **Paso 3 (Contacto Logístico):** Mostrar el mapa interactivo y seleccionar un vendedor cercano.
    *   *Acción:* **Paso 4 (Negociación y Cierre):** Abrir el chat en tiempo real. Mostrar cómo se acuerda la cantidad y se selecciona el método de pago ("Efectivo" o "Transferencia") para bloquear la transacción.
    *   *Acción:* **Paso 5 (Métricas):** Cambiar rápidamente al rol de Vendedor y mostrar cómo esa venta se refleja de inmediato en el Dashboard Financiero.

---

## 3. Resultados y Métricas (Duración: 10 Minutos) *[Punto Crítico]*

**Objetivo:** Demostrar medición, calidad técnica y comprensión del desfase entre lo planeado y lo ejecutado.

*   **Slide 5: El Proceso (Cómo lo construimos)**
    *   *Visual:* Línea de tiempo (Sprints del 1 al 5). Mostrar íconos de HUs aprobadas creciendo.
    *   *Discurso:* "Este fue nuestro ciclo de desarrollo iterativo. Empezamos con una arquitectura base, y de manera ágil fuimos inyectando historias de usuario. Un hito relevante fue en el Sprint 3, donde descartamos un motor estático y decidimos pivotar hacia una Búsqueda Híbrida (IA + Typesense) porque nos dimos cuenta de que los estudiantes no buscaban con términos técnicos exactos."
*   **Slide 6: Alcance Funcional (Qué se entregó)**
    *   *Visual:* Tabla comparativa (Requisitos Planeados vs Entregados).
    *   *Métrica:* **11 de 12 (91%) Requisitos Funcionales Completados.**
    *   *Discurso:* "De nuestro *Project Charter*, completamos casi la totalidad del core de negocio: Autenticación, Catálogo, Geolocalización, Chat P2P y Dashboard Analítico."
*   **Slide 7: Lo que NO se logró (Features Pendientes)**
    *   *Visual:* Icono de Pasarela de Pagos tachado / "En progreso".
    *   *Discurso:* "La característica que no logramos integrar fue la conexión directa y automática a APIs de billeteras digitales (Nequi/Daviplata) por restricciones de infraestructura y licencias Fintech. El siguiente paso recomendado (Fase 2) es integrar un Agregador de Pagos como Wompi o ePayco."
*   **Slide 8: Calidad Técnica y Testing (Transparencia)**
    *   *Visual:* Gráficos técnicos (Uptime, Latencia, Testing).
    *   *Métricas:* 
        *   **Latencia (Lograda):** Búsquedas resueltas en < 100ms (gracias a Typesense).
        *   **Cobertura de Pruebas (Deuda Técnica):** < 5% de Test Coverage.
    *   *Discurso:* "Técnicamente, el sistema es extremadamente veloz y resiliente bajo estrés. Logramos los tiempos de carga requeridos. Sin embargo, midiendo nuestra calidad interna, nuestra cobertura de pruebas automatizadas es inferior al 5%. Priorizamos la entrega de valor funcional (UI/UX) frente a la madurez de testing. Esta es nuestra mayor deuda técnica y el primer paso arquitectónico para la siguiente fase."

---

## 4. Lecciones Aprendidas (Duración: 5 Minutos)

**Objetivo:** Reflexión sobre la ingeniería de software y el impacto del negocio.

*   **Slide 9: Retos Arquitectónicos (IA y Fallbacks)**
    *   *Discurso:* "Aprendimos que depender de una IA externa (Gemini) es peligroso por la latencia y las cuotas. Diseñar un patrón de 'Fallback' automático hacia un motor tradicional fue la mejor decisión de ingeniería que tomamos para no romper la experiencia de usuario."
*   **Slide 10: Privacidad y Normativa Legal**
    *   *Discurso:* "La ingeniería no ocurre en el vacío. La Ley 1581 (Habeas Data) moldeó nuestra base de datos. Aprendimos a diseñar arquitecturas 'Privacy-First', implementando Row-Level Security y aislando datos personales por defecto."
*   **Slide 11: Reflexión de Cierre**
    *   *Discurso:* "Para concluir: Sí, logramos resolver el problema de descubrimiento y visibilidad de los emprendedores en el campus. Pero lo más valioso fue entender que el código es solo una herramienta; el éxito real radicó en entender cómo se comunican y negocian los estudiantes en la vida real. Muchas gracias."

---

### Tips Rápidos para el Día de la Presentación:
1. **Ensayen la Demo:** La demostración en vivo siempre tiene riesgo de fallar. Tengan un video pregrabado del "Happy Path" listo como plan B.
2. **Distribución del Tiempo:** Usen un cronómetro. Si la demo se alarga, recorten el Contexto, pero **NUNCA recorten la sección de Resultados y Métricas**, ya que es lo más evaluado.
3. **Seguridad en las Deudas Técnicas:** No teman decir "no logramos esto" o "nuestras pruebas fallaron aquí". Demostrar que saben exactamente qué falta y por qué, daña menos la nota que intentar ocultarlo.
