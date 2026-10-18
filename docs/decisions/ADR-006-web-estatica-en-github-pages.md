# ADR-006: Web estática en GitHub Pages, construida por GitHub Actions

## Status
Accepted

## Date
2026-10-18

## Context
La web (catálogo, formatos, estadísticas, ejemplos) debe verse en GitHub sin servidor. Pero el Taller y el renderizado necesitan la API.

## Decision
`servidor/tools/pages.py` construye una versión estática en `_site/` (rutas bajo `/guia`, sin llamadas a `/v1`, con la lista de diseños y el catálogo como JSON) y `.github/workflows/pages.yml` la publica. Lo que necesita la API avisa que corre en local («Demo estática»).

## Alternatives Considered

### Subir `docs/` con los archivos ya construidos
- Rejected: mezcla artefactos con código y se desactualiza.

### Alojar la API
- Rejected: expone un servidor que escribe archivos; el proyecto es local por diseño.

## Consequences
- Hay que activar Pages con fuente «GitHub Actions» en la configuración del repositorio.
- El ejemplo en video y las capturas salen de la web real (`servidor/tools/capturas_web.py`), enmarcadas con `servidor/tools/marco.py`.
