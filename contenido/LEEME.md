# Contenido escrito como agente externo

`guia.json` es todo lo que escribí **como agente**: datos para el contrato, sin código de diseño. Salió de
`teoria/guia.md` (tabla de contenido de §33), `teoria/anura-hallazgos.md` y los gráficos de `teoria/graficos-datos.html`.

Lo que seguí del Prompt Maestro y del sistema de diseño ANURA (README, `documentos.md`, `imagenes.md`, `auditoria.md`):
solo enviar contenido y decisiones (qué dice cada sección, qué tabla o gráfico, qué imagen); marcas `[FUENTE]`, `[INF]`,
`[SIN FUENTE]`, `[CALC]`, `[RESUMEN]` de `guia.md` conservadas; cifras sin dato como «dato pendiente»; estimaciones solo con
`[SIM]` y gráfico rayado; coma decimal; sin cifras inventadas.

## Decisiones que conviene revisar

- **Diseño:** usé ANURA (artifact enlazado), no Lima HUD/Aquire de `CONTINUAR.md` §3, porque ese kit no estaba entre los
  enlaces. Los bloques y el contenido no dependen del diseño: otro manifiesto cambia el aspecto, no el JSON. Por eso el PDF
  lleva portada con rana, divisores A–D y hojas crema, no negro/lima ni mascota.
- **Hojas:** «verde de punto clave» = `kind: "clave"` (tarjeta bosque con borde duro); «tablero» = tarjetas de gráficos
  lado a lado; «negra de apertura» = los 5 divisores (el índice de §33 pide apertura en §6 y §20: coinciden con el inicio de las partes 2 y 5).
- **Pendiente en el PDF** (no inventado): 2 imágenes «IMAGEN NECESARIA» (larva y adulto de trips con escala),
  crédito de `pares/rhinella_horribilis_1.jpg` (no está en `creditos.csv`), tamaños de larva/prepupa/pupa, norma ICA,
  FLOPs de BioCLIP, y lo de §34.
- **No integrado:** `research_notes/Fotos vacíos e insectos por contexto/` (PROMPT_PDF.md lo marca como pendiente de pasar
  a `guia.md`); el PDF sale de `guia.md` tal como está.
