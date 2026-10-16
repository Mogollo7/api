# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Gráficos declarativos -> SVG con el estilo ANURA (bordes duros, sin degradados, legible en grises).

El agente solo manda {type, data}; aquí se dibuja. Portado a Python desde la lógica de graficos-datos.html (D3-free).
Distinción en escala de grises: barra destacada = negro; normal = arena con borde negro; supuesto (SIM) = rayado.
"""
from .text import esc, num

W = 360
PL, PR, PT, PB = 44, 14, 26, 36


def _wrap(label: str, n: int = 11):
    words, lines, cur = str(label).split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= n:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:3] or [""]


DEFS = (
    '<defs><pattern id="hch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
    '<rect width="6" height="6" fill="#F8F5EE"/><rect width="2.4" height="6" fill="#121212"/></pattern></defs>'
)


def _fill(it):
    if it.get("hatch"):
        return "url(#hch)"
    return "#121212" if it.get("hi") else "#EDE8D8"


def bar(data, vmax=100, unit="%", H=230):
    items = data["items"]
    w, h = W - PL - PR, H - PT - PB
    gap = w / len(items)
    bw = min(gap * 0.62, 70)
    s = [f'<svg viewBox="0 0 {W} {H}" role="img">{DEFS}']
    for t in (0, 0.5, 1):
        y = PT + h - h * t
        s.append(f'<line class="ax" x1="{PL}" x2="{W-PR}" y1="{y:.1f}" y2="{y:.1f}"/>'
                 f'<text class="mu" x="{PL-6}" y="{y+4:.1f}" text-anchor="end">{num(vmax*t, 0 if vmax>=10 else 1)}</text>')
    for i, it in enumerate(items):
        x = PL + gap * i + (gap - bw) / 2
        bh = h * it["v"] / vmax
        y = PT + h - bh
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{_fill(it)}" stroke="#121212" stroke-width="2"/>')
        top = y
        if it.get("err"):
            e = h * it["err"] / vmax
            cx = x + bw / 2
            d = f"M{cx:.1f} {y-e:.1f}V{y+e:.1f}M{cx-6:.1f} {y-e:.1f}H{cx+6:.1f}M{cx-6:.1f} {y+e:.1f}H{cx+6:.1f}"
            s.append(f'<path d="{d}" stroke="#121212" stroke-width="5" fill="none"/><path d="{d}" stroke="#D4A72C" stroke-width="2.2" fill="none"/>')
            top = y - e
        s.append(f'<text class="bold" x="{x+bw/2:.1f}" y="{top-6:.1f}" text-anchor="middle">{num(it["v"])}{unit}</text>')
        fs = 10.5 if len(items) >= 4 else 12.5
        lines = _wrap(it["l"], max(6, int(gap / (0.6 * fs))))
        for k, ln in enumerate(lines):
            s.append(f'<text class="mu" x="{x+bw/2:.1f}" y="{H-PB+14+(fs+5)*k:.1f}" text-anchor="middle" style="font-size:{fs}px">{esc(ln)}</text>')
    s.append("</svg>")
    return "".join(s)


def hbar(data, vmax=None):
    items = data["items"]
    vmax = vmax or max(i["v"] for i in items)
    rh = 26
    H = len(items) * rh + 12
    lw = 206
    s = [f'<svg viewBox="0 0 {W} {H}" role="img">{DEFS}']
    for i, it in enumerate(items):
        y = 6 + i * rh
        bw = (W - lw - 40) * it["v"] / vmax
        s.append(f'<text x="{lw-6}" y="{y+14}" text-anchor="end" style="font-size:10.5px">{esc(it["l"])}</text>'
                 f'<rect x="{lw}" y="{y+2}" width="{bw:.1f}" height="15" fill="{_fill(it)}" stroke="#121212" stroke-width="2"/>'
                 f'<text class="bold" x="{lw+bw+6:.1f}" y="{y+14}">{num(it["v"])}</text>')
    s.append("</svg>")
    return "".join(s)


def line(data, H=240):
    pts = data["points"]
    xs = [p[0] for p in pts]
    xr = data.get("xrange") or [0, max(xs) * 1.05]
    yr = data.get("yrange") or [0, 100]
    w, h = W - PL - PR, H - PT - PB - 12
    X = lambda v: PL + w * (v - xr[0]) / (xr[1] - xr[0])
    Y = lambda v: PT + h - h * (v - yr[0]) / (yr[1] - yr[0])
    s = [f'<svg viewBox="0 0 {W} {H}" role="img">']
    for k in range(5):
        v = yr[0] + (yr[1] - yr[0]) * k / 4
        y = Y(v)
        s.append(f'<line class="ax" x1="{PL}" x2="{W-PR}" y1="{y:.1f}" y2="{y:.1f}"/>'
                 f'<text class="mu" x="{PL-6}" y="{y+4:.1f}" text-anchor="end">{num(round(v))}</text>')
    d = "".join(("L" if i else "M") + f"{X(p[0]):.1f} {Y(p[1]):.1f}" for i, p in enumerate(pts))
    s.append(f'<path d="{d}" stroke="#121212" stroke-width="3" fill="none" stroke-linejoin="miter"/>')
    for p in pts:
        lab = p[2] if len(p) > 2 and p[2] != "" else num(p[0])
        s.append(f'<rect x="{X(p[0])-5:.1f}" y="{Y(p[1])-5:.1f}" width="10" height="10" fill="#D4A72C" stroke="#121212" stroke-width="2"/>'
                 f'<text class="bold" x="{X(p[0]):.1f}" y="{Y(p[1])-11:.1f}" text-anchor="middle">{num(p[1])}</text>'
                 f'<text class="mu" x="{X(p[0]):.1f}" y="{H-PB-12+16}" text-anchor="middle">{esc(lab)}</text>')
    s.append(f'<text class="mu" x="{W/2}" y="{H-4}" text-anchor="middle">{esc(data.get("xlabel",""))}</text>'
             f'<text class="mu" x="6" y="12">{esc(data.get("ylabel",""))}</text>')
    s.append("</svg>")
    return "".join(s)


STACK_FILLS = ["#121212", "#D4A72C", "#F8F5EE"]


def stack(data):
    """Barras horizontales apiladas (p. ej. pesos imagen / lugar / otros por perfil)."""
    rows, series = data["rows"], data["series"]
    rh = 34
    H = len(rows) * rh + 14
    lw = 150
    tot = data.get("total", 100)
    s = [f'<svg viewBox="0 0 {W} {H}" role="img">']
    for i, r in enumerate(rows):
        y = 6 + i * rh
        s.append(f'<text x="{lw-6}" y="{y+19}" text-anchor="end">{esc(r["l"])}</text>')
        x = lw
        for j, v in enumerate(r["v"]):
            wv = (W - lw - 8) * v / tot
            fill = STACK_FILLS[j % 3]
            tc = "#F8F5EE" if fill == "#121212" else "#121212"
            s.append(f'<rect x="{x:.1f}" y="{y+3}" width="{wv:.1f}" height="24" fill="{fill}" stroke="#121212" stroke-width="2"/>'
                     f'<text class="bold" x="{x+wv/2:.1f}" y="{y+20}" text-anchor="middle" style="fill:{tc}">{num(v)}</text>')
            x += wv
    s.append("</svg>")
    return "".join(s)


def legend(data):
    kind = data.get("legend")
    if not kind:
        return ""
    sw = {"hi": "#121212", "n": "#EDE8D8", "hatch": "url(#hch)"}
    out = []
    for lab, k in kind:
        bg = "#121212" if k == "hi" else "#EDE8D8" if k == "n" else "#D4A72C" if k == "gold" else "#F8F5EE" if k == "w" else "#EDE8D8"
        cls = ' class="sw-h"' if k == "hatch" else f' style="background:{bg}"'
        out.append(f'<span><i{cls}></i>{esc(lab)}</span>')
    return f'<div class="leg">{"".join(out)}</div>'


def draw(chart: dict) -> str:
    t = chart["type"]
    d = chart["data"]
    if t == "bar":
        return bar(d, vmax=d.get("max", 100), unit=d.get("unit", "%"))
    if t == "hbar":
        return hbar(d, vmax=d.get("max"))
    if t == "line":
        return line(d)
    if t == "stack":
        return stack(d)
    raise ValueError(f"tipo de gráfico desconocido: {t}")
