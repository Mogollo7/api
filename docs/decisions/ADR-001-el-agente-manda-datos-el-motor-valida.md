# ADR-001: El agente manda datos; el motor dibuja y valida

## Status
Accepted

## Date
2026-10-16

## Context
Los agentes de IA escriben HTML y CSS inconsistentes: márgenes rotos, contrastes ilegibles, texto que se sale de la hoja. Cada documento se rehacía varias veces y gastaba decenas de miles de tokens.

## Decision
El agente solo entrega **contenido** (contrato JSON o Markdown). El motor (`servidor/engine`, `render*.py`) asigna el contenido a bloques con un diseño declarativo, valida (contrato, contraste, márgenes, redundancia) y devuelve `avisos` que el agente corrige con `patch`.

## Alternatives Considered

### Que el agente escriba HTML/CSS y lo convierta a PDF
- Pros: máxima libertad.
- Cons: nada garantiza márgenes ni contraste; cada modelo produce algo distinto.
- Rejected: la calidad dependería del modelo.

### Plantillas Word/PowerPoint con campos
- Pros: familiares.
- Cons: no sirven para video ni web, y no validan el diseño.
- Rejected: cubren un formato, no seis.

## Consequences
- Un mismo contenido sale como PDF, PPTX, Word, Excel, video y web.
- Lo no estándar no rompe: se degrada con aviso (`ESTANDARES.md`).
- Los diseños nuevos son datos (`designs/<id>/`), no código.
