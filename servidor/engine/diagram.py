# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Diagrama de flujo estándar (bloque `flowchart`): nodos y aristas -> SVG por capas, de arriba abajo.

ESTÁNDAR: tipos de nodo start / process / decision / io / end; ≤ 14 nodos; ≤ 3 columnas por capa; una decisión tiene 2–3 salidas
con etiqueta («sí» / «no»). Rectángulos de borde duro (radio 0), rombo para decisión, caja de doble borde para inicio y fin,
paralelogramo para entrada/salida. Flechas ortogonales negras. Si el grafo no cumple, el servidor lo degrada a lista numerada.
"""
from .text import esc

W = 360
BW, BH, DW, DH, GX, GY = 104, 40, 118, 62, 10, 30


class DiagramError(ValueError):
    pass


def _wrap(t, n=15):
    out, cur = [], ""
    for w in str(t).split():
        if len(cur) + len(w) + (1 if cur else 0) <= n:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out[:4] or [""]


def layout(nodes, edges):
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)):
        raise DiagramError("ids de nodo repetidos")
    if len(nodes) > 14:
        raise DiagramError(f"{len(nodes)} nodos y el estándar admite 14")
    for e in edges:
        if e["from"] not in ids or e["to"] not in ids:
            raise DiagramError(f"arista con nodo inexistente: {e['from']}→{e['to']}")
    succ = {i: [] for i in ids}
    for e in edges:
        succ[e["from"]].append(e["to"])
    # capa = camino más largo desde la raíz, ignorando aristas que cierran ciclos (DFS)
    state, back = {}, set()

    def dfs(u):
        state[u] = 1
        for v in succ[u]:
            if state.get(v) == 1:
                back.add((u, v))
            elif v not in state:
                dfs(v)
        state[u] = 2

    roots = [i for i in ids if not any(e["to"] == i for e in edges)] or [ids[0]]
    for r in roots:
        if r not in state:
            dfs(r)
    for i in ids:
        if i not in state:
            dfs(i)
    rank = {i: 0 for i in ids}
    for _ in range(len(ids)):
        for e in edges:
            if (e["from"], e["to"]) in back:
                continue
            rank[e["to"]] = max(rank[e["to"]], rank[e["from"]] + 1)
    layers = {}
    for i in ids:
        layers.setdefault(rank[i], []).append(i)
    if max(len(v) for v in layers.values()) > 3:
        raise DiagramError("más de 3 nodos en una misma capa")
    return rank, layers, back


def draw(d):
    nodes, edges = d["nodes"], d.get("edges", [])
    rank, layers, back = layout(nodes, edges)
    by = {n["id"]: n for n in nodes}
    nl = max(layers) + 1
    pos = {}
    y = 14
    ys = {}
    for r in range(nl):
        hmax = max(DH if by[i].get("kind") == "decision" else BH for i in layers[r])
        ys[r] = (y, hmax)
        y += hmax + GY
    H = y - GY + 14
    colw = (W - 20) / 3
    for r, ids in layers.items():
        k = len(ids)
        for j, i in enumerate(ids):
            cx = 10 + colw * (1 + j) - colw / 2 if k == 3 else (W / 2 if k == 1 else W / 2 + (j - 0.5) * (colw + 20))
            pos[i] = (cx, ys[r][0] + ys[r][1] / 2)
    s = [f'<svg viewBox="0 0 {W} {H:.0f}" role="img"><defs><marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" style="fill:var(--negro)"/></marker></defs>']
    edge_svg, label_svg = [], []
    for e in edges:
        a, b = pos[e["from"]], pos[e["to"]]
        ha = (DH if by[e["from"]].get("kind") == "decision" else BH) / 2
        hb = (DH if by[e["to"]].get("kind") == "decision" else BH) / 2
        if (e["from"], e["to"]) in back or rank[e["to"]] <= rank[e["from"]]:
            x = max(a[0], b[0]) + (DW / 2 + 12)
            p = f"M{a[0]+ (DW/2 if by[e['from']].get('kind')=='decision' else BW/2):.1f} {a[1]:.1f}H{x:.1f}V{b[1]:.1f}H{b[0]+(DW/2 if by[e['to']].get('kind')=='decision' else BW/2)+2:.1f}"
            lx, ly = x + 3, (a[1] + b[1]) / 2
        else:
            y0, y1 = a[1] + ha, b[1] - hb
            ym = y0 + (y1 - y0) / 2
            p = f"M{a[0]:.1f} {y0:.1f}V{ym:.1f}H{b[0]:.1f}V{y1-1:.1f}" if abs(a[0] - b[0]) > 1 else f"M{a[0]:.1f} {y0:.1f}V{y1-1:.1f}"
            lx, ly = (a[0] + b[0]) / 2 + 4, ym - 3 if abs(a[0] - b[0]) > 1 else y0 + 12
        edge_svg.append(f'<path d="{p}" style="fill:none;stroke:var(--negro);stroke-width:2" marker-end="url(#arw)"/>')
        if e.get("label"):
            label_svg.append(f'<rect x="{lx-2:.1f}" y="{ly-10:.1f}" width="{8+7*len(e["label"]):.0f}" height="14" style="fill:var(--crema)"/><text class="bold" x="{lx:.1f}" y="{ly:.1f}" style="font-size:10.5px">{esc(e["label"])}</text>')
    s += edge_svg
    for n in nodes:
        cx, cy = pos[n["id"]]
        k = n.get("kind", "process")
        lines = _wrap(n["label"], 13 if k == "decision" else 15)
        txt = "".join(f'<text x="{cx:.1f}" y="{cy - (len(lines)-1)*6.5 + i*13 + 4:.1f}" text-anchor="middle" style="font-size:10.5px;{"fill:var(--crema)" if k in ("start","end") else ""}">{esc(l)}</text>' for i, l in enumerate(lines))
        if k == "decision":
            pts = f"{cx:.1f},{cy-DH/2:.1f} {cx+DW/2:.1f},{cy:.1f} {cx:.1f},{cy+DH/2:.1f} {cx-DW/2:.1f},{cy:.1f}"
            s.append(f'<polygon points="{pts}" style="fill:var(--vivo);stroke:var(--negro);stroke-width:2"/>{txt}')
        elif k in ("start", "end"):
            s.append(f'<rect x="{cx-BW/2:.1f}" y="{cy-BH/2:.1f}" width="{BW}" height="{BH}" style="fill:var(--negro);stroke:var(--negro);stroke-width:2"/>'
                     f'<rect x="{cx-BW/2+3:.1f}" y="{cy-BH/2+3:.1f}" width="{BW-6}" height="{BH-6}" style="fill:none;stroke:var(--crema);stroke-width:1.2"/>{txt}')
        elif k == "io":
            sk = 10
            pts = f"{cx-BW/2+sk:.1f},{cy-BH/2:.1f} {cx+BW/2:.1f},{cy-BH/2:.1f} {cx+BW/2-sk:.1f},{cy+BH/2:.1f} {cx-BW/2:.1f},{cy+BH/2:.1f}"
            s.append(f'<polygon points="{pts}" style="fill:var(--arena);stroke:var(--negro);stroke-width:2"/>{txt}')
        else:
            s.append(f'<rect x="{cx-BW/2:.1f}" y="{cy-BH/2:.1f}" width="{BW}" height="{BH}" style="fill:var(--arena);stroke:var(--negro);stroke-width:2"/>{txt}')
    s += label_svg
    return "".join(s) + "</svg>"
