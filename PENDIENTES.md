# myStyle · estado, pendientes y bitácora de instrucciones

Actualizado: 2026-10-18. Fuente de verdad para retomar el trabajo. Las instrucciones nuevas del usuario se anotan al final, en la **Bitácora**,
antes de ejecutarlas. Especificación de referencia: artifact «API de documentos: especificación teórica y Prompt Maestro».

## 1 · Cómo arrancar y comprobar
```bash
cd guia
python servidor/api.py --puerto 8765 --imagenes imagenes        # web en http://localhost:8765 · clave admin en servidor/data/admin-key.txt
python -m unittest discover -s servidor/tests                    # 44 pruebas
python servidor/regresion.py --comprobar                         # regresión visual de los PDF
claude mcp add mystyle -e MYSTYLE_URL=http://127.0.0.1:8765 -- python <ruta>/guia/servidor/mcp_server.py
```

## 2 · Cumplimiento de la especificación del artifact
| Área | Estado | Dónde |
|---|---|---|
| Contrato único JSON + JSON Schema, 24 bloques, degradación segura, HTML libre saneado | ✔ | `engine/spec.py`, `engine/contract.py` |
| **PDF** A4 (maquetación, índice, auditoría, contraste, grises, regresión) | ✔ | `render.py` |
| **PowerPoint** 16:9 editable (gráficos/tablas/diagramas nativos, tema con paleta) | ✔ | `render_pptx.py` |
| **Word** A4 (estilos, índice, cabecera repetida, avisos, gráficos del motor del PDF) | ✔ | `render_office.py` |
| **Excel** (hoja por tabla/gráfico, números reales, totales =SUMA(), gráficos nativos) | ✔ | `render_office.py` |
| **Video** 16:9 y 9:16 con HyperFrames (cola propia, proyecto editable) | ✔ | `render_video.py` |
| Kit para /estudio-motion y /brag | ✔ | `GET /v1/designs/{id}/motion` |
| Trabajos asíncronos con estado, colas separadas (video / documentos), lotes | ✔ | `POST /v1/batch`, `GET /v1/jobs/{id}` |
| Idempotencia, informes breves con formato fijo, límites (cuerpo, hojas, video ≤ 120 s, subida 20 MB) | ✔ | `api.py` |
| URL firmadas con caducidad + retención automática (7 días; video 2; lo publicado se conserva) | ✔ | `api.py` (`sign`, `janitor`) |
| Claves de API (varias) y clave de administración | ✔ | `API_KEYS`, `servidor/data/admin-key.txt` |
| Observabilidad: tiempos y avisos por diseño, formato y bloque | ✔ | `GET /v1/stats` (admin) |
| Edición por parches (sin reenviar el documento) | ✔ | `POST /v1/jobs/{id}/patch` |
| Subidas (imagen/CSV), Wikimedia Commons con licencia y crédito | ✔ | `/v1/uploads`, `/v1/commons`, `/v1/commons/import` |
| Galería de trabajos (publicar, listar, filtrar por formato) | ✔ | `/v1/jobs/{id}/publish`, `/v1/designs/{id}/gallery` |
| Importar diseño (borrador validado) y publicarlo, solo admin | ✔ | `/v1/designs/import`, `/v1/designs/{id}/publish` |
| Kit del diseño para el modo B (zip) | ✔ | `GET /v1/designs/{id}/kit` |
| Skill y Prompt Maestro generados desde el manifiesto | ✔ | `/skill`, `POST /v1/prompt` |
| OpenAPI (ChatGPT) y servidor MCP delgado (Claude) | ✔ | `/v1/openapi.json`, `servidor/mcp_server.py` |
| Frontend: catálogo, ficha «por dentro», usar como base, taller, paleta propia con contraste en vivo, variantes con el motor real, generar prompt, galería, imágenes, MCP, nuevos estilos | ✔ | `servidor/web/` |
| Etiqueta de estilo (familia) en catálogo y diseños | ✔ | `manifest.estilo` (por defecto «brutalismo») |
| Entrada en **Markdown** (cabecera, `##` = hoja, tablas → gráfico, `:::kpi`) | ✔ (a confirmar contigo) | `engine/markdown.py`, `POST /v1/markdown` |
| Identificadores de bloque estables y parches por id | ✔ | `engine/ids.py`, `POST /v1/jobs/{id}/patch` |
| Auditoría de PDF externo (márgenes, solapes, contraste, fuentes) | ✔ | `auditar.py`, `POST /v1/audit` |
| Biblioteca de estilos/plantillas/componentes/animaciones con skills y búsqueda por similitud | ✔ | `biblioteca.py`, `servidor/biblioteca/`, `GET /v1/library` |
| Registro de correcciones (JSONL) y aprendizaje sin entrenar | ✔ | `correcciones.py`, `/v1/corrections` |
| Herramientas únicas (MCP + function calling OpenAI + HTTP) | ✔ | `herramientas.py`, `GET /v1/tools`, `mcp_server.py` |
| **Director local** (Qwen/Ollama): bucle con escalado a Claude y métrica semanal | ✔ probado con qwen2.5-coder:7b | `director.py`, `config/cerebro.json`, `AGENTS.md` |
| Evaluación con 20 entradas fijas + lote filtrado para Claude | ✔ | `evaluacion/` |
| Scripts de dataset para LoRA (Fase 4) | ✔ preparados, sin entrenar | `entrenamiento/` |
| Presets de animación de video (entrada, escalón) | ✔ | `render_video.py`, biblioteca/animaciones |
| Diseño **prompt-master** (estilo «editorial-saas») + guía de uso publicada | ✔ | `designs/prompt-master`, `contenido/prompt_master_uso.*` |
| Estadísticas de tokens con vs sin la herramienta | ✔ | `tools/tokens.py`, `/estadisticas` |

