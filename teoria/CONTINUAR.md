# Estado del trabajo y cómo continuar

Guardado el 2026-10-14. Léelo entero antes de tocar nada. Está pensado para que una sesión nueva retome sin que el usuario repita nada.

## 1. Objetivo

Hacer un PDF: **guía universal para que un modelo de IA distinga animales** (o cualquier cosa). Con el stack del usuario, la guía debe decir qué ruta seguir, qué método probar primero y qué resultado esperar. Debe incluir la teoría, el estilo visual del PDF y qué imágenes, mockups y gráficos hacen falta.

El usuario irá dando más información (stack, md a leer, datos). Hasta que diga lo contrario, **solo recopilas información**; no redactas el PDF final.

## 2. Reparto por modelo (de `pormt.txt`)

- **Haiku:** organiza carpetas, busca y agrupa datos y notas (propias y de otros), prepara el plan.
- **Sonnet:** redacta el texto, define dónde van imágenes y gráficos. Prefiere el tablero visual / dashboard informativo a gráficos planos.
- **Opus:** revisa exactitud técnica y aprueba el diseño antes de producir archivos finales.
- Skills a usar: `/frontend-design` (dibujar elementos con CSS), `/ui-ux-pro-max` (distribución e identidad). Las skills viven en `C:\Users\user\Downloads\SoNotes\andorid`.

## 3. Reglas del usuario (no reabrir)

- Paleta: negro `#0b0d12`, lima `#dfff04`, papel blanco, gris de glifos por superficie (`#cfd2d6` papel, `#2c3138` negro, `#b7d100` lima). Lima nunca como texto sobre blanco.
- Títulos en **Aquire** (archivos en `teoria/fonts/`; solo mayúsculas, sin tildes; licencia freeware no comercial).
- Forma principal: bloques fusionados con **esquinas interiores cóncavas** (radio 44 pt dentro y fuera), al estilo del póster cyberpunk.
- Fondo: **glifos grises** (◎ ✕ □ + ·) en manchas que se deshacen en puntos, nunca bajo el texto. Sustituye a los puntos.
- La **mascota** habla con **bocadillo** cuando una nota da un detalle o información extra. Sin mascota en la portada.
- Estilo retrofuturista impreso: sin neón, scanlines, glitch ni sombras.
- Portada preferida como referencia: **Hoja negra · apertura** (de `identidad.html`).
- Hojas del PDF: normal (papel), **verde** de punto clave, **negra** de apertura, tablero de datos. Todas con cabecera y pie HUD.
- Quitar EfficientNet de la guía (hecho).
- Cuando falte una imagen, mockup o gráfico, decirlo (se marca "IMAGEN NECESARIA").
- Cifras sin datos reales: "dato pendiente", nunca inventadas.

## 4. Archivos creados (todos en `C:\Users\user\Downloads\SoNotes\andorid\teoria\`)

| Archivo | Qué es |
|---|---|
| `guia.md` | Guía en md: teoría (§1), estilo (§2), imágenes (§3), reparto (§4), identidad (§5), datos a pedir a la DB (§6), **guía universal de ruta de método (§6b)**, dudas (§7) |
| `anura-hallazgos.md` | **Recopilación de `D:\Anura` y `D:\server\Anura`**: resultados con condiciones, segmentación, errores, datos, teoría, y reglas de decisión (§10) |
| `identidad.html` | Identidad visual: base, fondo de glifos, 4 portadas, 4 hojas interiores, elementos HUD, auditoría |
| `portadas-pdf.html` | 6 portadas A4 sobre la forma-lima, 8 formas, tablero de elementos |
| `portada-variaciones.html` | 6 variaciones iniciales de portada |
| `inner-corner-layout.html` | Disposición inner corner con 12 piezas numeradas |
| `elementos-referencia.html` | 30 piezas sacadas de las imágenes de referencia (aproximadas, no recortes) |
| `fonts/` | Aquire Light, Regular, Bold |
| `CONTINUAR.md` | Este archivo |

## 5. Artefactos de claude.ai

