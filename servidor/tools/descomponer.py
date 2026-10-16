#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor. Descompone una imagen de referencia en ÁTOMOS.
"""Parte una imagen de referencia (cartel, portada, captura) en piezas y dice dónde está cada una.

    python servidor/tools/descomponer.py referencia.jpg [-o ref/nombre]

Salida en ref/<nombre>/:
  atomos.json      kind (titular | texto | bloque | foto | simbolo | regla | codigo), caja en cqw (x,y,w,h = % del ancho),
                   zona (tercio vertical/horizontal), alineación, colores, tamaño de letra estimado
  guias.md         lectura corta: paleta, márgenes, ejes de alineación, jerarquía de tamaños, cómo se centra cada cosa
  anotada.png      la imagen con cada átomo numerado (una sola imagen para verificar)
  recortes/        un PNG por átomo; simbolos y reglas además en SVG vectorial (potrace, color = currentColor)
Heurística, no OCR: separa por color, textura y forma. Revisa anotada.png antes de fiarte de un átomo.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

try:
    import potrace
except Exception:  # noqa: BLE001
    potrace = None


def palette(im, n=8):
    q = im.quantize(colors=n, method=Image.MEDIANCUT)
    pal = q.getpalette()[: 3 * n]
    arr = np.asarray(q)
    out = []
    for i in range(n):
        m = (arr == i).mean()
        if m > 0.004:
            out.append(("#%02x%02x%02x" % tuple(pal[3 * i:3 * i + 3]), round(100 * m, 1), i))
    return sorted(out, key=lambda t: -t[1]), arr


def vectorize(mask, path):
    if potrace is None or mask.sum() < 20:
        return False
    big = np.kron(mask, np.ones((3, 3), bool))
    pa = potrace.Bitmap(big).trace(turdsize=6, alphamax=1.0, opticurve=True, opttolerance=0.3)
    d = []
    f = lambda p: f"{p.x / 3:.2f} {p.y / 3:.2f}"
    for c in pa:
        d.append("M" + f(c.start_point))
        for s in c.segments:
            d.append(("L" + f(s.c) + " L" + f(s.end_point)) if s.is_corner else ("C" + f(s.c1) + " " + f(s.c2) + " " + f(s.end_point)))
        d.append("Z")
    h, w = mask.shape
    Path(path).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path fill="currentColor" fill-rule="evenodd" d="{"".join(d)}"/></svg>')
    return True


def zone(cx, cy, W, H):
    v = "arriba" if cy < H / 3 else ("centro" if cy < 2 * H / 3 else "abajo")
    h = "izquierda" if cx < W / 3 else ("centro" if cx < 2 * W / 3 else "derecha")
    return f"{v}-{h}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imagen")
    ap.add_argument("-o", "--out")
    ap.add_argument("--min", type=float, default=0.0006, help="área mínima de un átomo, fracción de la hoja")
    a = ap.parse_args()
    src = Path(a.imagen)
    out = Path(a.out or f"ref/{src.stem}")
    (out / "recortes").mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > 1100:
        im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
    W, H = im.size
    cq = 100 / W
    arr = np.asarray(im).astype(float)
    gray = arr @ np.array([0.2126, 0.7152, 0.0722])
    pal, idx = palette(im)
    bg_hex = pal[0][0]
    # sustrato: papel (el color más claro frecuente) o fondo dominante
    atoms = []

    def add(kind, mask, extra=None):
        ys, xs = np.where(mask)
        if len(xs) == 0:
            return
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        reg = arr[y0:y1, x0:x1][mask[y0:y1, x0:x1]]
        col = "#%02x%02x%02x" % tuple(np.median(reg, axis=0).astype(int))
        box = {"x": round(x0 * cq, 1), "y": round(y0 * cq, 1), "w": round((x1 - x0) * cq, 1), "h": round((y1 - y0) * cq, 1)}
        cx = (x0 + x1) / 2
        al = "centro" if abs(cx - W / 2) < W * 0.04 else ("izq" if x0 < W * 0.12 else ("der" if x1 > W * 0.88 else "libre"))
        d = {"id": len(atoms) + 1, "kind": kind, "caja_cqw": box, "zona": zone(cx, (y0 + y1) / 2, W, H), "alinea": al, "color": col, "_px": (int(x0), int(y0), int(x1), int(y1))}
        if extra:
            d.update(extra)
        atoms.append(d)

    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
    red = (R > 140) & (G < 90) & (B < 90)
    dark = gray < 85
    taken = np.zeros((H, W), bool)

    def comps(mask, minarea):
        lab, n = ndi.label(mask)
        for k, sl in enumerate(ndi.find_objects(lab), 1):
            comp = lab[sl] == k
            if comp.sum() >= minarea:
                full = np.zeros((H, W), bool)
                full[sl] = comp
                yield sl, comp, full

    # A) bloques de color de acento (rojo, etc.): componentes grandes y llenos
    for sl, comp, full in comps(ndi.binary_closing(ndi.binary_opening(red, iterations=2), iterations=8), 0.012 * W * H):
        h, w = comp.shape
        if comp.sum() / (w * h) > 0.55:
            m = np.zeros((H, W), bool)
            m[sl] = True
            add("bloque", m, {"relleno": "#%02x%02x%02x" % tuple(np.median(arr[sl][comp], axis=0).astype(int))})
            taken |= m
    # B) foto: bloques de 16 px con muchos tonos medios
    bs = 16
    mid = ((gray > 70) & (gray < 190)).astype(float)
    pm = ndi.uniform_filter(mid, bs)
    sd = ndi.uniform_filter(gray, bs)
    sd = np.sqrt(np.maximum(ndi.uniform_filter(gray ** 2, bs) - sd ** 2, 0))
    ph = (pm > 0.42) & (sd > 40) & ~taken
    ph = ndi.binary_closing(ndi.binary_opening(ph, iterations=6), iterations=10)
    for sl, comp, full in comps(ph, 0.05 * W * H):
        h, w = comp.shape
        m = np.zeros((H, W), bool)
        m[sl] = True
        add("foto", m, {"tonos": "muchos"})
        taken |= m
    # C) bloques oscuros llenos (cajas negras, barras)
    solid = ndi.binary_opening(dark & ~taken, iterations=5)
    for sl, comp, full in comps(solid, 0.006 * W * H):
        h, w = comp.shape
        if comp.sum() / (w * h) > 0.88 and (w * h) > 0.01 * W * H and w > 0.12 * W and h < 0.2 * H and not (h > 0.15 * H and w < 0.3 * W):
            m = np.zeros((H, W), bool)
            m[sl] = True
            add("bloque", m, {"relleno": "oscuro"})
            taken |= m
    # D) titulares gigantes: letras oscuras muy altas, unidas por filas
    ink = (dark | red) & ~taken
    ink = ndi.binary_opening(ink, iterations=1)
    giant = ndi.binary_opening(ink, iterations=10)
    rows = ndi.binary_dilation(giant, structure=np.ones((3, 5)), iterations=int(0.03 * W / 2) + 2)
    for sl, comp, full in comps(rows, 0.012 * W * H):
        h, w = comp.shape
        if h > 0.05 * H:
            m = np.zeros((H, W), bool)
            m[sl] = True
            add("titular", m & (giant | ink), {"altura_letra_cqw": round(h * cq, 1)})
            taken |= m & ndi.binary_dilation(giant, iterations=6)
    # E) texto pequeño, símbolos, reglas y códigos sobre el papel
    ink2 = ink & ~taken
    merged = ndi.binary_dilation(ink2, structure=np.ones((3, 7)), iterations=3)
    lab, n = ndi.label(merged)
    for k, sl in enumerate(ndi.find_objects(lab), 1):
        comp = (lab[sl] == k) & ink2[sl]
        h, w = comp.shape
        if comp.sum() < a.min * W * H or max(h, w) < 0.012 * W:
            continue
        full = np.zeros((H, W), bool)
        full[sl] = comp
        dens = comp.sum() / (w * h)
        aspect = w / h
        if aspect > 8 and h < 0.012 * H * 2:
            add("regla", full)
        elif w < 0.09 * W and h < 0.09 * H and (aspect < 2.2) and dens > 0.1:
            add("simbolo", full)
        elif aspect < 1.6 and h > 0.025 * H and dens > 0.35 and w > 0.08 * W:
            add("codigo", full)
        else:
            add("texto", full, {"altura_letra_cqw": round(h * cq, 1)})
    # numerar, recortar, vectorizar
    ann = im.copy()
    dr = ImageDraw.Draw(ann)
    cols = {"titular": "#ffcc00", "texto": "#00aa00", "bloque": "#ff0000", "foto": "#ff00ff", "simbolo": "#0066ff", "regla": "#ff8800", "codigo": "#00cccc", "trama": "#888888"}
    for t in atoms:
        x0, y0, x1, y1 = t.pop("_px")
        crop = im.crop((x0, y0, x1, y1))
        name = f"{t['id']:02d}_{t['kind']}"
        crop.save(out / "recortes" / f"{name}.png")
        if t["kind"] in ("simbolo", "regla", "texto", "codigo", "titular") and potrace:
            g = np.asarray(crop.convert("L")).astype(float)
            dark_bg = g.mean() > 128
            mask = g < g.mean() - 20 if dark_bg else g > g.mean() + 20
            if vectorize(mask, out / "recortes" / f"{name}.svg"):
                t["svg"] = f"recortes/{name}.svg"
        dr.rectangle((x0, y0, x1, y1), outline=cols.get(t["kind"], "#000"), width=3)
        dr.rectangle((x0, y0, x0 + 26, y0 + 16), fill=cols.get(t["kind"], "#000"))
        dr.text((x0 + 3, y0 + 2), str(t["id"]), fill="white")
    ann.save(out / "anotada.png", optimize=True)
    # contenedores: los bloques de color continuo y las fotos son contenedores; texto y símbolos pertenecen al que los contiene (o al papel)
    conts = [t for t in atoms if t["kind"] in ("bloque", "foto")]
    inside = lambda c, a: (c["caja_cqw"]["x"] - 0.5 <= a["caja_cqw"]["x"] + a["caja_cqw"]["w"] / 2 <= c["caja_cqw"]["x"] + c["caja_cqw"]["w"] + 0.5
                           and c["caja_cqw"]["y"] - 0.5 <= a["caja_cqw"]["y"] + a["caja_cqw"]["h"] / 2 <= c["caja_cqw"]["y"] + c["caja_cqw"]["h"] + 0.5)
    for t in atoms:
        if t["kind"] in ("texto", "titular", "simbolo", "regla", "codigo"):
            owner = [c for c in conts if inside(c, t)]
            owner.sort(key=lambda c: c["caja_cqw"]["w"] * c["caja_cqw"]["h"])
            t["dentro_de"] = owner[0]["id"] if owner else "papel"
    tree = {"papel": {"color": bg_hex, "hijos": [t["id"] for t in atoms if t.get("dentro_de") == "papel"]}}
    for c in conts:
        tree[c["id"]] = {"tipo": c["kind"], "color": c.get("relleno", c["color"]), "caja_cqw": c["caja_cqw"], "hijos": [t["id"] for t in atoms if t.get("dentro_de") == c["id"]]}
    (out / "atomos.json").write_text(json.dumps({"hoja_px": [W, H], "paleta": [{"hex": h, "pct": p} for h, p, _ in pal], "contenedores": tree, "atomos": atoms}, ensure_ascii=False, indent=1))
    # guías: ejes de alineación y jerarquía
    lefts = sorted({round(t["caja_cqw"]["x"]) for t in atoms if t["kind"] in ("texto", "bloque", "foto")})
    sizes = sorted({t["altura_letra_cqw"] for t in atoms if t.get("altura_letra_cqw")}, reverse=True)
    CONT = ["## Contenedores (color continuo; el contenido va dentro, los símbolos dentro o fuera)"]
    for cid, c in tree.items():
        kids = [f"#{k} {next(a for a in atoms if a['id']==k)['kind']}" for k in c["hijos"]]
        CONT.append(f"- {'PAPEL (fondo)' if cid=='papel' else '#%s %s %s' % (cid, c['tipo'], c['color'])}: " + (", ".join(kids) if kids else "vacío"))
    L = [f"# Descomposición de {src.name}", f"Hoja {W}×{H}px (relación {H/W:.3f}). Medidas en cqw (% del ancho).", "",
         "## Paleta", ", ".join(f"{h} {p}%" for h, p, _ in pal), "",
         f"## Ejes de alineación a la izquierda (x en cqw)\n{lefts}", "",
         f"## Jerarquía de alturas de letra (cqw, de mayor a menor)\n{sizes[:12]}", "", *CONT, "", "## Átomos"]
    for t in atoms:
        c = t["caja_cqw"]
        L.append(f"- #{t['id']} {t['kind']} · x{c['x']} y{c['y']} w{c['w']} h{c['h']} · {t['zona']} · alinea {t['alinea']} · {t.get('relleno', t['color'])}" + (f" · en {t['dentro_de']}" if t.get("dentro_de") else "") + (f" · letra {t['altura_letra_cqw']}cqw" if t.get('altura_letra_cqw') else "") + (" · SVG" if t.get("svg") else ""))
    (out / "guias.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    cnt = {}
    for t in atoms:
        cnt[t["kind"]] = cnt.get(t["kind"], 0) + 1
    print(out, cnt)


def _box(full, sl, W, H):
    m = np.zeros((H, W), bool)
    m[sl] = True
    return m


if __name__ == "__main__":
    main()
