# Hacer video (MP4)

Tarda minutos. La herramienta espera hasta 10 min y devuelve `job` (12 hex) y la URL del MP4; si se acaba el tiempo, sigue con `job_status {"job":"…"}`.

## Dos modos
**A · Documento → video.** El motor elige los momentos fuertes de tu Markdown. `#` = parte (abre con un divisor), `##` = escena. **Tope real: 3 momentos por parte, 1 por sección** (bloques `:::big`, `:::kpi`, gráfico, cita, lista, párrafo); cada escena dura 2 compases. Si sobran, el aviso dice «momentos no entraron»: pon más partes (`#`) o sube `duracion`.
**B · Escenas explícitas `:::motion` (piezas tipo Brag).** Tú decides cada escena y su duración. Una línea = una escena: `tipo | texto | [extra] | segundos`.

| tipo | qué hace | ejemplo |
|---|---|---|
| `palabra` | frase gigante con zoom y desenfoque | `palabra \| Un solo motor \| 2` |
| `nombres` | nombres que entran con zoom/blur (con `extra` = centro: un servidor al medio) | `nombres \| Claude Code · Codex · OpenCode \| 4 \| MOTOR` |
| `cartas` | cartas que aparecen y se iluminan una a una | `cartas \| create_pdf() · audit() \| 4` |
| `flujo` | pasos con flechas que se dibujan y se encienden | `flujo \| Piensa → Elige → La API trabaja \| 5` |
| `contador` | cifra que sube de 0 | `contador \| 94 % \| menos tokens \| 3` |
| `estados` | rojo → verde → guardado (hasta 4) | `estados \| Error → Corregido → Guardado \| 4` |
| `final` | cierre en dos líneas | `final \| Build once. \| Connect any AI. \| 4` |

Los elementos de una lista se separan con ` · ` o ` → `. Cada escena: 1,5–12 s. Suma ≤ 120 s (`duracion: 120` en la cabecera).

## Pasos
1. Cabecera: `formato: video`, `estilo:`, `duracion:` (s, máx. 120), `ritmo:` (bpm, afecta a los modos A), `entrada: slide|fade-up|wipe-reveal`.
2. Escribe el Markdown (modo A o `:::motion`; se pueden usar los dos en documentos distintos, no mezclados).
3. `create_video {"markdown":"…"}` (o `"vertical":true` para 9:16). Un video de 100 s tarda ~5 min.
4. Mira un cuadro: `ffmpeg -ss 5 -i video.mp4 -frames:v 1 cuadro.png`.

## Reglas
- No vuelvas a llamar `create_video` mientras haya un job en curso: usa `job_status`.
- Logos de marcas: no se descargan; usa el nombre en tipografía (`nombres`) o un icono (`create_resource` tipo `icono`).
- Un estilo oscuro (p. ej. `arcano`) invierte los roles: la «tinta» es clara. Los colores de las escenas alternan por rol del estilo.
- Sin dato, «dato pendiente». Con `errores`, corrige con `patch` (ver `corregir-y-revisar.md`).
