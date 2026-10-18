# Pruebas con Postman

La colección `postman/myStyle.postman_collection.json` tiene 26 solicitudes agrupadas por operación. Cada una trae pruebas automáticas (`pm.test`) que verifican el estado HTTP y el contenido de la respuesta: son las pruebas que corren **cada vez que le haces una solicitud a la API**.

## Importar y preparar

1. Arranca la API: `python servidor/api.py --puerto 8765 --imagenes imagenes`.
2. En Postman: **Import** → elige `postman/myStyle.postman_collection.json` y `postman/myStyle.local.postman_environment.json`.
3. Selecciona el entorno **myStyle local** (variable `baseUrl` = `http://localhost:8765`).
4. Ejecuta la colección con **Run collection**, de arriba abajo. La solicitud «receta → PDF» guarda `job` y `pdfUrl`; las de «Revisar y corregir» y la descarga del PDF las usan.

Sin Postman, en terminal (el mismo resultado):

```bash
npx newman run postman/myStyle.postman_collection.json -e postman/myStyle.local.postman_environment.json
```

## 1. Verificar la API

* Método: `GET`
* URL completa: `http://localhost:8765/v1/tools`

Respuesta esperada (`200 OK`, lista de herramientas en function calling estilo OpenAI):

```json
[
  { "type": "function", "function": { "name": "list_recipes", "description": "EMPIEZA AQUÍ. Busca recetas …", "parameters": { "type": "object", "properties": { "q": { "type": "string" } }, "required": ["q"] } } },
  { "type": "function", "function": { "name": "recipe_get", "…": "…" } }
]
```

Pruebas: estado 200, responde JSON, hay al menos 20 herramientas, incluye `list_recipes` y `create_from_recipe`, tarda menos de 15 s.

## Orden y resultados esperados

| Grupo | Solicitud | Resultado esperado |
|---|---|---|
| 1. Verificar la API | `GET /v1/tools` · `GET /v1/tools?perfil=minimo` · `GET /v1/designs` · `GET /v1/openapi.json` | 200; perfil mínimo ≤ 12 herramientas; diseños con `id`, `name`, `version`; OpenAPI con `paths` |
| 2. Supermercado | `GET /v1/recipes?q=informe de ventas` | 200; la primera coincidencia es `informe_negocio` |
| | `GET /v1/recipes/informe_negocio` | 200; solo huecos con `defecto`, sin la plantilla |
| | `GET /v1/recipes/no_existe` | 404 con `ajuste` |
| | `POST /v1/recipes` | 200; `markdown` con el título pedido y `avisos: []` |
| | `POST /v1/recipes` con un hueco inventado | 200 con 1 aviso |
| 3. Crear archivos | `POST /v1/render` `{receta}` | 200; `estado` ok/con_avisos, `job` de 12 hex, `pdf` firmado |
| | `GET {{pdfUrl}}` | 200, `application/pdf` |
| | `POST /v1/markdown` | 200; devuelve el contrato |
| | `POST /v1/render` a PowerPoint y a `web-animada` | 200; devuelve `.pptx` y `.html` |
| | formato desconocido / receta inexistente | 400 con `error` o `ajuste` |
| 4. Revisar y corregir | `POST /v1/audit` · `POST /v1/quality` (por `job` y por `texto`) · `GET /v1/jobs/{{job}}/doc` | 200; PDF etiquetado e idioma `es`; ortografía si LanguageTool está instalado |
| 5. Biblioteca, estilos y recursos | `GET /v1/library?q=…` · `GET /v1/styles/anura/validate` | 200; encuentra `kpi`; los 10 chequeos en ✔ |
| | `POST /v1/styles` sin clave | 401 (crear estilos es de administración) |
| | `POST /v1/resources` (válido e inválido) | 201 con `src`; 400 |
| | `POST /v1/screenshot` | 200 con PNG firmado |

## Notas

- Crear estilos exige la clave de administración (`servidor/data/admin-key.txt`): para probarlo con éxito añade el encabezado `Authorization: Bearer <clave>` a esa solicitud.
- Si configuraste `API_KEYS`, añade `Authorization: Bearer <tu clave>` a la colección (pestaña *Authorization*).
- El video (`create_video`) no está en la colección porque tarda minutos; se prueba con `python servidor/herramientas.py call create_video …`.
- Las solicitudes de la API local crean archivos temporales que el servidor borra solo (retención configurable).
