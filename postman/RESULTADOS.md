# Resultados de Postman

Ejecución con `newman` de `postman/myStyle.postman_collection.json` contra `http://localhost:8765` (1792322923).
**26 solicitudes, 0 fallidas · 61 comprobaciones, 0 fallidas.**

| Método | URL | Estado | Tiempo | Pruebas |
|---|---|---|---|---|
| GET | `/v1/tools` | 200 OK | 30 ms | 5/5 |
| GET | `/v1/tools?perfil=minimo` | 200 OK | 6 ms | 2/2 |
| GET | `/v1/designs` | 200 OK | 6 ms | 2/2 |
| GET | `/v1/openapi.json` | 200 OK | 4 ms | 2/2 |
| GET | `/v1/recipes?q=informe%20de%20ventas` | 200 OK | 63 ms | 3/3 |
| GET | `/v1/recipes/informe_negocio` | 200 OK | 40 ms | 3/3 |
| GET | `/v1/recipes/no_existe` | 404 Not Found | 41 ms | 2/2 |
| POST | `/v1/recipes` | 200 OK | 7 ms | 3/3 |
| POST | `/v1/recipes` | 200 OK | 6 ms | 2/2 |
| POST | `/v1/render` | 200 OK | 15 ms | 5/5 |
| GET | `//v1/files/1f7847d99043.pdf?exp=…&sig=…` | 200 OK | 26 ms | 2/2 |
| POST | `/v1/markdown` | 200 OK | 4 ms | 2/2 |
| POST | `/v1/render` | 200 OK | 15 ms | 2/2 |
| POST | `/v1/render` | 200 OK | 9 ms | 2/2 |
| POST | `/v1/render` | 400 Bad Request | 6 ms | 2/2 |
| POST | `/v1/render` | 400 Bad Request | 5 ms | 2/2 |
| POST | `/v1/audit` | 200 OK | 499 ms | 3/3 |
| POST | `/v1/quality` | 200 OK | 4077 ms | 3/3 |
| POST | `/v1/quality` | 200 OK | 4676 ms | 2/2 |
| GET | `/v1/jobs/1f7847d99043/doc` | 200 OK | 5 ms | 2/2 |
| GET | `/v1/library?q=cifras%20clave&tipo=componente` | 200 OK | 10 ms | 2/2 |
| GET | `/v1/styles/anura/validate` | 200 OK | 10079 ms | 2/2 |
| POST | `/v1/styles` | 401 Unauthorized | 4 ms | 1/1 |
| POST | `/v1/resources` | 201 Created | 56 ms | 2/2 |
| POST | `/v1/resources` | 400 Bad Request | 4 ms | 1/1 |
| POST | `/v1/screenshot` | 200 OK | 125 ms | 2/2 |

## Respuestas de ejemplo

### GET herramientas (la API está viva)

`GET http://localhost:8765/v1/tools` → **200 OK** en 30 ms

Respuesta:

```json
[
  {
    "type": "function",
    "function": {
      "name": "list_recipes",
      "description": "EMPIEZA AQUÍ. Busca recetas (documentos completos con huecos) o ingredientes (piezas sueltas) para lo que te piden. Con una receta solo rellenas huecos y sale un documento completo.",
      "parameters": {
        "type": "object",
        "properties": {
          "q": {
            "type": "string",
            "description": "qué documento quieres, en palabras"
          },
          "tipo": {
            "enum": [
              "receta",
              "ingrediente"
            ]
          },
          "n": {
            "type": "integer"
          }
        },
        "required": [
          "q"
        ]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "recipe_get",
      "description": "Los huecos de una receta o ingrediente (qué escribir, máximos y valor por defecto). Es corto: no devuelve la plantilla.",
      "parameters": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          }
        },
        "required": [
          "id"
        ]
      }
    }
  },
  "…"
]
```

### GET huecos de una receta

`GET http://localhost:8765/v1/recipes/informe_negocio` → **200 OK** en 40 ms

Respuesta:

```json
{
  "id": "informe_negocio",
  "tipo": "receta",
  "nombre": "Informe de negocio",
  "descripcion": "Informe de resultados de una página y media: resumen, 3 o 4 cifras clave, tabla con gráfico y medidas. Sirve para ventas, consumo, encuestas o cualquier periodo.",
  "formato": "pdf",
  "estilo": "anura",
  "huecos": {
    "titulo": {
      "desc": "Título del informe (máx. 60 letras)",
      "defecto": "Informe de resultados del trimestre"
    },
    "resumen": {
      "desc": "Qué pasó, en 1 o 2 frases",
      "defecto": "Las ventas crecieron frente al trimestre anterior y se cumplió la meta en tres de cuatro líneas."
    },
    "…": "…"
  },
  "uso": "create_from_recipe(receta='informe_negocio', valores={…solo los huecos que quieras cambiar…})"
}
```

### POST receta → PDF

`POST http://localhost:8765/v1/render` → **200 OK** en 15 ms

Cuerpo enviado:

```json
{
  "receta": "informe_negocio",
  "valores": {
    "titulo": "Informe desde Postman"
  }
}
```

Respuesta:

```json
{
  "estado": "ok",
  "errores": [],
  "avisos": [],
  "auditoria": {},
  "imagenes_necesarias": [],
  "secciones": [
    {
      "id": "s1",
      "n": "01",
      "pagina": 3
    },
    {
      "id": "s2",
      "n": "02",
      "pagina": 4
    },
    {
      "id": "s3",
      "n": "03",
      "pagina": 5
    }
  ],
  "correcciones_contraste": [],
  "variantes_usadas": [
    "CV-1",
    "DV-A"
  ],
  "variantes_no_aprobadas": [
    "CV-1",
    "DV-A"
  ],
  "paginas": 5,
  "segundos": 4.3,
  "job": "1f7847d99043",
  "formato": "pdf-a4",
  "pdf": "/v1/files/1f7847d99043.pdf?exp=…&sig=…",
  "repetido": true
}
```

### POST receta inexistente

`POST http://localhost:8765/v1/render` → **400 Bad Request** en 5 ms

Cuerpo enviado:

```json
{
  "receta": "no_existe"
}
```

Respuesta:

```json
{
  "error": "no hay receta 'no_existe'",
  "ajuste": "busca con list_recipes y mira los huecos con recipe_get"
}
```

### POST calidad: ortografía y accesibilidad

`POST http://localhost:8765/v1/quality` → **200 OK** en 4077 ms

Cuerpo enviado:

```json
{
  "job": "1f7847d99043"
}
```

Respuesta:

```json
{
  "accesibilidad": {
    "titulo": true,
    "idioma": "es",
    "etiquetado": true,
    "paginas": 5,
    "fuentes_no_incrustadas": [],
    "avisos": []
  },
  "ortografia": {
    "disponible": true,
    "errores": 2
  }
}
```
