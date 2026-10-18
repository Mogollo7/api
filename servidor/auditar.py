#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Auditoría de un PDF hecho fuera de la API (modo B): márgenes, superposición, contraste y fuentes. Solo lectura.
"""python servidor/auditar.py archivo.pdf [--margen-mm 10]

Devuelve JSON con formato fijo: {estado, paginas, avisos:[{pagina, tipo, causa, ajuste}], resumen:{…}, fuentes:[…]}.
Contraste: color del texto contra el fondo más frecuente bajo él (WCAG 4,5:1; 3:1 desde 18 pt). Usa PyMuPDF."""
import json
import sys
from collections import Counter

PT_MM = 25.4 / 72
MAX_PAGINAS, MAX_AVISOS = 60, 40


def _lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def contraste(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def auditar(ruta=None, datos=None, margen_mm=10.0):
    import pymupdf as fitz
    doc = fitz.open(ruta) if ruta else fitz.open(stream=datos, filetype="pdf")
    avisos, res = [], Counter()

    def add(p, tipo, causa, ajuste):
        res[tipo] += 1
        if len(avisos) < MAX_AVISOS:
            avisos.append({"pagina": p, "tipo": tipo, "causa": causa, "ajuste": ajuste})

    fuentes = {}
    for pn in range(min(len(doc), MAX_PAGINAS)):
        pg = doc[pn]
        for f in pg.get_fonts():
            fuentes[f[3].split("+")[-1]] = f[1] != "n/a"
        W, H = pg.rect.width, pg.rect.height
        d = pg.get_text("dict")
        lines = []
        for b in d["blocks"]:
            for ln in b.get("lines", []):
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if t:
                    lines.append((fitz.Rect(ln["bbox"]), t, ln["spans"]))
        m = margen_mm / PT_MM
        for r, t, _ in lines:
            lado = [("izquierdo", r.x0), ("superior", r.y0), ("derecho", W - r.x1), ("inferior", H - r.y1)]
            mal = [(n, v) for n, v in lado if v < m]
            if mal:
                n, v = min(mal, key=lambda x: x[1])
                add(pn + 1, "margen", f"«{t[:30]}» a {max(v, 0) * PT_MM:.1f} mm del borde {n} (mínimo {margen_mm:g} mm)", "mueve o reduce el bloque; deja el margen mínimo")
        for i in range(min(len(lines), 400)):
            for j in range(i + 1, min(len(lines), 400)):
                a, b = lines[i][0], lines[j][0]
                x = a & b
                if x.is_empty or x.get_area() <= 0:
                    continue
                if x.get_area() / min(a.get_area(), b.get_area()) > .25:
                    add(pn + 1, "solape", f"«{lines[i][1][:24]}» se superpone con «{lines[j][1][:24]}»", "separa los bloques o reduce el tamaño del texto")
        if pn < 25 and lines:
            pix = pg.get_pixmap(dpi=72, alpha=False)
            for r, t, spans in lines[:120]:
                s = spans[0]
                col = s["color"]
                fg = ((col >> 16) & 255, (col >> 8) & 255, col & 255)
                rr = r & pix.irect
                if rr.is_empty or rr.width < 2 or rr.height < 2:
                    continue
                cnt = Counter()
                for yy in range(int(rr.y0), int(rr.y1), max(1, int(rr.height // 6))):
                    for xx in range(int(rr.x0), int(rr.x1), max(1, int(rr.width // 14))):
                        cnt[pix.pixel(xx, yy)[:3]] += 1
                bg = cnt.most_common(1)[0][0]
                c = contraste(fg, bg)
                lim = 3.0 if s["size"] >= 18 else 4.5
                if c < lim:
                    add(pn + 1, "contraste", f"«{t[:30]}» tiene contraste {c:.1f}:1 (mínimo {lim:g}:1)", "oscurece el texto o aclara el fondo")
    for n, emb in fuentes.items():
        if not emb:
            add(0, "fuente", f"la fuente «{n}» no está incrustada", "incrusta o convierte la fuente al exportar el PDF")
    out = {"estado": "ok" if not avisos else "con_avisos", "paginas": len(doc), "revisadas": min(len(doc), MAX_PAGINAS), "avisos": avisos,
           "resumen": {k: res.get(k, 0) for k in ("margen", "solape", "contraste", "fuente")}, "fuentes": [{"nombre": n, "incrustada": e} for n, e in sorted(fuentes.items())]}
    doc.close()
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    mm = float(sys.argv[sys.argv.index("--margen-mm") + 1]) if "--margen-mm" in sys.argv else 10.0
    print(json.dumps(auditar(sys.argv[1], margen_mm=mm), ensure_ascii=False, indent=1))
