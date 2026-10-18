# Plan «Supermercado»: que cualquier agente (Haiku, Codex, Antigravity, OpenCode) cree como Opus, sin entrenar

**Idea (del usuario, 2026-10-18):** el agente no escribe un JSON desde cero; **va al supermercado**: toma ingredientes y mezclas ya listas («solo agua» y sale el pastel).
Tres niveles, de menos a más listo:

| Nivel | Qué es | El agente escribe | Ejemplo |
|---|---|---|---|
| **Ingrediente** | bloque o sección suelta, ya maquetada con huecos | 1–3 campos | `kpi_4`, `tabla_comparativa`, `pasos_5`, `cita`, patrón de puntos, icono |
| **Mezcla (receta)** | documento completo con huecos y valores por defecto | los huecos (~100–300 tokens) | `informe_negocio(titulo, 4 cifras, serie, 3 medidas)` |
| **Pastel** | el archivo final | nada | PDF / PPTX / video / Word / Excel |

Hoy el agente escribe todo el contrato (1 000–20 000 tokens). Con recetas baja a unos cientos y **el resultado no depende de qué tan listo sea el modelo**: la calidad está en la mezcla, no en el cocinero. Ese es el camino para que Haiku iguale a Opus.

## Etapas, modelo recomendado y si conviene usar agentes
Regla: **modelo más barato que supere la prueba de la etapa.** Los agentes (subagentes) **no ahorran tokens** (cada uno arranca en frío y relee contexto); solo ahorran tiempo, y vale la pena con ellos únicamente para trabajo masivo e independiente o para la prueba final.

| Etapa | Qué se construye | Modelo | ¿Agentes? | Tokens aprox. |
|---|---|---|---|---|
| **E1 · Supermercado** | recetas + ingredientes: `servidor/recetas/*.json`, `engine/recetas.py`, herramientas `list_recipes`, `recipe_get` (solo huecos), `create_from_recipe`, `compose` (varios ingredientes), `POST /v1/recipes`; 12 recetas base (informe de negocio, propuesta, manual, ficha de proyecto, acta, guía de pasos, comparativo, plan trimestral, presentación de ventas, resumen en video, reporte de datos, hoja de cálculo) | **Sonnet** (diseña el mecanismo) | no | 150–250 k |
| E1b · Contenido de las recetas | textos de ejemplo, valores por defecto y «huecos» documentados | **Haiku** | sí: 3 en paralelo (4 recetas c/u), ahorra Sonnet | 60–90 k (Haiku) |
| **E2 · Fábrica de estilos** | `crear_estilo`: paleta + fuentes (+ imagen de referencia) → diseño completo **sin escribir CSS a mano**: kit de «pieles» paramétrico (radio, bordes, sombra, peso/tamaño de títulos, degradado, mayúsculas) que genera manifiesto, paletas, plantillas de portada/divisor y capa CSS; `crear_variante` (N portadas/divisores/hojas parametrizados) y validación automática en bucle | **Sonnet**; **Opus** solo si la primera piel no pasa 10/10 en dos estilos de prueba | no | 200–300 k |
| **E3 · Recursos** | `crear_recurso`: patrones SVG (puntos, rejilla, ondas, ruido, dots grid), fondos con degradado, iconos (catálogo de símbolos + paquete libre), tramas duotono, marcos; ficha de licencia por recurso; las ranas/arte propio como «presumir» | **Sonnet** (generadores) + **Haiku** (catalogar y escribir fichas) | opcional (Haiku) | 120–180 k |
| **E4 · Calidad y animación** | presets con **anime.js** (MIT, a verificar al instalar), GSAP (ya local), Lottie (reproducir), transiciones entre escenas, exportación **web animada** (HTML con anime.js), audio libre para video, **herramientas de calidad:** svgo (SVG), optimización de imágenes, corrector ortográfico en español (LanguageTool local), revisión de accesibilidad PDF (veraPDF/pikepdf: etiquetas, idioma, título), comprobación de video (`hyperframes check` + cuadros muertos) | **Sonnet** | no | 200–300 k |
| **E5 · Manual universal** | `SKILL.md` (formato skill de Claude/Codex/OpenCode/Antigravity) + `AGENTS.md` + reglas: cómo comprar en el supermercado, cuándo crear estilo/variante/recurso, límites. Un manual por tarea («hacer un informe», «crear un estilo», «hacer un video») de una pantalla | **Haiku** redacta, **Sonnet** revisa | opcional | 60–100 k |
| **E6 · Prueba Haiku = Opus** | las 20 entradas de `servidor/evaluacion` con recetas: Haiku vs Opus vs Qwen local; mismo contador de tokens y mismas métricas; informe de brecha | **Haiku y Opus como sujetos** (agentes), **Sonnet** compara | **sí** (es la prueba) | 200–400 k (sobre todo del sujeto) |

**Total estimado:** 1,0–1,6 M tokens; ≈ 40 % en Haiku. **Orden:** E1 → E1b → E5 (borrador) → E2 → E3 → E4 → E6. E5 va temprano porque con E1 ya se puede usar y probar con Haiku.

## Qué se añade del artifact (sin el entrenamiento potente)
Biblioteca de animaciones y video (anime.js, GSAP, Lottie, Remotion/Motion Canvas como opciones de licencia revisada), formatos de salida y bibliotecas (python-pptx, docx, openpyxl, PptxGenJS…), formatos extra (PNG/SVG para redes, GIF/MP4, EPUB, correo HTML, infografía, póster), componentes versionados con skill por pieza, edición por chat con secciones con nombre, correcciones aprendidas (ya hecho), portabilidad MCP/OpenAI (ya hecho). **Fuera:** Fase 4 de Soup y modelos LoRA.

## Preguntas antes de empezar (necesito tu respuesta)
1. ¿Empiezo E1 con **Sonnet** (el actual) y paso E1b a **Haiku** en 3 agentes? (recomendado)
2. ¿Qué recetas son las que más te sirven primero? (propuse 12; dime cuáles quitar o añadir).
3. ¿Anime.js se instala vía npm/CDN? (necesito tu permiso para instalar dependencias nuevas en E4).
