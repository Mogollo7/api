# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Recursos del diseño y de las imágenes: fuentes, símbolos, imágenes con filtro duotono y créditos.
Todo se incrusta (base64): el render no depende de internet.
"""
import base64
import csv
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

BAYER = np.array([
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26], [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25], [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]) / 64.0


def b64(path: Path) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


def font_css(design_dir: Path, manifest: dict) -> str:
    out = []
    for f in manifest["fonts"]:
        extra = f';font-stretch:{f["stretch"]}' if f.get("stretch") else ""
        out.append(
            f'@font-face{{font-family:"{f["family"]}";font-weight:{f["weight"]}{extra};'
            f'src:url(data:font/woff2;base64,{b64(design_dir / f["file"])}) format("woff2")}}'
        )
    return "\n".join(out)


def root_css(roles: dict, manifest: dict = None) -> str:
    """Variables de color por rol y de fuente. Un diseño puede declarar `font_roles: {display, body, mono}` (familias de su `fonts`); sin él, Anton / Archivo / IBM Plex Mono."""
    v = ";".join(f"--{k}:{c}" for k, c in roles.items())
    fr = (manifest or {}).get("font_roles") or {}
    disp = f'"{fr["display"]}",system-ui,sans-serif' if fr.get("display") else '"Anton",Impact,"Arial Narrow",sans-serif'
    body = f'"{fr["body"]}",system-ui,sans-serif' if fr.get("body") else '"Archivo",system-ui,sans-serif'
    mono = f'"{fr["mono"]}",system-ui,sans-serif' if fr.get("mono") else '"IBM Plex Mono",ui-monospace,monospace'
    return (":root{" + v + f";--font-display:{disp};--font-body:{body};--font-mono:{mono};"
            "--sombra-dura:8px 8px 0 var(--negro);--fondo:var(--negro)}")


class Symbols:
    def __init__(self, design_dir: Path):
        self.cat = json.loads((design_dir / "simbolos.json").read_text(encoding="utf-8"))["simbolos"]
        self.used = []

    def use(self, sid: str):
        if sid not in self.cat:
            raise KeyError(f"símbolo {sid} no existe en el catálogo")
        if sid not in self.used:
            self.used.append(sid)

    def defs(self) -> str:
        parts = [
            f'<symbol id="{sid}" viewBox="{self.cat[sid]["viewBox"]}"><path fill-rule="evenodd" d="{self.cat[sid]["d"]}"/></symbol>'
            for sid in self.used
        ]
        return '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(parts) + "</svg>"


def sym_html(sym: Symbols, sid: str, style: str = "", cls: str = "sym") -> str:
    sym.use(sid)
    return f'<i class="{cls}" style="{style}"><svg aria-hidden="true"><use href="#{sid}"/></svg></i>'


def duotone(src: Path, treatment: str, roles: dict, treatments: dict, cache: Path, width: int = 1400) -> Path:
    """Filtro de imagen del sistema (imagenes.md): grises, autocontraste, curva dura, grano, tramado Bayer 8x8 y dos tintas.
    Se aplica en el servidor con los colores de la paleta activa; el resultado se guarda en caché."""
    dark_k, light_k = treatments.get(treatment) or treatments["calido"]
    dark, light = roles.get(dark_k, dark_k), roles.get(light_k, light_k)
    key = hashlib.sha1(f"{src.resolve()}|{src.stat().st_mtime_ns}|{dark}|{light}|{width}".encode()).hexdigest()[:16]
    out = cache / f"{src.stem}_{treatment}_{key}.png"
    if out.exists():
        return out
    im = Image.open(src).convert("RGB")
    im = ImageOps.exif_transpose(im)
    w, h = im.size
    if w != width:
        im = im.resize((width, max(1, round(h * width / w))), Image.LANCZOS)
    g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=2)
    a = np.asarray(g).astype(float) / 255
    a = np.clip((a - 0.25) * 1.9, 0, 1) ** 1.1
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 0.16, a.shape)
    grain = np.asarray(Image.fromarray((np.clip(noise * 0.5 + 0.5, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8))).astype(float) / 255 - 0.5
    b = np.clip(a + grain * 0.9, 0, 1)
    hh, ww = b.shape
    T = np.tile(BAYER, (hh // 8 + 1, ww // 8 + 1))[:hh, :ww]
    bw = ((b * 0.55 + (b > T) * 0.45) > 0.5)
    img = Image.fromarray((bw * 255).astype("uint8"), "L").convert("P")
    pal = [int(dark[i:i + 2], 16) for i in (1, 3, 5)] + [int(light[i:i + 2], 16) for i in (1, 3, 5)]
    img.putpalette(pal + [0] * (768 - 6))
    cache.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(bw.astype("uint8"), "P")
    img.putpalette(pal + [0] * (768 - 6))
    img.save(out, optimize=True)
    return out


def load_credits(images_root: Path) -> dict:
    f = images_root / "creditos.csv"
    out = {}
    if f.exists():
        with f.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                out[r["archivo"]] = r
    return out


SRC_HEX = {"negro": "#121212", "bosque": "#10291F", "ocre": "#D4A72C", "crema": "#F8F5EE", "vivo": "#2ECC5F"}


def recolor(src: Path, roles: dict, cache: Path) -> Path:
    """Las ranas del sistema vienen en dos tintas fijas (p. ej. negro + ocre). Con otra paleta se repintan por luminancia:
    el tono oscuro pasa al rol oscuro de la paleta activa y el claro al rol claro. Con la paleta ANURA se devuelve el original."""
    toks = src.stem.split("-")[-2:]
    if len(toks) < 2 or toks[0] not in SRC_HEX or toks[1] not in SRC_HEX:
        return src
    d0, l0 = SRC_HEX[toks[0]], SRC_HEX[toks[1]]
    d1, l1 = roles.get(toks[0], d0), roles.get(toks[1], l0)
    if (d0.lower(), l0.lower()) == (d1.lower(), l1.lower()):
        return src
    out = cache / f"{src.stem}_{d1[1:]}_{l1[1:]}.png"
    if out.exists():
        return out
    rgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
    a = np.asarray(Image.open(src).convert("RGB")).astype(float)
    lum = lambda c: 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    ld, ll = lum(rgb(d0)), lum(rgb(l0))
    t = np.clip((lum(a) - ld) / (ll - ld), 0, 1)[..., None]
    res = rgb(d1) * (1 - t) + rgb(l1) * t
    cache.mkdir(parents=True, exist_ok=True)
    Image.fromarray(res.astype("uint8")).save(out, optimize=True)
    return out
