# Servidor ligero de documentos (fase 1: PDF)

Código creado por Claude como constructor (ver `../CODIGO_CREADO.md`). Recibe un JSON de contenido y devuelve un PDF A4
con el diseño ANURA más un informe corto de validación. El agente no escribe HTML ni CSS.

## Probar en tu PC

```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r servidor/requirements.txt
python -m playwright install chromium                    # solo si no tienes Chromium de Playwright
python servidor/render.py contenido/guia.json -o salida/guia.pdf --imagenes teoria/imagenes
python -m unittest discover -s servidor/tests -v         # 6 pruebas
python servidor/api.py --puerto 8765 --imagenes teoria/imagenes   # API local opcional
```

Si tu Chromium está en otra ruta: `CHROMIUM_PATH=/ruta/al/chrome`. Tarda ~16 s en generar la guía de 70 páginas.

## Contrato (resumen)

```json
{"design":"anura","format":"pdf-a4","palette":"default","options":{"seed":7},
 "meta":{"title":"…","date":"…","version":"…","header_left":["…","…"],"footer":"…"},
 "document":{"cover":{"vertical":"…","title":"…","text":"…"},
   "parts":[{"id":"p1","title":"…","desc":"…","divider":"auto",
     "sections":[{"id":"s01","title":"…","tema":"…","kind":"normal|clave","lead":"…","blocks":[ … ]}]}]}}
```

Bloques: `p`, `h`, `list`, `table`, `chart` (`bar`, `hbar`, `line`, `stack`), `kpi`, `big`, `callout`
(`nota|clave|ojo|sim|pend|regla`), `image`, `flow`, `ladder`, `ranks`, `timeline`, `compare`, `toc`. Ejemplo de cada uno en
`servidor/tests/ejemplo_minimo.json` y en `contenido/guia.json`. Dos bloques consecutivos con `"half": true` se
colocan lado a lado.

## Informe

`salida/<nombre>.informe.json` lista solo lo que falla: `errores` del contrato (rechaza), `avisos` de maquetación,
`auditoria` (superposiciones, desbordes y contraste en 794 impresión, 1300 y 400 px), `imagenes_necesarias` y la
página de cada sección. Estado `ok` = sin nada que corregir.


## Novedades (v0.2)
- Paletas (`"palette": "cine"`), variantes con registro y aprobación (`galeria.py`, `aprobar.py`), gráficos estándar (hist, box, scatter, heat, map), `flowchart`,
  `figure` con cifras laterales, `form`, `custom` saneado, degradación segura de lo no estándar y protocolo de grises automático. Ver `../ESTANDARES.md`.
- Salida web: `python servidor/web.py contenido/guia.json -o salida/web/index.html --imagenes teoria/imagenes --estilo` (reglas en `../WEB.md`).
- Lectura de referencias: `servidor/tools/leer_pdf.py` y `servidor/tools/descomponer.py` (ver `../CLAUDE.md`).
- Pruebas: 15 (`python -m unittest discover -s servidor/tests`), incluida `no_estandar.json`.
