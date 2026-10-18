# ADR-003: Una sola definición de herramientas para MCP, OpenAI y terminal

## Status
Accepted

## Date
2026-10-18

## Context
Claude Code, Codex, OpenCode, Antigravity y los modelos locales hablan protocolos distintos (MCP, function calling, HTTP). Mantener una definición por cliente se desincroniza.

## Decision
`servidor/herramientas.py` define cada herramienta una vez y sirve tres puertas: el servidor MCP (`mcp_server.py`), `GET /v1/tools` (function calling estilo OpenAI, con `?perfil=minimo` para modelos pequeños) y la terminal (`python servidor/herramientas.py call <herramienta> '<json>'`). `servidor/conectar.py` imprime o escribe la configuración de cada agente.

## Alternatives Considered

### Un servidor MCP por agente
- Rejected: duplica código y divergen las descripciones.

### Solo HTTP/OpenAPI
- Rejected: MCP es la integración natural en Claude Code y Codex.

## Consequences
- Una herramienta nueva aparece sola en las tres puertas.
- El perfil mínimo (9 herramientas) mantiene corto el contexto de un modelo de 3B.
- El cliente local lee la clave de administración sola; en una instalación expuesta hay que fijar `API_KEYS`.
