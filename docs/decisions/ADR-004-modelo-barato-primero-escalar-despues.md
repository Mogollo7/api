# ADR-004: El modelo más barato primero; escalar solo cuando hace falta

## Status
Accepted

## Date
2026-10-18

## Context
El gasto de tokens de un modelo grande en tareas repetitivas es innecesario. Hay un modelo local (Qwen en Ollama) y modelos de la API (Haiku, Opus).

## Decision
Se usa el modelo más barato que supere la prueba de la etapa. Se escala solo si el motor rechaza tres veces seguidas o el usuario marca que no quedó bien tras dos intentos (`director.py` deja un informe en `salida/director/`). Todo lo que resuelve el modelo grande se guarda como corrección (`save_correction`).
La comparación Haiku frente a Opus se hace con las mismas entradas y el mismo manual (`skills/mystyle/`). El modelo local queda como está; los estilos con Ollama/Qwen se añaden después, por separado.

## Alternatives Considered

### Siempre el modelo más potente
- Rejected: caro y innecesario para lo repetitivo.

### Solo modelo local
- Rejected: falla en tareas abiertas (estilos nuevos, guiones de video).

## Consequences
- Medida de éxito: `python servidor/director.py --semana` (escalados por semana; debe bajar).
- Los agentes no ahorran tokens (cada uno relee el contexto): se usan para trabajo masivo e independiente y para pruebas.
