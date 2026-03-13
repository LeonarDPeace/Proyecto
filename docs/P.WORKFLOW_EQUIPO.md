# VeraMarket — Workflow del Equipo

Este documento define las prácticas de desarrollo, control de versiones (Git) y revisión de código para el equipo 🚀

## 1. Estrategia de Ramas (Git Branching)

Utilizamos un flujo simplificado basado en **Git Flow**:

*   **`main` / `master`**: Código en producción. Siempre estable.
*   **`develop`**: Rama base de integración y pruebas (Staging). Aquí se unen todas las features.
*   **Ramas de Feature (`feat/...`)**:
    *   Formato: `feat/sprint-[X]-[nombre-funcionalidad]`
    *   Ejemplos: `feat/sprint-1-auth`, `feat/sprint-1-products`, `feat/sprint-2-pwa`
*   **Ramas de Fix (`fix/...`)**:
    *   Formato: `fix/sprint-[X]-[nombre-bug]`
    *   Ejemplo: `fix/sprint-1-otp-validation`

### Flujo de Trabajo
1. Sincronizar local: `git checkout develop && git pull origin develop`
2. Crear nueva rama: `git checkout -b feat/sprint-1-nueva-funcion`
3. Desarrollar y hacer commits atómicos (ver sección 2).
4. Subir rama: `git push origin feat/sprint-1-nueva-funcion`
5. Crear **Pull Request (PR)** hacia `develop`.

---

## 2. Conventional Commits

Todo el historial de Git debe seguir la convención de [Conventional Commits](https://www.conventionalcommits.org/).

**Estructura:**
`tipo(contexto opcional): descripción corta en imperativo`

**Tipos permitidos:**
*   `feat`: Nueva funcionalidad
*   `fix`: Corrección de un bug
*   `refactor`: Cambio de código que no corrige un bug ni añade una función (ej. limpieza)
*   `docs`: Cambios solo en la documentación
*   `style`: Cambios que no afectan el significado del código (espacios, formateo, punto y coma)
*   `test`: Añadir tests faltantes o corregir existentes
*   `chore`: Cambios en la ejecución del build, herramientas auxiliares o dependencias (ej. actualizar npm)

**Ejemplos Reales:**
*   `feat(auth): add vendor role request endpoint`
*   `fix(db): remove auto-commit from database dependency`
*   `docs: update architecture diagram with correct stack`
*   `test(products): add unit tests for product creation`

---

## 3. Pull Requests y Code Review

Antes de fusionar (merge) una rama a `develop`, se deben cumplir los siguientes criterios:

1.  **Checklist de PR Completo**: Llenar el [PULL_REQUEST_TEMPLATE](../.github/PULL_REQUEST_TEMPLATE.md).
2.  **Tests Pasando**: El CI de GitHub Actions (Linting + Pytest + Frontend Build) debe tener éxito "✅".
3.  **Aprobación**: Al menos un (1) miembro del equipo debe aprobar los cambios.
4.  No haber dejado datos sensibles, contraseñas o un `.env` commiteado.

*Se recomienda hacer Squash and Merge para mantener el historial de `develop` limpio, con un solo commit representativo por feature.*
