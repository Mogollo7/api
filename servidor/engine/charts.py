# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Gráficos estándar -> SVG con el estilo del diseño. El agente solo manda {type, data}; aquí se dibuja.

ANATOMÍA ESTÁNDAR (vale para todos los tipos; ver ESTANDARES.md):
  marco .ch (borde duro, fondo papel) · título (display) · etiqueta mono · área de trazado 360×H · leyenda · pie en caja.
  Ejes: línea negra, rejilla negra al 18 %, marcas en mono con el color 'hoja'. Marcas: relleno 'hoja' (serie),
  'vivo' (resalte), 'arena' (neutro), SIEMPRE con borde negro. Referencias: media = vivo continua, mediana = negro discontinua.
  Todo color sale de variables del diseño (var(--hoja)…), así que cambia con la paleta. Números con coma decimal.
  Límites: ver LIMITES. Si los datos no cumplen, el servidor devuelve una tabla en su lugar y un aviso (no rompe).
"""
import math

from .text import esc, num

W = 360
PL, PR, PT, PB = 46, 14, 26, 38
LIMITES = {"pie": 7, "bar": 14, "hbar": 20, "line": 14, "stack": 8, "hist": 40, "box": 40, "scatter": 400, "heat": 12, "map": 60}

N = "fill:var(--negro)"
S = "fill:var(--hoja)"
R = "fill:var(--vivo)"
A = "fill:var(--arena)"
C = "fill:var(--crema)"
STK = "stroke:var(--negro);stroke-width:1.6"

DEFS = (
    '<defs><pattern id="hch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
    '<rect width="6" height="6" style="fill:var(--crema)"/><rect width="2.4" height="6" style="fill:var(--negro)"/></pattern>'
    '<marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0 0L10 5L0 10z" style="fill:var(--negro)"/></marker></defs>'
)


class ChartError(ValueError):
    pass


def fmt(x, dec=None):
    if dec is None:
        dec = 0 if abs(x) >= 100 or float(x).is_integer() else (1 if abs(x) >= 10 else 2)
    t = f"{x:.{dec}f}".replace(".", ",")
    return t.replace("-", "−")


def nice_max(v):
    """Tope «redondo» del eje que NUNCA queda por debajo de v (ticks() solo devuelve marcas ≤ v)."""
    t = ticks(0, v)
    step = t[1] - t[0] if len(t) > 1 else (v or 1)
    return t[-1] if t[-1] >= v - 1e-9 else round(t[-1] + step, 10)


def ticks(lo, hi, n=5):
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / (n - 1)
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    t0 = math.ceil(lo / step - 1e-9) * step
    out, v = [], t0
    while v <= hi + 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def _wrap(label, n):
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


def _fill(it):
    if it.get("hatch"):
        return "fill:url(#hch)"
    return R if it.get("hi") else A


def _axes(xr, yr, xl, yl, H, x_is_cat=False, w=None, h=None, xt=None, yt=None, xfmt=None):
    """Ejes estándar: devuelve (svg, X, Y)."""
    w = w or (W - PL - PR)
    h = h or (H - PT - PB)
    X = lambda v: PL + w * (v - xr[0]) / ((xr[1] - xr[0]) or 1)
    Y = lambda v: PT + h - h * (v - yr[0]) / ((yr[1] - yr[0]) or 1)
    s = []
    for v in (yt if yt is not None else ticks(*yr)):
        y = Y(v)
        s.append(f'<line class="ax" x1="{PL}" x2="{W-PR}" y1="{y:.1f}" y2="{y:.1f}"/><text class="mu" x="{PL-6}" y="{y+4:.1f}" text-anchor="end">{fmt(v)}</text>')
    if not x_is_cat:
        for v in (xt if xt is not None else ticks(*xr)):
            x = X(v)
            s.append(f'<line class="ax" x1="{x:.1f}" x2="{x:.1f}" y1="{PT}" y2="{PT+h}"/><text class="mu" x="{x:.1f}" y="{PT+h+15}" text-anchor="middle">{(xfmt or fmt)(v)}</text>')
    s.append(f'<path d="M{PL} {PT}V{PT+h}H{W-PR}" style="fill:none;stroke:var(--negro);stroke-width:1.8"/>')
    if xl:
        s.append(f'<text class="mu" x="{(PL+W-PR)/2}" y="{H-5}" text-anchor="middle">{esc(xl)}</text>')
    if yl:
        s.append(f'<text class="mu" x="6" y="12">{esc(yl)}</text>')
    return "".join(s), X, Y


def _open(H):
    return f'<svg viewBox="0 0 {W} {H}" role="img">{DEFS}'


# ---------------- barras / líneas / apiladas ----------------
def bar_simple(d, roles=None, H=230):
    items = d["items"]
    mv = max((i["v"] for i in items), default=0)
    vmax = d.get("max") or (100 if mv <= 100 else nice_max(mv * 1.05))   # 100 por defecto (porcentajes) sin cortar valores mayores
    w, h = W - PL - PR, H - PT - PB
    gap = w / len(items)
    bw = min(gap * 0.62, 70)
    s = [_open(H)]
    for t in (0, 0.5, 1):
        y = PT + h - h * t
        s.append(f'<line class="ax" x1="{PL}" x2="{W-PR}" y1="{y:.1f}" y2="{y:.1f}"/><text class="mu" x="{PL-6}" y="{y+4:.1f}" text-anchor="end">{fmt(vmax*t)}</text>')
    for i, it in enumerate(items):
        x = PL + gap * i + (gap - bw) / 2
        bh = h * it["v"] / vmax
        y = PT + h - bh
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" style="{_fill(it)};{STK}"/>')
        top = y
        if it.get("err"):
            e = h * it["err"] / vmax
            cx = x + bw / 2
            p = f"M{cx:.1f} {y-e:.1f}V{y+e:.1f}M{cx-6:.1f} {y-e:.1f}H{cx+6:.1f}M{cx-6:.1f} {y+e:.1f}H{cx+6:.1f}"
            s.append(f'<path d="{p}" style="fill:none;stroke:var(--negro);stroke-width:5"/><path d="{p}" style="fill:none;stroke:var(--crema);stroke-width:2"/>')
            top = y - e
        s.append(f'<text class="bold" x="{x+bw/2:.1f}" y="{top-6:.1f}" text-anchor="middle">{fmt(it["v"])}{d.get("unit","%")}</text>')
        fs = 10.5 if len(items) >= 4 else 12.5
        for k, ln in enumerate(_wrap(it["l"], max(6, int(gap / (0.6 * fs))))):
            s.append(f'<text class="mu" x="{x+bw/2:.1f}" y="{H-PB+14+(fs+5)*k:.1f}" text-anchor="middle" style="font-size:{fs}px">{esc(ln)}</text>')
    s.append(f'<path d="M{PL} {PT}V{PT+h}H{W-PR}" style="fill:none;stroke:var(--negro);stroke-width:1.8"/></svg>')
    return "".join(s)


def hbar(d, roles=None):
    items = d["items"]
    vmax = d.get("max") or max(i["v"] for i in items)
    rh, lw = 26, 206
    H = len(items) * rh + 12
    s = [_open(H)]
    for i, it in enumerate(items):
        y = 6 + i * rh
        bw = (W - lw - 40) * it["v"] / vmax
        s.append(f'<text x="{lw-6}" y="{y+14}" text-anchor="end" style="font-size:10.5px">{esc(it["l"])}</text>'
                 f'<rect x="{lw}" y="{y+2}" width="{bw:.1f}" height="15" style="{_fill(it)};{STK}"/>'
                 f'<text class="bold" x="{lw+bw+6:.1f}" y="{y+14}">{fmt(it["v"])}</text>')
    return "".join(s) + "</svg>"


def line_simple(d, roles=None, H=240):
    pts = d["points"]
    xs = [p[0] for p in pts]
    xr = d.get("xrange") or [0, max(xs) * 1.05]
    yr = d.get("yrange") or [0, 100]
    ax, X, Y = _axes(xr, yr, d.get("xlabel", ""), d.get("ylabel", ""), H, x_is_cat=True, h=H - PT - PB - 12)
    s = [_open(H), ax]
    path = "".join(("L" if i else "M") + f"{X(p[0]):.1f} {Y(p[1]):.1f}" for i, p in enumerate(pts))
    s.append(f'<path d="{path}" style="fill:none;stroke:var(--negro);stroke-width:3"/>')
    for p in pts:
        lab = p[2] if len(p) > 2 and p[2] != "" else fmt(p[0])
        s.append(f'<rect x="{X(p[0])-5:.1f}" y="{Y(p[1])-5:.1f}" width="10" height="10" style="{R};{STK}"/>'
                 f'<text class="bold" x="{X(p[0]):.1f}" y="{Y(p[1])-11:.1f}" text-anchor="middle">{fmt(p[1])}</text>'
                 f'<text class="mu" x="{X(p[0]):.1f}" y="{H-PB-12+16}" text-anchor="middle">{esc(lab)}</text>')
    return "".join(s) + "</svg>"


def stack(d, roles=None):
    rows, tot = d["rows"], d.get("total", 100)
    rh, lw = 34, 150
    H = len(rows) * rh + 14
    fills = [(N, "var(--crema)"), (R, "var(--negro)"), (C, "var(--negro)")]
    s = [_open(H)]
    for i, r in enumerate(rows):
        y = 6 + i * rh
        s.append(f'<text x="{lw-6}" y="{y+19}" text-anchor="end">{esc(r["l"])}</text>')
        x = lw
        for j, v in enumerate(r["v"]):
            wv = (W - lw - 8) * v / tot
            f, tc = fills[j % 3]
            s.append(f'<rect x="{x:.1f}" y="{y+3}" width="{wv:.1f}" height="24" style="{f};{STK}"/>'
                     f'<text class="bold" x="{x+wv/2:.1f}" y="{y+20}" text-anchor="middle" style="fill:{tc}">{fmt(v)}</text>')
            x += wv
    return "".join(s) + "</svg>"


# ---------------- estadística: histograma, cajas, dispersión, mapa de calor ----------------
def hist(d, roles=None, H=250):
    bars = d["bars"]  # [[x, conteo], ...]
    bw = d.get("width", 0.5)
    xr = d.get("xrange") or [min(b[0] for b in bars) - bw, max(b[0] for b in bars) + bw]
    ymax = max(b[1] for b in bars)
    yr = [0, nice_max(ymax * 1.12)]
    ax, X, Y = _axes(xr, yr, d.get("xlabel", ""), d.get("ylabel", ""), H, xt=d.get("xticks"))
    s = [_open(H), ax]
    for x, c in bars:
        s.append(f'<rect x="{X(x-bw/2):.1f}" y="{Y(c):.1f}" width="{X(x+bw/2)-X(x-bw/2)-1:.1f}" height="{Y(0)-Y(c):.1f}" style="{S};{STK}"/>')
    for ln in d.get("lines", []):
        x = X(ln["x"])
        dash = "" if ln.get("style", "mean") == "mean" else "stroke-dasharray:6 4;"
        col = "var(--vivo)" if ln.get("style", "mean") == "mean" else "var(--negro)"
        s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{PT}" y2="{Y(0):.1f}" style="stroke:{col};stroke-width:2.6;{dash}"/>')
    yy = PT + 10
    for ln in d.get("lines", []):
        col = "var(--vivo)" if ln.get("style", "mean") == "mean" else "var(--negro)"
        dash = "" if ln.get("style", "mean") == "mean" else "stroke-dasharray:6 4;"
        s.append(f'<line x1="{PL+8}" x2="{PL+30}" y1="{yy-4}" y2="{yy-4}" style="stroke:{col};stroke-width:2.6;{dash}"/>'
                 f'<text x="{PL+36}" y="{yy}" style="font-size:11px">{esc(ln["label"])} {fmt(ln["x"], 2)}</text>')
        yy += 15
    return "".join(s) + "</svg>"


def box(d, roles=None):
    groups = d["groups"]
    lo = min([g["lo"] for g in groups] + [o for g in groups for o in g.get("out", [])])
    hi = max([g["hi"] for g in groups] + [o for g in groups for o in g.get("out", [])])
    xr = d.get("xrange") or [math.floor(lo) - 0.5, math.ceil(hi) + 0.5]
    n = len(groups)
    rh = 30 if n <= 6 else 17
    lw = 150 if max(len(g["l"]) for g in groups) > 4 else 20
    H = n * rh + 70
    pl = PL if lw == 20 else lw
    w = W - pl - PR
    X = lambda v: pl + w * (v - xr[0]) / (xr[1] - xr[0])
    s = [_open(H)]
    top = 12
    for v in (d.get("xticks") or ticks(*xr)):
        x = X(v)
        s.append(f'<line class="ax" x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top+n*rh}"/><text class="mu" x="{x:.1f}" y="{top+n*rh+16}" text-anchor="middle">{fmt(v)}</text>')
    s.append(f'<path d="M{pl} {top}V{top+n*rh}H{W-PR}" style="fill:none;stroke:var(--negro);stroke-width:1.8"/>')
    fs = "font-size:10.5px" if n > 6 else ""
    for i, g in enumerate(groups):
        cy = top + i * rh + rh / 2
        bh = rh * 0.62
        if lw > 20:
            s.append(f'<text x="{pl-6}" y="{cy+4:.1f}" text-anchor="end" style="{fs}">{esc(g["l"])}</text>')
        s.append(f'<path d="M{X(g["lo"]):.1f} {cy:.1f}H{X(g["q1"]):.1f}M{X(g["q3"]):.1f} {cy:.1f}H{X(g["hi"]):.1f}M{X(g["lo"]):.1f} {cy-bh/3:.1f}V{cy+bh/3:.1f}M{X(g["hi"]):.1f} {cy-bh/3:.1f}V{cy+bh/3:.1f}" style="fill:none;stroke:var(--negro);stroke-width:1.6"/>'
                 f'<rect x="{X(g["q1"]):.1f}" y="{cy-bh/2:.1f}" width="{X(g["q3"])-X(g["q1"]):.1f}" height="{bh:.1f}" style="{S};{STK}"/>'
                 f'<line x1="{X(g["med"]):.1f}" x2="{X(g["med"]):.1f}" y1="{cy-bh/2:.1f}" y2="{cy+bh/2:.1f}" style="stroke:var(--crema);stroke-width:2.6"/>')
        for o in g.get("out", []):
            s.append(f'<circle cx="{X(o):.1f}" cy="{cy:.1f}" r="{4 if n<=6 else 3}" style="{R};{STK}"/>')
    s.append(f'<text class="mu" x="{(pl+W-PR)/2}" y="{H-6}" text-anchor="middle">{esc(d.get("xlabel",""))}</text>')
    return "".join(s) + "</svg>"


def _ols(pts):
    n = len(pts)
    mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    syy = sum((p[1] - my) ** 2 for p in pts)
    b = sxy / sxx
    return b, my - b * mx, sxy / math.sqrt(sxx * syy)


def scatter(d, roles=None, H=250):
    pts = d["points"]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    xr = d.get("xrange") or [min(xs), max(xs)]
    yr = d.get("yrange") or [min(ys), max(ys)]
    ax, X, Y = _axes(xr, yr, d.get("xlabel", ""), d.get("ylabel", ""), H, xt=d.get("xticks"), yt=d.get("yticks"))
    s = [_open(H), ax]
    for x, y in pts:
        s.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3.4" style="fill:var(--hoja);fill-opacity:.7;stroke:var(--negro);stroke-width:.8"/>')
    tr = d.get("trend")
    if tr:
        if tr == "auto" or tr is True:
            b, a, r = _ols(pts)
            tr = {"slope": b, "intercept": a, "label": f"Tendencia lineal (r = {fmt(r, 2)})"}
        y0, y1 = tr["intercept"] + tr["slope"] * xr[0], tr["intercept"] + tr["slope"] * xr[1]
        s.append(f'<line x1="{X(xr[0]):.1f}" y1="{Y(y0):.1f}" x2="{X(xr[1]):.1f}" y2="{Y(y1):.1f}" style="stroke:var(--vivo);stroke-width:3.2"/>'
                 f'<line x1="{PL+8}" x2="{PL+34}" y1="{H-PB-22}" y2="{H-PB-22}" style="stroke:var(--vivo);stroke-width:3.2"/>'
                 f'<text x="{PL+40}" y="{H-PB-18}" style="font-size:11px">{esc(tr.get("label","Tendencia"))}</text>')
    return "".join(s) + "</svg>"


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _lum(c):
    f = lambda v: (v / 255 / 12.92) if v / 255 <= 0.03928 else ((v / 255 + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def heat(d, roles, H=None):
    labs, M = d["labels"], d["matrix"]
    n = len(labs)
    lo, hi = d.get("range", [-1, 1])
    neg, mid, pos = _hex(roles["hoja"]), _hex(roles["crema"]), _hex(roles["vivo"])
    cell = 38 if n <= 7 else 28
    pl, pt = 96, 8
    Wd = pl + n * cell + 8
    H = pt + n * cell + 62
    s = [f'<svg viewBox="0 0 {Wd} {H}" role="img">{DEFS}']
    for i in range(n):
        s.append(f'<text x="{pl-6}" y="{pt+i*cell+cell/2+4:.1f}" text-anchor="end" style="font-size:10.5px">{esc(labs[i])}</text>')
        s.append(f'<text x="{pl+i*cell+cell/2:.1f}" y="{pt+n*cell+14}" text-anchor="end" transform="rotate(-45 {pl+i*cell+cell/2:.1f} {pt+n*cell+14})" style="font-size:9.5px">{esc(labs[i])}</text>')
        for j in range(n):
            v = M[i][j]
            t = (v - lo) / (hi - lo) * 2 - 1
            col = _mix(mid, pos, t) if t >= 0 else _mix(mid, neg, -t)
            tc = "#030B18" if _lum(col) > 0.28 else "#FFFFFF"
            s.append(f'<rect x="{pl+j*cell}" y="{pt+i*cell}" width="{cell}" height="{cell}" style="fill:rgb{col};stroke:var(--negro);stroke-width:1.2"/>'
                     f'<text class="bold" x="{pl+j*cell+cell/2:.1f}" y="{pt+i*cell+cell/2+4:.1f}" text-anchor="middle" style="fill:{tc};font-size:{10 if n<=7 else 8.5}px">{fmt(v, 2)}</text>')
    return "".join(s) + "</svg>"


# ---------------- mapa estándar ----------------
def geo_map(d, roles=None, outlines=None, H=None):
    outline = d.get("outline")
    if isinstance(outline, str):
        outline = (outlines or {}).get(outline)
        if outline is None:
            raise ChartError(f"contorno '{d.get('outline')}' no existe")
    pts = d.get("points", [])
    polys = outline or []
    lons = [p[0] for poly in polys for p in poly] + [p["lon"] for p in pts]
    lats = [p[1] for poly in polys for p in poly] + [p["lat"] for p in pts]
    if not lons:
        raise ChartError("mapa sin contorno ni puntos")
    x0, x1, y0, y1 = min(lons) - 0.5, max(lons) + 0.5, min(lats) - 0.5, max(lats) + 0.5
    k = math.cos(math.radians((y0 + y1) / 2))
    wd, ht = (x1 - x0) * k, (y1 - y0)
    scale = min(300 / wd, 215 / ht)
    Wm = wd * scale
    Hm = ht * scale
    H = Hm + 40
    ox, oy = 30 + (300 - Wm) / 2, 14
    X = lambda lon: ox + (lon - x0) * k * scale
    Y = lambda lat: oy + (y1 - lat) * scale
    s = [f'<svg viewBox="0 0 {W} {H:.0f}" role="img">{DEFS}']
    step = d.get("graticule", 2)
    if step:
        g = math.ceil(x0 / step) * step
        while g <= x1:
            s.append(f'<line class="ax" x1="{X(g):.1f}" x2="{X(g):.1f}" y1="{oy}" y2="{oy+Hm:.1f}"/><text class="mu" x="{X(g):.1f}" y="{oy+Hm+14:.1f}" text-anchor="middle" style="font-size:9.5px">{fmt(g)}°</text>')
            g += step
        g = math.ceil(y0 / step) * step
        while g <= y1:
            s.append(f'<line class="ax" x1="{ox}" x2="{ox+Wm:.1f}" y1="{Y(g):.1f}" y2="{Y(g):.1f}"/><text class="mu" x="{ox-4}" y="{Y(g)+3:.1f}" text-anchor="end" style="font-size:9.5px">{fmt(g)}°</text>')
            g += step
    for poly in polys:
        p = "".join(("L" if i else "M") + f"{X(a):.1f} {Y(b):.1f}" for i, (a, b) in enumerate(poly)) + "Z"
        s.append(f'<path d="{p}" style="{A};stroke:var(--negro);stroke-width:2;stroke-linejoin:miter"/>')
    vmax = max([p.get("v", 1) for p in pts] or [1])
    placed = []
    for i, p in enumerate(pts):
        r = 3 + 4.5 * (p.get("v", 1) / vmax) ** 0.5 if d.get("size") else 5
        s.append(f'<rect x="{X(p["lon"])-r:.1f}" y="{Y(p["lat"])-r:.1f}" width="{2*r:.1f}" height="{2*r:.1f}" style="{R};{STK}"/>')
        lab = p.get("label")
        if lab and len(pts) <= 14:
            wl = 6.4 * len(str(lab))
            hit = lambda x, y, an: any(abs(y - by_) < 12 and (x < bx + bw and x + wl > bx if an == "start" else x - wl < bx + bw and x > bx) for bx, by_, bw in placed)
            bx0, by0 = X(p["lon"]), Y(p["lat"]) + 4
            cands = [(bx0 + r + 3, by0, "start"), (bx0 - r - 3, by0, "end"), (bx0 + r + 3, by0 + 12, "start"), (bx0 - r - 3, by0 + 12, "end"), (bx0 + r + 3, by0 - 12, "start")]
            lx, ly, anc = next(((x, y, an) for x, y, an in cands if not hit(x, y, an) and (x + wl <= 358 if an == "start" else x - wl >= 2)), cands[0])
            placed.append((lx if anc == "start" else lx - wl, ly, wl))
            s.append(f'<text class="bold" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anc}" style="font-size:10.5px">{esc(lab)}</text>')
    s.append(f'<rect x="{ox}" y="{oy}" width="{Wm:.1f}" height="{Hm:.1f}" style="fill:none;stroke:var(--negro);stroke-width:1.8"/>')
    # norte y escala gráfica
    s.append(f'<path d="M{W-24} {oy+30}V{oy+6}M{W-24} {oy+6}l-5 9M{W-24} {oy+6}l5 9" style="fill:none;stroke:var(--negro);stroke-width:2"/><text class="bold" x="{W-24}" y="{oy+42}" text-anchor="middle">N</text>')
    return "".join(s) + "</svg>"


SERIES = ["fill:var(--hoja)", "fill:var(--vivo)", "fill:var(--negro)", "fill:var(--arena)", "fill:url(#hch)"]
SKEYS = ["s", "hi", "k", "n", "hatch"]
SERIES_TXT = ["var(--crema)", "var(--negro)", "var(--crema)", "var(--negro)", "var(--negro)"]


def auto_legend(ch):
    """Leyenda automática para gráficos de varias series o de pastel."""
    d = ch.get("data", {})
    if ch.get("type") in ("bar", "line") and d.get("series"):
        return [(sr.get("name", f"Serie {i+1}"), SKEYS[i % 5]) for i, sr in enumerate(d["series"])]
    return None


def bar(d, roles=None, H=230):
    if not d.get("series"):
        return bar_simple(d, roles, H)
    cats, ser = d["categories"], d["series"]
    stacked = d.get("mode") == "stacked"
    n, m = len(cats), len(ser)
    tot = [sum(sr["values"][i] for sr in ser) for i in range(n)]
    vmax = d.get("max") or nice_max(max(tot) if stacked else max(v for sr in ser for v in sr["values"]) * 1.1)
    w, h = W - PL - PR, H - PT - PB
    gap = w / n
    gw = gap * 0.74
    ax, X, Y = _axes([0, n], [0, vmax], "", d.get("ylabel", ""), H, x_is_cat=True, w=w, h=h)
    s = [_open(H), ax]
    for i in range(n):
        x0 = PL + gap * i + (gap - gw) / 2
        base = 0
        for j, sr in enumerate(ser):
            v = sr["values"][i]
            if stacked:
                y1, y0 = Y(base + v), Y(base)
                bx, bw = x0, gw
                base += v
            else:
                bw = gw / m
                bx = x0 + bw * j
                y1, y0 = Y(v), Y(0)
            s.append(f'<rect x="{bx:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{y0-y1:.1f}" style="{SERIES[j % 5]};{STK}"/>')
            if not stacked and m <= 3 and bw > 16:
                s.append(f'<text class="bold" x="{bx+bw/2:.1f}" y="{y1-4:.1f}" text-anchor="middle" style="font-size:10px">{fmt(v)}</text>')
        fs = 10.5 if n >= 5 else 12
        for k, ln in enumerate(_wrap(cats[i], max(5, int(gap / (0.6 * fs))))):
            s.append(f'<text class="mu" x="{PL+gap*i+gap/2:.1f}" y="{H-PB+14+(fs+5)*k:.1f}" text-anchor="middle" style="font-size:{fs}px">{esc(ln)}</text>')
    return "".join(s) + "</svg>"


def line(d, roles=None, H=240):
    series = d.get("series")
    pts0 = d.get("points")
    if not series:
        if pts0 and any(isinstance(p[0], str) for p in pts0):
            series = [{"name": "", "points": pts0}]
        else:
            return line_simple(d, roles, H)
    # eje x categórico (texto o fechas ISO) o numérico
    allx = [p[0] for sr in series for p in sr["points"]]
    cat = any(isinstance(x, str) for x in allx)
    xs = sorted(set(allx)) if cat else None
    if cat:
        xr = [0, max(len(xs) - 1, 1)]
        pos = lambda x: xs.index(x)
    else:
        xr = d.get("xrange") or [min(allx), max(allx)]
        pos = lambda x: x
    ally = [p[1] for sr in series for p in sr["points"]]
    yr = d.get("yrange") or [min(0, min(ally)), nice_max(max(ally) * 1.08)]
    ax, X, Y = _axes(xr, yr, d.get("xlabel", ""), d.get("ylabel", ""), H, x_is_cat=cat, h=H - PT - PB - 12)
    s = [_open(H), ax]
    if cat:
        step = max(1, len(xs) // 7)
        for i, x in enumerate(xs):
            if i % step == 0:
                s.append(f'<text class="mu" x="{X(i):.1f}" y="{H-PB-12+19}" text-anchor="middle" style="font-size:10.5px">{esc(x)}</text>')
    for j, sr in enumerate(series):
        col = ["var(--hoja)", "var(--vivo)", "var(--negro)", "var(--arena)", "var(--negro)"][j % 5]
        dash = "stroke-dasharray:7 4;" if j % 5 == 4 else ""
        path = "".join(("L" if i else "M") + f"{X(pos(p[0])):.1f} {Y(p[1]):.1f}" for i, p in enumerate(sr["points"]))
        s.append(f'<path d="{path}" style="fill:none;stroke:var(--negro);stroke-width:5.2"/><path d="{path}" style="fill:none;stroke:{col};stroke-width:2.6;{dash}"/>')
        for p in sr["points"]:
            s.append(f'<rect x="{X(pos(p[0]))-4:.1f}" y="{Y(p[1])-4:.1f}" width="8" height="8" style="{SERIES[j % 5]};{STK}"/>')
        if len(series) == 1:
            for p in sr["points"]:
                s.append(f'<text class="bold" x="{X(pos(p[0])):.1f}" y="{Y(p[1])-9:.1f}" text-anchor="middle" style="font-size:10px">{fmt(p[1])}</text>')
    return "".join(s) + "</svg>"


def pie(d, roles=None):
    items = d["items"]
    tot = sum(i["v"] for i in items)
    cx, cy, r = 105, 108, 88
    ri = 48 if d.get("donut") else 0
    H = 216
    s = [_open(H)]
    a0 = -math.pi / 2
    for k, it in enumerate(items):
        frac = it["v"] / tot
        a1 = a0 + frac * 2 * math.pi
        large = 1 if a1 - a0 > math.pi else 0
        x0, y0, x1, y1 = cx + r * math.cos(a0), cy + r * math.sin(a0), cx + r * math.cos(a1), cy + r * math.sin(a1)
        if ri:
            xi1, yi1, xi0, yi0 = cx + ri * math.cos(a1), cy + ri * math.sin(a1), cx + ri * math.cos(a0), cy + ri * math.sin(a0)
            path = f"M{x0:.1f} {y0:.1f}A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}L{xi1:.1f} {yi1:.1f}A{ri} {ri} 0 {large} 0 {xi0:.1f} {yi0:.1f}Z"
        else:
            path = f"M{cx} {cy}L{x0:.1f} {y0:.1f}A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}Z" if frac < 0.999 else f"M{cx-r} {cy}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0Z"
        s.append(f'<path d="{path}" style="{SERIES[k % 5]};stroke:var(--negro);stroke-width:2;stroke-linejoin:miter"/>')
        if frac >= 0.09:
            am = (a0 + a1) / 2
            rr = (r + ri) / 2 if ri else r * 0.62
            s.append(f'<text class="bold" x="{cx+rr*math.cos(am):.1f}" y="{cy+rr*math.sin(am)+4:.1f}" text-anchor="middle" style="fill:{SERIES_TXT[k % 5]};font-size:11px">{fmt(frac*100, 0)} %</text>')
        a0 = a1
    for k, it in enumerate(items):
        y = 24 + k * 24
        s.append(f'<rect x="218" y="{y-10}" width="14" height="14" style="{SERIES[k % 5]};{STK}"/><text x="238" y="{y+2}" style="font-size:11px">{esc(str(it["l"])[:20])}</text>')
    return "".join(s) + "</svg>"


def legend(ch):
    kind = ch.get("legend") or auto_legend(ch)
    if not kind:
        return ""
    out = []
    for lab, k in kind:
        cls = {"hi": "background:var(--vivo)", "n": "background:var(--arena)", "s": "background:var(--hoja)", "k": "background:var(--negro)", "w": "background:var(--crema)"}.get(k)
        c = ' class="sw-h"' if k == "hatch" else f' style="{cls or "background:var(--arena)"}"'
        out.append(f'<span><i{c}></i>{esc(lab)}</span>')
    return f'<div class="leg">{"".join(out)}</div>'


def _check(t, d):
    lim = LIMITES.get(t)
    n = {"pie": len(d.get("items", [])), "bar": len(d.get("items", [])) or len(d.get("categories", [])), "hbar": len(d.get("items", [])), "line": len(d.get("points", [])) or max([len(sr.get("points", [])) for sr in d.get("series", []) if isinstance(sr, dict)] or [0]), "stack": len(d.get("rows", [])),
         "hist": len(d.get("bars", [])), "box": len(d.get("groups", [])), "scatter": len(d.get("points", [])),
         "heat": len(d.get("labels", [])), "map": len(d.get("points", []))}.get(t, 0)
    if n == 0:
        raise ChartError("sin datos")
    if lim and n > lim:
        raise ChartError(f"{n} elementos y el estándar admite {lim}")


def draw(ch: dict, roles: dict, outlines=None) -> str:
    t, d = ch["type"], ch["data"]
    if t not in LIMITES:
        raise ChartError(f"tipo de gráfico '{t}' no es estándar")
    _check(t, d)
    f = {"pie": pie, "bar": bar, "hbar": hbar, "line": line, "stack": stack, "hist": hist, "box": box, "scatter": scatter, "heat": heat}
    if t == "map":
        return geo_map(d, roles, outlines)
    return f[t](d, roles)
