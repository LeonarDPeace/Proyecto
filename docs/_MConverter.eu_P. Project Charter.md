---
title: |
  **Project Charter (PC) -- VeraMarket**

  Eduard Criollo Yule (Cod: 2220335)
---

Juan Sebastián Delgado (Cod: 2216223)

Felipe Charria Caicedo (Cod: 2216033)

Valentina Velastegui López (Cod: 2226725)

# **PROJECT CHARTER: VERAMARKET MVP**  {#project-charter-veramarket-mvp}

**Ubicación:** Ubicación: Cali, Valle del Cauca, Colombia. Sede de Operaciones: Esquema híbrido (Home Office del equipo fundador y espacio de Coworking en el Centro de Innovación Sinapsis UAO).

**Presupuesto Fase Piloto:** \$0 COP (Arquitectura MVP basada en Capas Gratuitas y Open Source).

**Presupuesto Fase de Escalamiento:** Sujeto a validación del piloto, se proyecta inversión para migración a servicios Cloud pagos (AWS/Render) para soportar la expansión.\"

1.  **Propósito y Justificación del Proyecto:**

Desarrollar una PWA que potencie y digitalice las ventas de los emprendimientos avalados por el Centro de Innovación Sinapsis

1.  **Criterios de Éxito del Piloto VeraMarket:**

<!-- -->

1.  **Criterio Técnico (Disponibilidad):** La plataforma PWA debe mantener un *Uptime* (tiempo de actividad) mínimo del **99.0%** durante las 4 semanas del piloto.

2.  **Criterio de Adopción (Tracción):** Lograr la adquisición de **500 usuarios registrados** y validados en el primer mes de operación.

3.  **Criterio de Negocio (Volumen P2P):** Facilitar y registrar un promedio de **200 transacciones completadas por día** al finalizar el piloto.

4.  **Criterio Financiero (GMV):** Alcanzar un volumen de mercancía bruta (Gross Merchandise Value) proyectado de **\$15.000.000 COP/mes**, calculado a partir de los precios de lista de las transacciones marcadas como \"Completadas\".

5.  **Criterio de Calidad Comunitaria:** El **90%** de las calificaciones post-transacción deben ser iguales o superiores a 4.0 estrellas.

## **2. Objetivos del Proyecto (SMART):** {#objetivos-del-proyecto-smart}

- **Negocio:** Alcanzar 100 usuarios activos (estudiantes) y 50 transacciones registradas al finalizar la semana 11. la centralización y seguridad de la información en tiempo real.

- **Técnico:** Desplegar una PWA instalable con latencia de respuesta minima (tiempo de carga inicial \< 3 segundos) y un motor de búsqueda semántica local respaldado por una API OpenAI gpt 4o-mini en la semana 9.

## **3. Alcance del MVP (In/Out):** {#alcance-del-mvp-inout}

- *In Scope:* Autenticación con correo universitario, PWA instalable, catálogo de productos/servicios, chat básico de negociación P2P, motor de recomendación local.

- *Out of Scope:* Pasarelas de pago (Nequi/Daviplata integradas por API), entregas a domicilio fuera del campus, integraciones con redes sociales corporativas. Pagos se acordarán en persona (Cash/QR directo). Validación de perfiles de vendedores contra la base de datos oficial de graduados/activos de Sinapsis.

## **4. Cronograma de Hitos (11 Semanas - Sprints de 2 semanas):** {#cronograma-de-hitos-11-semanas---sprints-de-2-semanas}

- **S1-S2:** Configuración de Arquitectura, CI/CD, Base de datos y Auth.

- **S3-S4:** Módulo de Publicación de Productos e interfaz PWA.

- **S5-S6:** Optimización de API e integración de IA.

- **S7-S8:** Integración de IA (Llama local) para categorización y búsqueda semántica.

- **S9-S10:** QA, Pruebas de usabilidad en campus y corrección de bugs.

- **S11:** Despliegue en producción y Presentación Final.

## **5. Riesgos Principales y Mitigación:** {#riesgos-principales-y-mitigación}

- *Riesgo:* Complejidad de mantener la IA local en servidores gratuitos (latencia).

  - *Mitigación (Arquitectónica):* Implementar el **Patrón Adapter**. Si el modelo Llama local falla por recursos, el sistema hace un *fallback* automático a un motor de búsqueda de texto tradicional o una API Mockup.

- *Riesgo:* Privacidad de datos (Ley 1581 de 2012 de Habeas Data).

  - *Mitigación:* Cifrado de base de datos, mínimo almacenamiento de PII (Personally Identifiable Information). No se pedirán datos financieros.
