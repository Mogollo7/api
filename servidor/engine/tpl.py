# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Motor de plantillas mínimo para portadas y divisores de un diseño (designs/<id>/templates/*.html). Sin dependencias.

  {{ruta.a.campo}}      valor escapado (HTML)         {{&ruta}}   valor sin escapar (HTML ya saneado por el servidor)
  {{#if x}}…{{else}}…{{/if}}                          {{#each lista}}… {{campo}} o {{.}} …{{/each}}
Las rutas se buscan primero en el elemento actual del `each` y luego en el contexto global. Lo que falta se imprime vacío.
"""
import html
import re

TOK = re.compile(r"\{\{\s*(#if|#each|/if|/each|else|&)?\s*([\w.\-]*)\s*\}\}")


def _get(ctx_stack, path):
    if path == ".":
        return ctx_stack[-1]
    for ctx in reversed(ctx_stack):
        cur = ctx
        ok = True
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok:
            return cur
    return ""


def _parse(src):
    """Árbol: lista de nodos str | ('var', raw, path) | ('if', path, then, else) | ('each', path, body)."""
    pos, stack = 0, [[]]
    stack_meta = []
    for m in TOK.finditer(src):
        stack[-1].append(src[pos:m.start()])
        pos = m.end()
        kind, path = m.group(1), m.group(2)
        if kind is None or kind == "&":
            stack[-1].append(("var", kind == "&", path))
        elif kind == "#if":
            stack.append([])
            stack_meta.append(["if", path, None])
        elif kind == "#each":
            stack.append([])
            stack_meta.append(["each", path, None])
        elif kind == "else":
            stack_meta[-1][2] = stack.pop()
            stack.append([])
        elif kind in ("/if", "/each"):
            body = stack.pop()
            meta = stack_meta.pop()
            if meta[0] == "if":
                then, els = (meta[2], body) if meta[2] is not None else (body, [])
                stack[-1].append(("if", meta[1], then, els))
            else:
                stack[-1].append(("each", meta[1], body))
    stack[-1].append(src[pos:])
    return stack[0]


def _render(nodes, ctx):
    out = []
    for n in nodes:
        if isinstance(n, str):
            out.append(n)
        elif n[0] == "var":
            v = _get(ctx, n[2])
            v = "" if v is None else str(v)
            out.append(v if n[1] else html.escape(v, quote=True))
        elif n[0] == "if":
            out.append(_render(n[2] if _get(ctx, n[1]) else n[3], ctx))
        elif n[0] == "each":
            for it in (_get(ctx, n[1]) or []):
                out.append(_render(n[2], ctx + [it]))
    return "".join(out)


def render(src: str, context: dict) -> str:
    return _render(_parse(src), [context])
