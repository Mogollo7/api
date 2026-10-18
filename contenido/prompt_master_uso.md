---
titulo: Cómo usar myStyle con tu agente
objetivo: Guía corta para que cualquier agente cree PDF, presentaciones y videos con myStyle sin empezar de cero.
formato: pdf
estilo: prompt-master
paleta: prompt-master
autor: Equipo myStyle
fecha: Octubre 2026
vertical: AGENTES
---

# Antes de empezar

## Qué hace myStyle por tu agente

Tu agente escribe el contenido; myStyle lo **maqueta, lo valida y lo entrega** en el formato que pidas. El motor revisa márgenes, superposición y contraste, así que el agente corrige con avisos concretos en vez de adivinar.

:::kpi
5 | formatos de salida
24 | bloques del contrato
13 | herramientas para el agente
3 | diseños disponibles
:::

> [!NOTA] Los formatos son PDF, PowerPoint, Word, Excel y video. El mismo contenido sirve para todos.

## Conecta tu agente en cuatro pasos

1. Enciende la API con `python servidor/api.py --puerto 8765`.
2. Conéctala por MCP con `claude mcp add mystyle -- python servidor/mcp_server.py` (OpenCode y Codex usan la misma línea en su configuración).
3. Si tu agente no habla MCP, usa `GET /v1/tools` o el archivo `/v1/openapi.json`.
4. Para un modelo local, ejecuta `python servidor/director.py "lo que quieres" --formato pdf`.

# Crear documentos

## El flujo de trabajo en cinco pasos

1. Buscar un estilo parecido con `search_library`.
2. Escribir el contenido en Markdown con cabecera, secciones, listas y tablas.
3. Crear el archivo con `create_pdf`, `create_pptx` o `create_video`.
4. Leer los avisos del resultado y corregir con `patch`.
5. Auditar el PDF con `audit` antes de entregarlo.

> El agente decide cómo presentar; el motor decide si pasa.
> — Regla central de myStyle

## Qué herramienta usar para cada cosa

| Herramienta | Para qué sirve | Perfil mínimo |
|---|---|---|
| search_library | Encontrar estilos, plantillas y componentes | Sí |
| library_get | Ver parámetros y un ejemplo correcto | Sí |
| create_pdf | Crear un PDF A4 | Sí |
| create_pptx | Crear una presentación editable | Sí |
| create_video | Crear un video MP4 | Sí |
| audit | Revisar márgenes, solapes y contraste | Sí |
| patch | Corregir un bloque sin rehacer todo | Sí |
| save_style | Guardar un estilo nuevo | Sí |
| render | Crear Word o Excel | No |

## Lo que contiene la biblioteca

Cada entrada tiene su ficha de una pantalla: qué es, cuándo usarla, parámetros, un ejemplo correcto y el error típico.

| Tipo | Entradas |
|---|---|
| Plantillas | 155 |
| Componentes | 34 |
| Animaciones | 5 |
| Estilos | 3 |
{grafico: hbar}

# Mejorar con el tiempo

## Corrige sin empezar de cero

Cada bloque tiene un identificador estable, así que un parche apunta a él sin depender de su posición. Si pasas el motivo, la corrección queda guardada para casos parecidos.

- Cambiar un bloque: operación `set` con el id del bloque.
- Añadir contenido: operación `insert` en la sección.
- Quitar un bloque: operación `delete`.
- Dejar constancia: el campo `motivo` explica qué estaba mal.

## Cuándo pedir ayuda a Claude

Primero trabaja el modelo local y lo valida el motor. Solo se recurre a Claude en dos casos:

- El motor rechaza el resultado tres veces seguidas.
- Tú marcas que no quedó bien y el modelo local no lo corrige en dos intentos.

:::big
3 | rechazos seguidos y se escala a Claude
:::

Medida de éxito: anotar cada semana cuántas veces hizo falta. Si baja, el sistema funciona.
