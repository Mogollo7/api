# Crítica de diseño de la web (/design:design-critique) · 2026-10-18

Alcance: /, /como, /agente, /catalogo, /taller, /formatos, /estilos, /estadisticas · 1024 y 375 px · claro y oscuro. Método: lectura del DOM con una auditoría automática (huecos verticales, objetivos táctiles, desbordes, contraste) y capturas de las vistas con más riesgo.

## Impresión general
Identidad fuerte y coherente (barra oscura, titulares condensados, esquinas cortadas, Paleta 7). La mayor oportunidad no era estética sino **de ritmo**: los espacios salían de valores sueltos (12, 18, 23, 24, 26, 28, 32, 36, 40, 44, 64, 88 px) y por eso unas secciones respiraban más que otras.

| # | Hallazgo | Prioridad | Estado |
|---|---|---|---|
| 1 | Sin escala de espaciado: 12 valores distintos entre bloques | Alta | **corregido**: escala 4·8·12·16·24·32·48·72·96 (`--s1…--s9`) aplicada a relleno de sección, pila de titular (etiqueta → título → introducción), rejillas, filtros y tarjetas |
| 2 | Objetivos táctiles < 44 px: «Ver ejemplo…» (37 px), enlace «Cómo se mide» (16 px), casillas del Taller (20 px), campo de Commons (26 px de ancho) | Alta | **corregido**: 44 px mínimo; casillas con su etiqueta completa como zona táctil; campo de Commons con ancho mínimo y salto de línea |
| 3 | Títulos con última línea de una sola palabra corta (huérfanas) | Media | **corregido**: `text-wrap: balance` en títulos y `pretty` en párrafos |
| 4 | Contador de resultados del catálogo con interlineado apretado | Media | **corregido** (1,5) |
| 5 | Etiqueta «Listo» de las tarjetas de /formatos se estira a todo el ancho | Media | **corregido** (ancho propio) |
| 6 | Miniatura de PDF en /formatos recorta el titular de la portada (página vertical en marco 16:9) | Baja | pendiente: usar la portada completa con `object-fit: contain` o una miniatura horizontal propia; requiere decidir el encuadre |
| 7 | Bordes gruesos de KPI/gráficos del estilo «prompt-master» contrastan con su aire SaaS | Baja | corregido en el diseño (borde 0,2 cqw) |

## Verificación (auditoría automática tras los cambios)
| Combinación | Desbordes | Táctiles < 44 px | Contraste | Total |
|---|---|---|---|---|
| 1024 px · claro | 0 | 0 | 0 | **0** |
| 1024 px · oscuro | 0 | 0 | 0 | **0** |
| 375 px · claro | 0 | 0 | 0 | **0** |
| 375 px · oscuro | 0 | 0 | 0 | **0** |

Límite: el panel del navegador de pruebas no llega a 1366 px; 1024 px cubre el diseño de escritorio. Contraste: se omiten fondos con degradado/imagen (hero) por no poder medirse con este método.

## Qué funciona bien
- Jerarquía clara: etiqueta mono, titular condensado, párrafo corto.
- Barra superior con menú de tres líneas, tema y estado de la API siempre a mano.
- Catálogo: portadas reales, filtros con conteo y píldoras, estado en la URL.
