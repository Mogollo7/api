# Crear recurso (patrón, fondo o icono)

Los recursos son imágenes generadas por código.

## Tipos
`puntos`, `rejilla`, `lineas`, `ondas`, `degradado`, `ruido`, `marco`, `icono`.

## Pasos
1. Crea el recurso:
   `create_resource {"tipo":"puntos","id":"fondo-azul","color":"#1D4ED8","color2":"#FFFFFF"}`
   - `id` en minúsculas.
   - Devuelve `src` (p. ej. `recursos/fondo-azul.png`).
2. Icono: `create_resource {"tipo":"icono","id":"hoja","icono":"leaf","color":"#15803D"}`.
   - Nombres de iconos Lucide (licencia ISC). Búscalos: `python servidor/recursos.py iconos <texto>`.
3. Úsalo en un bloque `image` con ese `src`, o en Markdown: `![pie](recursos/fondo-azul.png)`.
4. CLI equivalente: `python servidor/recursos.py crear <tipo> <id> --color "#…" --color2 "#…"`.