## 3 · Pendiente que puedo hacer yo (orden sugerido)
**Tanda ejecutada (2026-10-18):** H1, S1–S5, O1, O2, D1–D8 y la preparación de D9 (ver bitácora). Plan original en [PROMPTS_SIGUIENTES.md](PROMPTS_SIGUIENTES.md).
Queda de esa tanda: miniatura de PDF de /formatos con la portada completa (CRITICA_DISENO.md #6) y la corrida de entrenamiento (tuya, ver §4).

**Nueva línea (2026-10-18):** [PLAN_DIRECTOR_CREATIVO.md](PLAN_DIRECTOR_CREATIVO.md) — modelo local como director creativo (D1–D9), integrado al reparto Haiku/Sonnet/Opus.

Además, de la revisión del artifact:
2. **Ranuras de imagen por plantilla** en el frontend (hoy la búsqueda/subida está en el Taller y se copia el `src`), y aceptar **URL externa** de imagen con lista de dominios permitidos.
3. **Presets**: guardar la selección completa (diseño, formato, variantes, paleta) con la misma forma del contrato, no solo la paleta.
4. **Chromium reutilizado** (pool de páginas) y caché de gráficos renderizados; hoy cada PDF abre Chromium.
5. **Regresión visual de PPTX** (PPTX → PNG con PowerPoint/LibreOffice → comparar con «golden») y galería aprobable de diapositivas.
6. **Gráficos vectoriales en Word** (SVG con PNG de respaldo); hoy van como PNG 2x.
7. **Skill de gráficos propia** con `/skill-creator` sobre `dataviz`, leyendo el estilo de gráfico del manifiesto.
8. **Versiones conservadas** de cada diseño (hoy se sobrescribe; los trabajos guardan su JSON pero no la versión del diseño).
10. Entrada en **Markdown** (si lo apruebas), formato **Carta**, **ecuaciones**, fuentes y logos subidos por el usuario.
11. **Audio** en el video (música/efectos libres) y transiciones más ricas con `/estudio-motion`.
12. `GET /v1/libs/{nombre}/{versión}` (hoy lo cubre el kit; el video ya trae GSAP local).

## 4 · Solo tú puedes hacerlo (necesito tu decisión, tu cuenta o tu permiso)
- [ ] **Dónde corre**: VPS o contenedor propio, dominio y TLS (o un túnel) para que ChatGPT/Claude externos lleguen a la API.
- [ ] **Probar con un agente real**: ChatGPT con el OpenAPI (Acción personalizada) y Claude Code con `claude mcp add …`. Yo escribí los documentos de prueba; falta la prueba independiente.
- [ ] **Docker**: abrir Docker Desktop (está instalado pero detenido) y aprobar que construya la imagen, o construirla tú.
- [ ] **Fuentes en el servidor**: instalar los `.ttf` de `/v1/designs/{id}/fonts.zip` (cambio del sistema: necesita tu permiso) para que PPTX y Word se vean con Anton/Archivo/Plex.
- [ ] **Licencias**: la foto del hero (fotograma de *El Padrino*) necesita licencia antes de publicar la web; Remotion si hay uso comercial; completar autor/licencia de `imagenes/enfermera.png` y `campo.png` (hoy «dato pendiente»).
- [ ] **Claves**: definir `API_KEYS` para quien use la API y guardar la clave de administración (`servidor/data/admin-key.txt`, fuera de git).
- [ ] **Preguntas abiertas del artifact**: ¿se acepta Markdown? ¿quién más puede crear diseños? ¿la skill del diseño la instala la API o cada usuario? ¿formato Carta?
- [ ] **Versionar**: nada está en commit todavía. Decide cuándo hacer commit/push.
- [ ] **Música** para los videos: elegir fuente libre de derechos si quieres audio.

## 5 · Bitácora de instrucciones del usuario
Cada instrucción nueva se anota aquí (fecha, pedido, estado) antes de ejecutarla.

| Fecha | Instrucción | Estado |
|---|---|---|
| 2026-10-17 | Reescribir el frontend: presentación de la API, uso con agentes externos, catálogo tipo librería con ficha «por dentro» y «usar» | ✔ |
| 2026-10-17 | Instalar las skills del artifact (brag, Remotion, Hyperframes…) y dividir el plan en etapas Sonnet / Opus | ✔ |
| 2026-10-17 | Usar /ui-ux-pro-max para el diseño y Wikimedia Commons para las imágenes | ✔ |
| 2026-10-17 | PPTX editable listo | ✔ |
| 2026-10-17 | Rutas por sección (/ruta), nombre myStyle, hero con la imagen dada, modo oscuro con la Paleta 7, auditoría completa, tablas sin salto en atributos, arreglar solape de «manda datos» | ✔ |
| 2026-10-17 | Motor de video listo con /brag, /estudio-motion, Remotion/HyperFrames | ✔ |
| 2026-10-17 | Todas las plantillas bajo la etiqueta «brutalismo»; estilo tipo Riot/VALORANT (retroalimentación, no copia); /design:ux-copy; sección «Expande tu imaginación»; icono de tema; menú de 3 líneas responsivo | ✔ |
| 2026-10-17 | Franja de cifras con más aire; /estilos sin rojo fuerte (neutro + medio + acento) | ✔ |
| 2026-10-17 | Logo de 3 círculos (indicador RGB, cambia con el tema) también como icono de la pestaña | ✔ |
| 2026-10-17 | Revisar todo lo del artifact, corregir lo posible y listar lo que solo puede hacer el usuario | ✔ (este archivo) |
| 2026-10-17 | Consolidar en un md lo que falta y anotar aquí las instrucciones nuevas; continuar después con la creación | ✔ |
| 2026-10-17 | El logo debe coincidir con la identidad visual (Paleta 7) | ✔ S1 (rojo + noche + tono claro; multiply en claro, screen en oscuro) |
| 2026-10-17 | En /formatos quitar las fotos y poner referencias reales que, al hacer clic, lleven a los ejemplos | ✔ H1 (`servidor/web/fmt/`) |
| 2026-10-17 | Crear paleta con cuentagotas: abrir una imagen y armar la paleta desde ella | ✔ S2 (Taller → «Paleta desde una imagen») |
| 2026-10-17 | Mejorar el filtro de /catalogo | ✔ S3 (desplegables con conteo, píldoras, orden, URL) |
| 2026-10-17 | Probar el creador de estilos con *Guia-Prompt-Master-v2.pdf*: estilo nuevo, PDF con la API y mostrarlo en la web; considerar el gasto de tokens | ⏳ planificado → O1 |
| 2026-10-17 | Estadísticas: cuánto gasta crear video, PDF y PPTX con la herramienta vs sin ella, también desde cualquier agente | ⏳ planificado → O2 + S4 |
| 2026-10-17 | /design:design-critique para criticar y corregir la web (espacios apeñuscados, márgenes) — **marcado para después** | ⏳ planificado → S5 |
| 2026-10-17 | Dividir todo por modelo (Haiku, Sonnet, Opus) para ahorrar tokens y escribir el paso a paso con /prompt-master | ✔ [PROMPTS_SIGUIENTES.md](PROMPTS_SIGUIENTES.md) |
| 2026-10-17 | **Esperar a que el usuario revise el plan antes de empezar, de Haiku a Opus** | ✔ aprobado el 2026-10-18: se ejecuta H1→S1→S2→S3→D… |
| 2026-10-17 | Con esa tanda y lo que falte, dar el proyecto por cerrado | ⏳ tras H2 |
| 2026-10-18 | Añadir al planificado el artifact «Plan operativo: Director Creativo local» (modelo local + biblioteca + correcciones + Markdown + Soup) | ✔ planificado → [PLAN_DIRECTOR_CREATIVO.md](PLAN_DIRECTOR_CREATIVO.md) (D1–D9), ⏸ en espera de tu revisión |
| 2026-10-18 | «Autorizo… dejar a Qwen listo para generar PDF fácil… hagámoslo desde el principio» | ✔ H1, S1, S2, S3, O1, O2, S4, S5, D1–D8, D6; D9 preparado (entrenas tú) |
| 2026-10-18 | Detener contenedores Docker de pnepot (penpot) y guia | ✔ detenidos; `guia-guia-1` reapareció por su política `unless-stopped` y se detuvo otra vez; los de penpot tienen `always` y volverán al reiniciar Docker |
| 2026-10-18 | Quedó pendiente de tu aprobación: descargar **Space Grotesk** (OFL) para los numerales de prompt-master; hoy usa Archivo 900 | ⏸ |
| 2026-10-18 | Entregable de la noche: que Codex, Antigravity, OpenCode, Haiku u otro cree diseños nuevos con variantes y recursos usando solo un manual/skill y herramientas servidas (sin entrenar); añadir anime.js y lo demás del artifact; avisar el modelo por etapa; idea «supermercado»: ingredientes y mezclas listas en vez de un JSON desde cero | ⏳ en ejecución → [PLAN_SUPERMERCADO.md](PLAN_SUPERMERCADO.md) (E1–E6) |
| 2026-10-18 | Respuesta: «1. sí 2. sí 3. sí y todo lo demás three.js etc.» (E1 con Sonnet + E1b con Haiku; 12 recetas; instalar anime.js y el resto) | ✔ E1, E1b, E2, E3, E4 hechas (ver bitácora de la etapa); ⏳ E5 (manual) y E6 (prueba Haiku = Opus) |
| 2026-10-18 | «Añade esto al repo»: pruebas de Postman cuando le hago una solicitud a la API (modelo: colección + guía + GET de verificación) | ✔ `postman/` (26 solicitudes, 61 comprobaciones) + `POSTMAN_DOCUMENTATION.md` + sección en README; ⏳ repetir newman tras reiniciar la API (arreglo de `POST /v1/recipes`) |
