# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Texto en línea: el agente escribe texto plano con marcas mínimas; el servidor lo convierte en HTML saneado.

Marcas aceptadas:  **negrita**   *cursiva* (nombres científicos)   [FUENTE] [INF] [SIN FUENTE] [CALC] [SIM]
y la expresión «dato pendiente», que el servidor resalta sola. Cualquier HTML escrito por el agente se escapa.
"""
import html
import re

_TAGS = {
    "FUENTE": ("f", "FUENTE"),
    "CALC": ("c", "CALC"),
    "INF": ("i", "INF"),
    "SIN FUENTE": ("s", "SIN FUENTE"),
    "SIM": ("m", "SIMULACIÓN"),
    "SIMULACIÓN": ("m", "SIMULACIÓN"),
    "RESUMEN": ("i", "RESUMEN"),
    "BD": ("c", "BD"),
    "STAT": ("c", "STAT"),
    "DOC": ("i", "DOC"),
    "HIST": ("i", "HIST"),
}


def inline(s: str) -> str:
    s = html.escape(str(s), quote=False)
    s = re.sub(r"\[\^(\w{1,3})\]", r'<sup class="fn">\1</sup>', s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)

    def chip(m):
        key = m.group(1).strip()
        if key in _TAGS:
            cls, label = _TAGS[key]
            return f'<span class="et {cls}">{label}</span>'
        return m.group(0)

    s = re.sub(r"\[([A-ZÁÉÍÓÚ ]{2,14})\]", chip, s)
    s = re.sub(r"(dato pendiente)", r'<span class="pend">\1</span>', s, flags=re.I)
    return s


def plain(s: str) -> str:
    """Texto sin marcas (para índices, créditos, atributos)."""
    s = re.sub(r"\[\^\w{1,3}\]", "", str(s))
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", s)
    return re.sub(r"\[[A-ZÁÉÍÓÚ ]{2,14}\]", "", s).strip()


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def num(x, dec=None) -> str:
    """Formato español: coma decimal."""
    if dec is not None:
        t = f"{x:.{dec}f}"
    else:
        t = f"{x:g}"
    return t.replace(".", ",")
