# Plan operativo: Director Creativo local (integrado a myStyle)

Fuente: artifact «Plan operativo: Director Creativo local» (https://claude.ai/artifact/FKQv83Ts9jUj13i7JsKZJs), revisado 2026-10-18.
Objetivo: **gastar menos tokens de Claude**. Un modelo local (visión + texto + código, 4 bits, 6 GB VRAM, por turnos) decide y usa la API; el motor valida;
Claude solo revisa lotes filtrados. Regla de escalado: a Claude solo si el motor rechaza 3 veces seguidas, o el usuario marca que no quedó y el local falla 2 veces.

## Lo que el artifact da por faltante y YA existe aquí (actualizar el artifact)
- `create_pptx`, `create_video` → hechos (`render_pptx.py`, `render_video.py`), más Word y Excel. Fase 1 puede probar los 4 formatos, no solo PDF.
- Servidor MCP → hecho (`servidor/mcp_server.py`, 7 herramientas). Falta renombrar/añadir las que pide el plan (ver D1).
- Respuestas a sus preguntas abiertas: API en Python; plantillas propias en HTML con campos `{{…}}` (sin herramienta externa). Frontend brutalista: hecho, no se retira.

## Estado (2026-10-18)
D1 herramientas ✔ · D2 biblioteca ✔ · D3 correcciones e ids ✔ · D4 Markdown ✔ · D5 protocolo de estilos ✔ (probado con prompt-master) · D6 AGENTS.md y config ✔ · D7 presets de animación ✔ (GSAP; anime.js no se instaló) · D8 evaluación ✔ · D9 dataset/scripts ✔ (entrenamiento: tuyo). Fase 0 y 1: el modelo local ya genera PDF y PPTX de punta a punta con `director.py` (qwen2.5-coder:7b); probar qwen2.5:3b y 1.5b es tuyo.

## Línea base medida (qwen2.5-coder:7b, 20 casos fijos, `servidor/evaluacion/linea_base.json`)
Sin error de validación **95 %** (criterio del plan: ≥ 70 %) · herramienta correcta 80 % · buscó en la biblioteca antes de crear 90 % · bloques esperados en el contrato 60 % · calidad del motor 82 % · escalados a Claude 2 de 20 · ~156 000 tokens locales de entrada en toda la corrida (gratis).
Lo que subió la segmentación de 35–40 % a 60 %: prompt corto con la hoja de Markdown, aceptar `con_avisos` como final (el modelo rompía el resultado al «corregir» con ids inventados), alias de formato (`pdf` → `pdf-a4`) y mensaje claro si el `job` no es un id. Un prompt más largo **empeoró** (6 escalados): el contexto por defecto de Ollama es 4096 tokens.

## Reparto (sigue el esquema Haiku / Sonnet / Opus de PROMPTS_SIGUIENTES.md; no se ejecuta hasta que el usuario lo apruebe)
| Id | Tarea | Modelo | Dónde |
|---|---|---|---|
| D1 | Herramientas del plan: `search_library`, `audit` (PDF externo, ya listado en PENDIENTES §3.1), `save_style`, `render`; esquemas JSON estilo OpenAI function-calling en `GET /v1/tools` además de MCP | Sonnet | `api.py`, `mcp_server.py` |
| D2 | Biblioteca versionada en archivos (estilos, plantillas, componentes, animaciones) con tags/descripción/origen/licencia + `SKILL.md` por componente (≤1 pantalla) + búsqueda por similitud | Sonnet (script de carga: Haiku) | `servidor/biblioteca/` |
| D3 | Registro de correcciones JSONL (`antes`/`despues`, sección con nombre p. ej. `portada.titulo`, motivo) y su uso como ejemplos; ids estables por bloque (PENDIENTES §3.9) | Sonnet | `api.py` (`/patch`) |
| D4 | Entrada Markdown con cabecera (objetivo, formato, estilo) y imágenes relativas/zip: `#`→título, `##`→sección, listas, tablas, imágenes→figura | Sonnet | nuevo `engine/markdown.py` |
| D5 | Protocolo de estilos nuevos (extraer paleta/tipos/espaciado/bordes/sombras, buscar parecido, nombrar, versionar, WCAG 4,5:1, validar, guardar con ejemplo). Se fusiona con O1 (estilo desde el PDF) | Opus | `crear_diseno.py`, `LEEME.md` |
| D6 | `AGENTS.md` + config del «cerebro» (endpoint y nombre del modelo en un archivo) + modo solo localhost/auth | Haiku | raíz |
| D7 | Animaciones como presets (5 de anime.js; GSAP ya local) invocados como dependencia con licencia anotada; video las captura | Sonnet | `render_video.py` |
| D8 | Conjunto fijo de 20 entradas, evaluación automática (herramienta correcta, segmentación, reutilización, calidad visual) y lote filtrado para Claude | Opus | `servidor/evaluacion/` |
| D9 | Entrenamiento LoRA con Soup (dataset JSONL ≥100 ejemplos, línea base, QLoRA 4 bits) | Opus (solo preparar scripts) | **requiere GPU del usuario** |

Orden sugerido: D6 → D1 → D3 → D2 → D4 → D5/O1 → D7 → D8 → D9. Sinergia con la tanda anterior: O2 (medición de tokens) es la métrica base del «objetivo real».

## Solo el usuario puede hacerlo (Fase 0 y 4, en su portátil)
- [ ] Instalar Ollama o LM Studio; bajar Qwen2-VL-2B (o VL más reciente) y Qwen2.5-Coder 1.5B/3B y Qwen2.5 Instruct 1.5B/3B en 4 bits; medir VRAM y tiempo.
- [ ] Conectar OpenCode (o Codex/Claude Code) al servidor MCP; elegir orquestador. Anotar versiones de Python, Ollama y Soup.
- [ ] Probar 10 casos reales (criterio: ≥7 sin error de validación); luego 2–3 tamaños y quedarse con el menor que pase.
- [ ] Entrenamiento nocturno con Soup (o GPU alquilada) y anotar semanalmente cuántas veces se recurrió a Claude.
- [ ] Confirmar licencias «a verificar» (anime.js, Motion Canvas, Lottie…); GSAP/Remotion son gratis para uso propio.
- [ ] Decidir si se acepta Markdown como entrada (pregunta abierta ya en PENDIENTES §4).

## Comandos que ejecutas tú (PowerShell, en tu portátil)
Los nombres de modelo son candidatos; confirma que existen en https://ollama.com/library antes de bajarlos.
```powershell
winget install Ollama.Ollama                 # instalar Ollama
ollama --version; python --version           # anota las versiones (Fase 0)
ollama pull qwen2.5:3b                       # texto: decide herramientas
ollama pull qwen2.5-coder:3b                 # código (prueba también :1.5b)
ollama pull qwen2.5vl:3b                     # visión pequeña (alternativa a Qwen2-VL-2B; verifica el nombre)
ollama run qwen2.5:3b "responde solo JSON: {\"ok\":true}"   # prueba rápida
nvidia-smi                                   # VRAM usada mientras responde
pip install soup                             # solo en Fase 4; fija la versión (v0.75 rechaza claves desconocidas)
```
```powershell
# conectar mi API a un agente local (MCP): ajusta la ruta
claude mcp add mystyle -e MYSTYLE_URL=http://127.0.0.1:8765 -- python D:\feibert\api\guia\servidor\mcp_server.py
```

## Qué puedes hacer tú para ahorrar tokens (yo puedo hacerlo, pero cuesta)
| Tarea | Quién conviene | Cómo |
|---|---|---|
| Bajar y probar modelos, medir VRAM/tiempo | **Tú** (cero tokens) | comandos de arriba; pega solo el resultado resumido |
| Los 10 casos de prueba de la Fase 1 | **Tú** ejecutas, yo reviso solo los fallos | guarda entrada → herramientas → resultado en una hoja |
| Correr `python -m unittest` y `regresion.py` tras cada cambio | **Tú** | basta con pegarme solo las líneas que fallan |
| Reunir 20 entradas reales para el conjunto fijo (D8) | **Tú** (criterio humano) | PDF/imágenes/Markdown que usarías de verdad |
| Revisión visual de PDF/PPTX/video | **Tú** mirando; yo solo si algo está mal | evita que yo renderice y lea capturas (caro) |
| Verificar licencias «a verificar» | **Tú** (páginas oficiales) | anótalas en la biblioteca |
| Docker (construir imagen), instalar fuentes `.ttf`, claves API | **Tú** (permisos del sistema) | ver PENDIENTES §4 |
| Escribir scripts repetitivos (cargar biblioteca, tags) | **Modelo local** (D2), no Claude | lo bajamos de Opus/Sonnet a Qwen |
| Reparto de tareas por modelo | Haiku: texto, comandos, docs · Sonnet: código estándar · Opus: diseño del método, evaluación, estilos | ya en PROMPTS_SIGUIENTES.md |
