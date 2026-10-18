# ADR-002: Markdown como entrada y recetas («supermercado»)

## Status
Accepted

## Date
2026-10-18

## Context
Incluso el contrato JSON cuesta entre 1 000 y 20 000 tokens y un modelo pequeño lo escribe mal. El objetivo es que un modelo barato (Haiku, Qwen local) iguale a uno grande.

## Decision
Tres niveles: **ingrediente** (pieza suelta con huecos), **receta** (documento completo con huecos y valores por defecto) y el archivo final. El agente llama `list_recipes`, `recipe_get` (solo los huecos) y `create_from_recipe` con únicamente los huecos que cambia (~100–300 tokens). Si ninguna receta sirve, `compose` junta ingredientes; si tampoco, escribe Markdown (`engine/markdown.py`) y, en último caso, el contrato JSON.

## Alternatives Considered

### Solo Markdown
- Pros: simple.
- Cons: el modelo sigue decidiendo la estructura; la calidad varía con el modelo.
- Rejected: la calidad debe estar en la mezcla, no en quien cocina.

### Entrenar un modelo propio
- Pros: ahorra más tokens a largo plazo.
- Cons: costoso y frágil ante cada diseño nuevo.
- Rejected por ahora: queda como opción aparte (`servidor/entrenamiento/`).

## Consequences
- Cada receta se prueba sola: `python servidor/tools/probar_recetas.py --render` (sale completa sin rellenar nada).
- Lo que un agente crea y sirve de nuevo se guarda con `save_style` (recetas, ingredientes, recursos).
- Las recetas viven en la biblioteca, así que `search_library` y `list_recipes` las encuentran igual.
