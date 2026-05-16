# Guia: Cómo Ejecutar Test Coverage, Guardar Resultados e Interpretar Archivos

## 1. Comandos para ejecutar la cobertura

```bash
# Desde la carpeta backend/
cd backend

# Opcion A: Solo terminal (texto plano)
python -m pytest --cov=app.services app/tests/ --cov-report=term-missing

# Opcion B: Reporte HTML interactivo (recomendado para exposicion)
python -m pytest --cov=app.services app/tests/ \
  --cov-report=term-missing \
  --cov-report=html:coverage_html \
  --cov-report=json:coverage.json \
  --cov-report=xml:coverage.xml
```

### Equivalente en Windows PowerShell (una sola línea):
```powershell
cd backend; python -m pytest --cov=app.services app/tests/ --cov-report=term-missing --cov-report=html:coverage_html --cov-report=json:coverage.json --cov-report=xml:coverage.xml
```

---

## 2. Archivos generados y su ubicacion

| Archivo / Directorio           | Ubicacion                          | Descripcion                                                        |
|-------------------------------|------------------------------------|--------------------------------------------------------------------|
| `coverage.json`               | `backend/coverage.json`            | JSON estructurado con cobertura por archivo, linea a linea         |
| `coverage.xml`                | `backend/coverage.xml`             | Formato Cobertura (compatible con CI/CD: GitHub Actions, Jenkins)  |
| `coverage_html/`              | `backend/coverage_html/index.html` | Reporte visual interactivo; abrir en el navegador                  |
| `.coverage`                   | `backend/.coverage`                | Base de datos binaria de pytest-cov (no abrir manualmente)         |
| `coverage_output.txt`         | `backend/coverage_output.txt`      | Salida de texto guardada manualmente (redireccion de consola)      |

---

## 3. Como ver los resultados

### Terminal (durante la ejecucion):
```
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
app\services\analytics_service.py       33      0   100%
app\services\coupon_service.py          65      3    95%   72-78, 169
app\services\negotiation_service.py    200     56    72%   97, 140...
-------------------------------------------------------------------
TOTAL                                  965    257    73%
```

### HTML interactivo:
```bash
# Abrir en navegador despues de ejecutar
start backend/coverage_html/index.html   # Windows
```

### JSON (para scripts):
```python
import json
with open("coverage.json") as f:
    data = json.load(f)

# Estructura del JSON:
# data["totals"]["percent_covered"]  → cobertura global
# data["files"]["app/services/X.py"]["summary"]["percent_covered"]
```

---

## 4. Resultados actuales del proyecto (Sprint 5)

| Servicio                    | Stmts | Miss | Cover |
|-----------------------------|-------|------|-------|
| analytics_service.py        | 33    | 0    | 100%  |
| rating_service.py           | 42    | 0    | 100%  |
| map_service.py              | 5     | 0    | 100%  |
| sinapsis_service.py         | 52    | 1    | 98%   |
| push_service.py             | 11    | 1    | 91%   |
| typesense_service.py        | 144   | 22   | 85%   |
| location_service.py         | 39    | 7    | 82%   |
| quota_service.py            | 43    | 9    | 79%   |
| negotiation_service.py      | 200   | 56   | 72%   |
| coupon_service.py           | 65    | 3    | 95%   |
| report_service.py           | 65    | 3    | 95%   |
| product_service.py          | 65    | 38   | 42%   |
| auth_service.py             | 39    | 19   | 51%   |
| email_service.py            | 63    | 31   | 51%   |
| nlu_service.py              | 99    | 67   | 32%   |
| **TOTAL**                   | **965** | **257** | **73%** |

> Umbral objetivo: 70% — **SUPERADO**

---

## 5. Interpretar `coverage.json` (estructura)

```json
{
  "meta": {
    "version": "7.x",
    "branch_coverage": false,
    "show_contexts": false
  },
  "files": {
    "app/services/analytics_service.py": {
      "executed_lines": [1,2,...],
      "missing_lines": [],
      "summary": {
        "num_statements": 33,
        "missing_lines": 0,
        "percent_covered": 100.0
      }
    }
  },
  "totals": {
    "num_statements": 965,
    "missing_lines": 257,
    "percent_covered": 73.37
  }
}
```

---

## 6. Deuda tecnica identificada (lineas no cubiertas por servicio)

| Servicio           | Lineas sin cubrir | Prioridad de mejora |
|--------------------|-------------------|---------------------|
| nlu_service.py     | 67 (lineas 35-216) | Media — requiere mock de Gemini API |
| product_service.py | 38 (lineas 23-174) | Media — tests de integracion CRUD   |
| email_service.py   | 31 (lineas 86-205) | Baja — SMTP externo, mock complejo  |
| auth_service.py    | 19 (lineas 73-127) | Baja — JWT/OTP flujo de integracion |
