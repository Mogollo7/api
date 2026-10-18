#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Herramientas de calidad: ortografía (LanguageTool local), accesibilidad del PDF (pikepdf), SVG (svgo) e imágenes (Pillow).
"""python servidor/calidad.py pdf archivo.pdf | texto "frase" | svg archivo.svg | imagen foto.jpg [--max 2000]
Todo local y gratis. LanguageTool vive en servidor/tools/vendor/ (ver servidor/tools/LEEME_CALIDAD.md); si falta, `ortografia` lo dice sin romper nada."""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LT = next(iter(sorted((HERE / "tools" / "vendor").glob("LanguageTool-*/languagetool-commandline.jar"))), None)
SVGO = HERE / "tools" / "node" / "node_modules" / "svgo" / "bin" / "svgo.js"


def textos(doc):
    """Todos los textos visibles de un contrato (para la ortografía)."""
    out = []

    def rec(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("text", "title", "l", "note", "desc", "lead", "cite", "label") and isinstance(v, str):
                    out.append(v)
                else:
                    rec(v)
        elif isinstance(o, list):
            for v in o:
                if isinstance(v, str) and len(v) > 12:
                    out.append(v)
                else:
                    rec(v)
    rec(doc.get("document", {}))
    return out


def ortografia(texto, lang="es"):
    if not LT:
        return {"disponible": False, "ajuste": "descarga LanguageTool en servidor/tools/vendor/ (LEEME_CALIDAD.md)"}
    r = subprocess.run(["java", "-jar", str(LT), "-l", lang, "--json", "-"], input=texto, capture_output=True, text=True, encoding="utf-8", timeout=180)
    try:
        d = json.loads(r.stdout[r.stdout.find("{"):])
    except ValueError:
        return {"disponible": True, "error": (r.stderr or r.stdout)[-300:]}
    m = [{"error": x["context"]["text"][x["context"]["offset"]:x["context"]["offset"] + x["context"]["length"]], "regla": x["rule"]["id"], "causa": x["message"][:110], "sugerencias": [s["value"] for s in x.get("replacements", [])[:3]]}
         for x in d.get("matches", []) if x["rule"]["id"] not in ("WHITESPACE_RULE", "UPPERCASE_SENTENCE_START")]
    return {"disponible": True, "errores": len(m), "detalle": m[:15]}


def pdf_accesible(ruta):
    import pikepdf
    with pikepdf.open(ruta) as p:
        root, info = p.Root, p.docinfo
        fonts_no_incrustadas = set()
        for pg in p.pages:
            for k, f in (pg.get("/Resources", {}).get("/Font", {}) or {}).items():
                d = f.get("/DescendantFonts", [f])[0] if "/DescendantFonts" in f else f
                fd = d.get("/FontDescriptor")
                if fd is not None and not any(x in fd for x in ("/FontFile", "/FontFile2", "/FontFile3")):
                    fonts_no_incrustadas.add(str(d.get("/BaseFont", k)))
        r = {"titulo": bool(str(info.get("/Title", "")).strip()), "idioma": str(root.get("/Lang", "")) or None, "etiquetado": bool(root.get("/MarkInfo", {}).get("/Marked", False)) and "/StructTreeRoot" in root,
             "paginas": len(p.pages), "fuentes_no_incrustadas": sorted(fonts_no_incrustadas)}
    r["avisos"] = [m for ok, m in ((r["titulo"], "falta el título en los metadatos"), (r["idioma"], "falta el idioma (/Lang)"), (r["etiquetado"], "el PDF no está etiquetado (lectores de pantalla)"),
                                   (not r["fuentes_no_incrustadas"], "hay fuentes sin incrustar")) if not ok]
    return r


def svg(texto):
    if not SVGO.exists():
        return {"disponible": False, "ajuste": "cd servidor/tools/node && npm install"}
    r = subprocess.run(["node", str(SVGO), "-i", "-", "-o", "-", "--multipass"], input=texto, capture_output=True, text=True, encoding="utf-8", timeout=60)
    return {"svg": r.stdout, "antes": len(texto), "despues": len(r.stdout), "ahorro_pct": round(100 * (1 - len(r.stdout) / max(1, len(texto))), 1)} if r.returncode == 0 else {"error": r.stderr[-300:]}


def imagen(ruta, max_px=2000, calidad=82):
    from PIL import Image
    p = Path(ruta)
    im = Image.open(p)
    antes = p.stat().st_size
    im.thumbnail((max_px, max_px))
    out = p.with_name(p.stem + "_opt" + (".png" if im.mode in ("RGBA", "P") else ".jpg"))
    im.save(out, optimize=True, **({} if out.suffix == ".png" else {"quality": calidad}))
    return {"archivo": str(out), "antes": antes, "despues": out.stat().st_size, "px": im.size}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
    elif a[0] == "pdf":
        print(json.dumps(pdf_accesible(a[1]), ensure_ascii=False, indent=1))
    elif a[0] == "texto":
        print(json.dumps(ortografia(a[1]), ensure_ascii=False, indent=1))
    elif a[0] == "svg":
        r = svg(Path(a[1]).read_text(encoding="utf-8"))
        print({k: v for k, v in r.items() if k != "svg"})
    elif a[0] == "imagen":
        print(imagen(a[1], int(a[a.index("--max") + 1]) if "--max" in a else 2000))