- **Notas Lima HUD** (copia reutilizable, la vigente): https://claude.ai/artifact/C2yTU64di9TN5JADyNBb7M. Tiene lima, Aquire, InnerCorner, FondoGlifos, Hojas, ElementosHUD, Portadas, Bocadillo y la mascota.
- **Notas Dot Grid** (original): https://claude.ai/artifact/VmJ4DjSH76vrZbmvYA9T2E. Restaurado a su versión monocroma (v14). No lo cambies.
- Son de tipo Design System: el contenido va en `project/…` y se publica con `root` + `file_path`; el índice `design-system.json` se publica **último**. `index.d.ts` necesita `contentType: text/plain`.
- Copia de trabajo local en la carpeta de scratchpad de la sesión anterior (puede no existir); si no está, léelo del artefacto.

## 6. Dónde está la información

- **Obsidian (vaults encontrados):** `C:\Users\user\Documents\obsidian\cyberseguridad`, `Downloads\semillero\semillero`, `Downloads\SO\SO`, `Downloads\SoNotes\notas clase`.
- **Anura:** `D:\Anura\Second Brain\Brain` (189 md), `D:\Anura` (raíz con planes), `D:\Anura\validation`, `D:\Anura\evaluation`, `D:\Anura\bioclip`, `D:\Anura\training`, `D:\Anura\segmentacion`, y `D:\server\Anura`.
- En esas rutas, no listes con `Get-ChildItem -Recurse` en todo `D:\Anura`: hay datasets enormes y `.venv`; se cuelga. Usa `Glob`/`Grep` por subcarpeta.

## 6b. Qué NO se ha leído de Anura

~100 notas de la bóveda sobre app, diseño, Kotlin y guía CVAT; `D:\server\Anura\docs`, `README`, `DEPLOY_LINUX`; informes de fases 11, 12, 14, 15 y 18 de `validation/`; `evaluation/fase13/*`; logs de scraping y `.py` completos.

## 7. Hallazgos clave (resumen; detalle en `anura-hallazgos.md`)

- Quitar el fondo / recortar al animal **empeoró** el resultado (60,7 % → 50,7 % → 44,7 %). Nunca se probó reentrenar con recortes.
- Prior geográfico: +15 a +25 pp, pero solo para reordenar; nunca decide la especie.
- Paquete regional + k-NN: +11,8 pp frente a un clasificador de 41 clases.
- INT8 en ViT falla; usar FP16. La destilación a un modelo pequeño falló (−33 pp).
- Mahalanobis con covarianza compartida degradó el rechazo; coseno o euclídea cruda fueron mejores. El rechazo de desconocidos sigue sin resolverse (FAR 52–94 %).
- Cuello de botella: pares de especies hermanas casi idénticas en el embedding.
- Contaminación de datos y evaluaciones infladas fueron un error recurrente.

## 8. Pendiente

1. El usuario dará el **stack**, los **md a leer** y los datos que faltan.
2. Pasar los hallazgos a la guía universal (`guia.md` §6b) cuando el usuario lo pida.
3. Elegir portada del PDF (candidatas: Hoja negra · apertura, y las 4 de `identidad.html`).
4. Pendientes de imágenes: figura PNG sin fondo para la portada, diagramas del pipeline, gráficos del tablero de datos.
5. `guia.md` §7 tiene dudas abiertas: especies y región del modelo del usuario, y si las notas de compañeros son citables.
6. Si se quiere, añadir al artefacto lo nuevo (por ejemplo, la hoja "apertura" como componente).

## 9. Prompt para la sesión nueva

Pega esto como primer mensaje:

```
Lee completo C:\Users\user\Downloads\SoNotes\andorid\teoria\CONTINUAR.md y luego C:\Users\user\Downloads\SoNotes\andorid\teoria\anura-hallazgos.md y C:\Users\user\Downloads\SoNotes\andorid\teoria\guia.md. Son el estado de un trabajo largo: una guía universal en PDF para que un modelo de IA distinga animales (ruta, método a probar, resultado esperado), con una identidad visual retrofuturista (negro, lima #dfff04, papel, tipografía Aquire, esquinas interiores, fondo de glifos grises, mascota con bocadillo).

Respeta las reglas de la sección 3 de CONTINUAR.md sin reabrirlas. No inventes cifras: si falta un dato escribe "dato pendiente". Hasta que yo lo diga, solo recopilas y organizas información; no redactes el PDF final.

Voy a darte más información (stack, md a leer, datos). Cuando te la pase: 1) léela entera, 2) añade lo nuevo a anura-hallazgos.md o guia.md según corresponda, 3) dime qué datos siguen faltando y qué imágenes, mockups o gráficos necesitas. Si algo depende de un archivo que no encuentres, pregúntame la ruta antes de suponer.
```
