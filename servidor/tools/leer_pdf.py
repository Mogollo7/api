#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor. Lector eficiente de PDF de referencia.
"""Lee un PDF de ejemplo SIN mirar todas las páginas: saca estructura, tipografías, paleta y medidas en cqw.

    python servidor/tools/leer_pdf.py referencia.pdf [-o ref/nombre] [--paginas 1-6]

Escribe en ref/<nombre>/:
  resumen.md       ← lo que hay que leer (≈ 0,5 KB por página): tipo de hoja, bloques de texto con tamaño/estilo/posición, imágenes, recuadros
  estructura.json  ← lo mismo, para código
  contacto.png     ← todas las páginas en una sola imagen pequeña (mirar ESTA, no 18 imágenes)
  paleta.json      ← colores dominantes (fondos, acentos) con proporción
Unidades: x, y, w, h en cqw (1 = 1 % del ancho de la hoja), como el sistema ANURA; tamaño de letra también en cqw.
"""
import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pdfplumber
from PIL import Image


def hexc(c):
    try:
        return _hexc(c)
    except (TypeError, ValueError):
        return None


def _hexc(c):
    if c is None:
        return None
    if isinstance(c, (int, float)):
        c = (c,)
    if len(c) == 1:
        v = round(c[0] * 255)
        return "#%02x%02x%02x" % (v, v, v)
    if len(c) == 3:
        return "#%02x%02x%02x" % tuple(round(x * 255) for x in c)
    if len(c) == 4:
        k = c[3]
        return "#%02x%02x%02x" % tuple(round(255 * (1 - min(1, x + k))) for x in c[:3])
    return None


