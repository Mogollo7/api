# Prompt para generar el PDF (sesión en la nube, repo Mogollo7/guia)

Pega esto como primer mensaje en una sesión de Claude Code con este repo:

---
Lee completo `teoria/CONTINUAR.md`, `teoria/guia.md` (Partes 1 a 4; tabla de contenido definitiva en §33; pendientes en §34) y `teoria/anura-hallazgos.md` (Parte A y Parte B). Después lee `research_notes/*/*.md` (fuentes) y mira `teoria/imagenes/` (+ `creditos.csv`, `LEEME.md` si existen) y `teoria/graficos-datos.html`.

Objetivo: PDF A4 «Guía de IA: cómo hacer que un modelo distinga animales», teoría de cómo desarrollar un modelo que identifique especie, etapa, sexo y salud usando contexto. Lectores: estudiantes; caso conductor Frankliniella (trips, §32). Sin app, sin PNG de portada (portada solo tipográfica, sin mascota).

Reglas (CONTINUAR.md §3, no reabrir): negro #0b0d12, lima #dfff04 (nunca como texto sobre blanco), papel blanco; títulos en Aquire (`teoria/fonts/`, solo mayúsculas sin tildes); bloques con esquinas interiores cóncavas (radio 44 pt); fondo de glifos grises (◎ ✕ □ + ·) nunca bajo texto; mascota con bocadillo solo en notas extra; sin neón, scanlines, glitch ni sombras; hojas normal / verde / negra de apertura / tablero, todas con cabecera y pie HUD. Cifras sin dato: «dato pendiente». Estimaciones solo con la marca «SIMULACIÓN». Respeta las etiquetas [FUENTE]/[INF]/[SIN FUENTE] de guia.md.

Haz: 1) sigue la tabla de §33; 2) redacta cada sección desde su § de origen; 3) usa los gráficos de `graficos-datos.html` y dibuja con SVG/CSS los que faltan (línea de vida del trips, especie×etapa×sexo, fine-tuning vs congelado, escalera de pocas imágenes, escala del prior, árbol taxonómico, pipeline); 4) donde falte una imagen escribe «IMAGEN NECESARIA»; 5) renderiza el PDF a `salida/guia.pdf` (HTML + Chromium/WeasyPrint) y revisa páginas; 6) al final lista qué quedó pendiente.
---

## Qué falta (a 2026-10-15)
- Integrar en `guia.md` lo de `research_notes/Fotos vacíos e insectos por contexto/` (insectos por contexto: hospedero, dieta, daño, trampas; vacíos cerrados: Gosner, BBCH, FLOPs OpenCLIP, datos de gráficos). Está en los notas, no en la guía.
- Fotos: solo hay lo que haya en `teoria/imagenes/` (renacuajos, dimorfismo); faltan síntomas y trips si la búsqueda no terminó; *R. marina* no está en el disco local (solo *R. horribilis*).
- Dato pendiente: tamaños exactos de larva/prepupa/pupa de trips (fuentes en conflicto), norma ICA para F. occidentalis, antecedente de gráficos nuevos.
- Fuentes: casi todas leídas desde resúmenes; verificar las marcadas «snippet».
