#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Exporta cada diapositiva de un .pptx a PNG con PowerPoint (Windows, COM) o LibreOffice (soffice) si no hay PowerPoint.
"""python servidor/tools/pptx_png.py salida/pptx/x.pptx -o salida/pptx/x_png [--pdf]   (revisión visual y regresión PPTX)"""
import argparse
import shutil
import subprocess
from pathlib import Path


def export(pptx: Path, out: Path, pdf=False):
    out.mkdir(parents=True, exist_ok=True)
    pptx, out = pptx.resolve(), out.resolve()
    if shutil.which("soffice") and not shutil.which("powershell"):
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out), str(pptx)], check=True)
        return
    ps = (f"$a=New-Object -ComObject PowerPoint.Application;$p=$a.Presentations.Open('{pptx}',$true,$false,$false);"
          f"$p.Export('{out}','PNG',1600,900);" + (f"$p.SaveAs('{out / pptx.stem}.pdf',32);" if pdf else "") + "$p.Close();$a.Quit()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True, timeout=600)


def contact(folder: Path, dest: Path, cols=4):
    """Hoja de contacto de todas las diapositivas (en orden), para revisar de un vistazo."""
    from PIL import Image
    import re
    fs = sorted(folder.glob("*.PNG"), key=lambda f: int(re.sub(r"\D", "", f.stem) or 0))
    ims = [Image.open(f).resize((400, 225)) for f in fs]
    sheet = Image.new("RGB", (cols * 410, ((len(ims) + cols - 1) // cols) * 235), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * 410, (i // cols) * 235))
    sheet.save(dest)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--pdf", action="store_true")
    a = ap.parse_args()
    export(Path(a.pptx), Path(a.out), a.pdf)
    contact(Path(a.out), Path(a.out) / "contacto.png")
    print(sorted(p.name for p in Path(a.out).iterdir())[:5], "…")