def lum(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def palette_of(img, n=7):
    sm = img.convert("RGB").resize((160, int(160 * img.height / img.width)))
    q = sm.quantize(colors=n, method=Image.MEDIANCUT)
    pal = q.getpalette()[: 3 * n]
    cnt = Counter(q.getdata())
    tot = sum(cnt.values())
    return [{"hex": "#%02x%02x%02x" % tuple(pal[3 * i:3 * i + 3]), "pct": round(100 * c / tot, 1)} for i, c in cnt.most_common()]


def lines_of(words, W):
    """Agrupa palabras en líneas por (y, fuente, tamaño) y las une en bloques."""
    rows = defaultdict(list)
    for w in words:
        rows[(round(w["top"] / 3), w["fontname"], round(w["size"]))].append(w)
    lines = []
    for (_, font, size), ws in rows.items():
        ws.sort(key=lambda w: w["x0"])
        lines.append({"text": " ".join(w["text"] for w in ws), "x": ws[0]["x0"], "y": ws[0]["top"], "x1": ws[-1]["x1"], "y1": ws[-1]["bottom"],
                      "font": font.split("+")[-1], "size": ws[0]["size"], "color": hexc(ws[0].get("color"))})
    lines.sort(key=lambda l: (round(l["y"] / 4), l["x"]))
    blocks = []
    for l in lines:
        for b in blocks:
            if b["font"] == l["font"] and abs(b["size"] - l["size"]) < 0.6 and 0 <= l["y"] - b["y1"] < l["size"] * 0.9 and abs(l["x"] - b["x"]) < 8:
                b["lines"].append(l["text"]); b["y1"] = l["y1"]; b["x1"] = max(b["x1"], l["x1"]); break
        else:
            blocks.append({**l, "lines": [l["text"]]})
    return blocks


def page_info(pg, idx, img):
    W, H = float(pg.width), float(pg.height)
    c = 100 / W
    words = pg.extract_words(extra_attrs=["fontname", "size", "non_stroking_color"], keep_blank_chars=False, use_text_flow=False)
    for w in words:
        w["color"] = w.pop("non_stroking_color", None)
    blocks = lines_of(words, W)
    pal = palette_of(img)
    bg = pal[0]["hex"]
    dark = lum(bg) < 0.2
    info = {"pagina": idx, "fondo": bg, "oscura": dark, "bloques": [], "imagenes": [], "recuadros": []}
    for b in blocks:
        info["bloques"].append({"texto": " / ".join(b["lines"])[:160], "fuente": b["font"], "tam_cqw": round(b["size"] * c, 2), "color": b["color"],
                                "x": round(b["x"] * c, 1), "y": round(b["y"] * c, 1), "w": round((b["x1"] - b["x"]) * c, 1), "h": round((b["y1"] - b["y"]) * c, 1),
                                "alinea": "centro" if abs((b["x"] + b["x1"]) / 2 - W / 2) < W * 0.03 else ("izq" if b["x"] < W * 0.2 else "der")})
    for im in pg.images:
        info["imagenes"].append({"x": round(im["x0"] * c, 1), "y": round(im["top"] * c, 1), "w": round((im["x1"] - im["x0"]) * c, 1), "h": round((im["bottom"] - im["top"]) * c, 1)})
    for r in pg.rects[:60]:
        w, h = (r["x1"] - r["x0"]) * c, (r["bottom"] - r["top"]) * c
        if w > 3 and h > 1:
            info["recuadros"].append({"x": round(r["x0"] * c, 1), "y": round(r["top"] * c, 1), "w": round(w, 1), "h": round(h, 1), "relleno": hexc(r.get("non_stroking_color")) if r.get("fill") else None, "borde": hexc(r.get("stroking_color")) if r.get("stroke") else None})
    big = max((b["tam_cqw"] for b in info["bloques"]), default=0)
    n = len(info["bloques"])
    if page_no(idx) == 1:
        info["tipo"] = "portada"
    elif dark and big > 40:
        info["tipo"] = "divisor"
    elif dark:
        info["tipo"] = "oscura"
    elif any(len(i.get("lines", [])) for i in []):
        info["tipo"] = "clara"
    else:
        info["tipo"] = "clara"
    info["paleta"] = pal[:5]
    return info


def page_no(i):
    return i


def md(info):
    L = [f"## Hoja {info['pagina']} · {info['tipo']} · fondo {info['fondo']}"]
    L.append("Paleta: " + ", ".join(f"{p['hex']} {p['pct']}%" for p in info["paleta"]))
    for b in info["bloques"]:
        L.append(f"- «{b['texto']}» · {b['fuente']} {b['tam_cqw']}cqw {b['color']} · x{b['x']} y{b['y']} w{b['w']} ({b['alinea']})")
    for i in info["imagenes"]:
        L.append(f"- IMAGEN x{i['x']} y{i['y']} w{i['w']} h{i['h']}")
    for r in info["recuadros"][:12]:
        L.append(f"- RECUADRO x{r['x']} y{r['y']} w{r['w']} h{r['h']} relleno {r['relleno']} borde {r['borde']}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out")
    ap.add_argument("--paginas")
    ap.add_argument("--dpi", type=int, default=40)
    a = ap.parse_args()
    pdf = Path(a.pdf)
    out = Path(a.out or f"ref/{pdf.stem}")
    out.mkdir(parents=True, exist_ok=True)
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout
    tmp = out / "_p"
    tmp.mkdir(exist_ok=True)
    subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", str(pdf), str(tmp / "p")], check=True)
    pngs = sorted(tmp.glob("p-*.png"))
    infos = []
    with pdfplumber.open(pdf) as doc:
        sel = range(len(doc.pages))
        if a.paginas:
            lo, _, hi = a.paginas.partition("-")
            sel = range(int(lo) - 1, int(hi or lo))
        for i in sel:
            infos.append(page_info(doc.pages[i], i + 1, Image.open(pngs[i])))
        size = (float(doc.pages[0].width), float(doc.pages[0].height))
    allpal = Counter()
    for inf in infos:
        for p in inf["paleta"][:4]:
            allpal[p["hex"]] += p["pct"]
    (out / "estructura.json").write_text(json.dumps(infos, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "paleta.json").write_text(json.dumps([{"hex": h, "peso": round(v, 1)} for h, v in allpal.most_common(10)], indent=1), encoding="utf-8")
    scales = Counter()
    for inf in infos:
        for b in inf["bloques"]:
            scales[(b["fuente"], b["tam_cqw"])] += 1
    head = [f"# Lectura de {pdf.name}", f"{len(infos)} hojas · {size[0]:.0f}×{size[1]:.0f} pt · medidas en cqw (1 = 1 % del ancho)", "", "## Tipografías", "```", fonts.strip(), "```",
            "", "## Escala tipográfica (fuente, tamaño cqw, usos)"] + [f"- {f} {s}cqw ×{n}" for (f, s), n in sorted(scales.items(), key=lambda kv: -kv[0][1])[:18]]
    (out / "resumen.md").write_text("\n".join(head) + "\n\n" + "\n\n".join(md(i) for i in infos) + "\n", encoding="utf-8")
    ims = [Image.open(p) for p in pngs[: len(infos)]]
    w, h = ims[0].size
    cols = min(6, len(ims))
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (w * cols, h * rows), "white")
    for k, im in enumerate(ims):
        sh.paste(im, ((k % cols) * w, (k // cols) * h))
    sh.save(out / "contacto.png", optimize=True)
    for p in pngs:
        p.unlink()
    tmp.rmdir()
    print(f"{out}/resumen.md ({(out/'resumen.md').stat().st_size//1024} KB) · contacto.png · estructura.json · paleta.json")


if __name__ == "__main__":
    main()
