# ADR-005: Fábrica de estilos con «pieles» en vez de CSS a mano

## Status
Accepted

## Date
2026-10-18

## Context
Crear un estilo costaba ~76 000 tokens y cuatro iteraciones visuales (medido con Prompt Master). Un agente pequeño no puede escribir esa capa de CSS.

## Decision
`servidor/fabrica_estilo.py` parte de `prompt-master` y genera un diseño completo desde un acento (o 7 colores), una **piel** (suave, recta, redonda, editorial) y un modo (claro u oscuro): manifiesto, paletas, variantes, capa CSS y la lista de 10 chequeos. `analyze_reference` lee la imagen del usuario y propone el comando. Los agentes la usan por las herramientas `create_style`, `create_variant`, `validate_style` y `screenshot`.

## Alternatives Considered

### Pedir al agente que escriba el CSS
- Rejected: caro y propenso a romper contraste y márgenes.

### Un solo estilo con muchos temas
- Rejected: no cubre formas distintas (radios, trazos, mayúsculas).

## Consequences
- Un estilo nuevo es un comando y ~10 s; lo que no cubre una piel (formas nuevas, fuentes nuevas) sigue siendo trabajo de diseño (`servidor/designs/LEEME.md`).
- Los estilos generados nacen como «propuesta» y no aparecen en la lista pública hasta que se aprueban.
