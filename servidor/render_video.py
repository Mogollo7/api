#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Contrato JSON -> video MP4 (16:9 o 9:16) con HyperFrames. Mismo contrato, roles de color y fuentes que el PDF y el PPTX.

    python servidor/render_video.py contenido/informe_ventas.json -o salida/video/informe.mp4 [--formato video-9x16] [--sin-render]

Cómo funciona (determinista, sin agente):
  1. El «director» elige escenas del documento: portada → una apertura por parte → los momentos fuertes de cada parte
     (cifra gigante, tarjetas de cifras, gráfico, cita, lista, idea principal) → cierre. Todo cae en la grilla del tempo (BPM).
  2. Escribe un proyecto HyperFrames (index.html + gsap + fuentes del diseño) con UN timeline GSAP en pausa: cada cuadro es función del tiempo.
  3. `npx hyperframes lint` y `npx hyperframes render` producen el MP4.
El proyecto queda junto al MP4 (carpeta `<nombre>_proyecto/`) para pulirlo con las skills /estudio-motion, /brag o las de HyperFrames.
Texto del documento = datos: siempre escapado, nunca HTML.
"""
import argparse
import sys
import html
import json
import math
import re
import shutil
import subprocess
import time
from pathlib import Path

import render
from engine import contract, paleta
from engine.text import plain

HERE = Path(__file__).resolve().parent
FORMATS = {"video-16x9": (1920, 1080), "video-9x16": (1080, 1920)}
CHAR_W = {"display": 0.46, "body": 0.52, "mono": 0.6}
NPX = shutil.which("npx") or shutil.which("npx.cmd") or "npx"


def esc(s):
    return html.escape(plain(str(s)), quote=True)


def fit_px(text, width, lines, big, small, font="display"):
    """Tamaño de letra (px) para que `text` quepa en `lines` líneas de `width` px. Sin medir en el navegador (regla de HyperFrames)."""
    n = max(len(plain(str(text))), 1)
    for px in range(big, small - 1, -4):
        if math.ceil(n * px * CHAR_W[font] / width) <= lines:
            return px
    return small


def number(v):
    """'$ 128 M' -> ('$ ', 128.0, ' M', 0); '62,9 %' -> ('', 62.9, ' %', 1). None si no hay cifra."""
    m = re.search(r"-?\d[\d.]*(?:,\d+)?", str(v))
    if not m:
        return None
    raw = m.group(0)
    dec = len(raw.split(",")[1]) if "," in raw else 0
    val = float(raw.replace(".", "").replace(",", ".")) if "," in raw or raw.count(".") > 1 else float(raw)
    return str(v)[:m.start()], val, str(v)[m.end():], dec


# presets de animación (biblioteca/animaciones): nombre -> (desde, hasta, ease, usa_clip). Los parámetros salen de options.video (entrada, escalon).
PRESETS_ENTRADA = {"slide": ("{x:-60,opacity:0}", "{x:0,opacity:1,%s,ease:\"expo.out\"}"), "fade-up": ("{y:40,opacity:0}", "{y:0,opacity:1,%s,ease:\"power3.out\"}"),
                   "wipe-reveal": ("{clipPath:\"inset(0 100% 0 0)\"}", "{clipPath:\"inset(0 0% 0 0)\",%s,ease:\"power4.inOut\"}")}


class Director:
    def __init__(self, doc, m, roles, fmt, opts, report):
        self.doc, self.m, self.roles, self.rep = doc, m, roles, report
        self.W, self.H = FORMATS[fmt]
        self.vert = self.H > self.W
        self.bpm = int(opts.get("bpm", 120))
        self.beat = 60 / self.bpm
        self.auto = "duration" not in opts
        self.max_s = float(opts.get("duration", 60))
        self.entrada = opts.get("entrada", "slide")           # preset de entrada de titulares (ver biblioteca/animaciones)
        if self.entrada not in PRESETS_ENTRADA:
            report["avisos"].append({"bloque": "options.video.entrada", "causa": f"preset '{self.entrada}' desconocido", "ajuste": f"usa {', '.join(PRESETS_ENTRADA)}; se usó 'slide'"})
            self.entrada = "slide"
        self.escalon = max(0.02, min(0.5, float(opts.get("escalon", self.beat / 2))))     # retraso entre tarjetas (stagger-grid)
        self.pairs = {tuple(x) for x in m["palette"]["pares_texto_permitidos"]}
        fam = [f["family"] for f in m["fonts"]]
        self.F = {"display": fam[0], "body": fam[1] if len(fam) > 1 else fam[0], "mono": fam[2] if len(fam) > 2 else fam[-1]}
        self.scenes, self.tweens, self.t = [], [], 0.0
        self.esc, self.fit, self.extra_css = esc, fit_px, ""
        self.overlays, self.motion, self.cortes = [], False, []          # transiciones y modo motion (video_motion.py)
        self.pad = round(self.W * 0.07)

    # color de texto solo en pares permitidos (igual que el PPTX)
    def fg(self, bg, prefs=("crema", "negro", "bosque")):
        for r in prefs:
            if (r, bg) in self.pairs:
                return r
        return "crema" if paleta.ratio(self.roles["crema"], self.roles[bg]) >= 4.5 else "negro"

    def acc(self, bg):
        return self.fg(bg, ("vivo", "ocre", "crema", "negro"))

    def scene(self, bars, bg, body, tw):
        """Una escena = un clip HyperFrames que dura `bars` compases. `tw(t0, d)` devuelve los tweens (relativos al inicio)."""
        d = bars * 4 * self.beat
        sid = f"s{len(self.scenes) + 1}"
        self.scenes.append(f'<section id="{sid}" class="clip" data-start="{self.t:.3f}" data-duration="{d:.3f}" data-track-index="1" '
                           f'style="background:var(--{bg});color:var(--{self.fg(bg)})"><div class="in" id="{sid}-in">{body(sid)}</div></section>')
        self.tweens += [x.replace("$S", sid) for x in tw(self.t, d)]
        # salida: el contenido se va en la última corchea (el clip lo oculta el runtime al terminar)
        self.tweens.append(f'tl.to("#{sid}-in",{{opacity:0,y:-30,duration:{self.beat/2:.3f},ease:"power2.in"}},{self.t + d - self.beat/2:.3f});')
        self.t += d

    # ---------- escenas ----------
    def cover(self, cov, meta):
        word, title = plain(cov.get("vertical", "")).upper(), plain(cov.get("title", ""))
        vw = fit_px(word, self.W - 2 * self.pad, 1, 420, 120)
        tp = fit_px(title.upper(), self.W - 2 * self.pad, 3, 120, 48)
        b = self.beat

        def body(s):
            return (f'<div class="kick mono" id="{s}-k">{esc(" · ".join(x for x in (meta.get("date"), meta.get("version")) if x))}</div>'
                    f'<div class="word" id="{s}-w" style="font-size:{vw}px;color:var(--{self.acc("negro")})">{esc(word)}</div>'
                    f'<div class="rule" id="{s}-r"></div>'
                    f'<div class="title" id="{s}-t" style="font-size:{tp}px">{esc(title)}</div>')
        self.scene(2, "negro", body, lambda t0, d: [
            f'tl.fromTo("#$S-w",{{scale:1.5,opacity:0,filter:"blur(30px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:{b*1.5:.3f},ease:"expo.out"}},{t0:.3f});',
            f'tl.fromTo("#$S-r",{{scaleX:0}},{{scaleX:1,duration:{b:.3f},ease:"power4.inOut"}},{t0 + b*2:.3f});',
            f'tl.fromTo("#$S-t",{{y:80,opacity:0}},{{y:0,opacity:1,duration:{b:.3f},ease:"back.out(1.6)"}},{t0 + b*2.5:.3f});',
            f'tl.fromTo("#$S-k",{{opacity:0}},{{opacity:1,duration:{b/2:.3f}}},{t0 + b*3:.3f});'])

    def divider(self, k, part):
        bg = "bosque" if k % 2 else "negro"
        num, title = f"{k+1:02d}", plain(part.get("title", "")).upper()
        b = self.beat
        np_ = round(self.H * (0.55 if not self.vert else 0.3))
        tp = fit_px(title, self.W - 2 * self.pad, 2, 150, 60)

        def body(s):
            return (f'<div class="num" id="{s}-n" data-layout-allow-overflow style="font-size:{np_}px;color:var(--{self.acc(bg)})">{num}</div>'
                    f'<div class="title" id="{s}-t" style="font-size:{tp}px">{esc(title)}</div>'
                    f'<div class="sub" id="{s}-d">{esc(part.get("desc", ""))}</div>')
        self.scene(1, bg, body, lambda t0, d: [
            f'tl.fromTo("#$S-n",{{yPercent:60,opacity:0}},{{yPercent:0,opacity:1,duration:{b*1.2:.3f},ease:"expo.out"}},{t0:.3f});',
            f'tl.fromTo("#$S-t",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:{b:.3f},ease:"power4.inOut"}},{t0 + b:.3f});',
            f'tl.fromTo("#$S-d",{{opacity:0,y:20}},{{opacity:1,y:0,duration:{b:.3f},ease:"power3.out"}},{t0 + b*2:.3f});'])

    def headline(self, s, title, bg):
        tp = fit_px(plain(title).upper(), self.W - 2 * self.pad, 2, 110, 56)
        return f'<div class="head" id="{s}-h" style="font-size:{tp}px">{esc(title)}</div>'

    def head_tw(self, t0):
        a, b = PRESETS_ENTRADA[self.entrada]
        return 'tl.fromTo("#$S-h",' + a + "," + b.replace("%s", f"duration:{self.beat:.3f}") + f",{t0:.3f});"

    def counter(self, sel, v, t0, dur):
        n = number(v)
        if not n:
            return f'tl.fromTo("{sel}",{{opacity:0,scale:.8}},{{opacity:1,scale:1,duration:{dur:.3f},ease:"back.out(2)"}},{t0:.3f});'
        pre, val, post, dec = (json.dumps(x) for x in (n[0], n[1], n[2], n[3]))
        return (f'(()=>{{const o={{v:0}};tl.to(o,{{v:{val},duration:{dur:.3f},ease:"power3.out",onUpdate:()=>{{document.querySelector("{sel}").textContent='
                f'{pre}+o.v.toLocaleString("es-CO",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})+{post}}}}},{t0:.3f});'
                f'tl.fromTo("{sel}",{{opacity:0}},{{opacity:1,duration:.15}},{t0:.3f})}})();')

    def big(self, title, b):
        bg, v = "crema", f"{b.get('value', '')}{b.get('unit', '')}"
        vp = fit_px(v, self.W - 2 * self.pad, 1, 420, 140)

        def body(s):
            return (self.headline(s, title, bg) + f'<div class="bigv" id="{s}-v" style="font-size:{vp}px;color:var(--{self.fg(bg, ("bosque", "hoja", "negro"))})">{esc(v)}</div>'
                    f'<div class="sub" id="{s}-c">{esc(b.get("caption", ""))}</div>')
        self.scene(2, bg, body, lambda t0, d: [self.head_tw(t0), self.counter("#$S-v", v, t0 + self.beat, self.beat * 3),
                                               f'tl.fromTo("#$S-c",{{opacity:0,y:20}},{{opacity:1,y:0,duration:{self.beat:.3f}}},{t0 + self.beat*3:.3f});'])

    def kpi(self, title, b):
        its = b.get("items", [])[:4]
        cols = 2 if self.vert else len(its)

        def body(s):
            cards = "".join(f'<div class="card" id="{s}-c{i}" style="background:var(--{"negro" if i == 0 else "bosque"});color:var(--{self.fg("negro")})">'
                            f'<div class="kv" id="{s}-v{i}" style="color:var(--{self.acc("negro" if i == 0 else "bosque")})">{esc(it.get("v", ""))}</div>'
                            f'<div class="kl">{esc(it.get("l", ""))}</div></div>' for i, it in enumerate(its))
            return self.headline(s, title, "crema") + f'<div class="cards" style="grid-template-columns:repeat({cols},1fr)">{cards}</div>'
        b_ = self.beat
        self.scene(2, "crema", body, lambda t0, d: [self.head_tw(t0)] + [
            f'tl.fromTo("#$S-c{i}",{{y:120,opacity:0}},{{y:0,opacity:1,duration:{b_:.3f},ease:"back.out(1.4)"}},{t0 + b_ + i*self.escalon:.3f});' + self.counter(f"#$S-v{i}", it.get("v", ""), t0 + b_ * 1.5 + i*self.escalon, b_ * 2)
            for i, it in enumerate(its)])

    def bars(self, title, b):
        ch = b.get("chart") or {}
        d = ch.get("data") or {}
        if ch.get("type") == "hist":
            its = [{"l": f"{x:g}", "v": v} for x, v in d.get("bars", [])][:14]
        elif ch.get("type") == "stack":
            its = [{"l": r.get("l"), "v": (r.get("v") or [0])[0]} for r in d.get("rows", [])]
        elif d.get("series") and d.get("categories"):
            its = [{"l": c, "v": d["series"][0]["values"][i]} for i, c in enumerate(d["categories"])]
        elif ch.get("type") == "line":
            pts = d.get("points") or (d.get("series") or [{}])[0].get("points", [])
            its = [{"l": str(p[0]), "v": p[1]} for p in pts]
        else:
            its = d.get("items", [])
        its = [i for i in its if isinstance(i.get("v"), (int, float))][:12]
        if not its:
            return False
        mx = max(i["v"] for i in its) or 1
        horiz = self.vert or ch.get("type") == "hbar"

        def body(s):
            rows = "".join(f'<div class="bar"><span class="bl">{esc(i.get("l", ""))}</span><span class="bt"><span class="bf" id="{s}-b{k}" '
                           f'style="{"width" if horiz else "height"}:{100 * i["v"] / mx:.1f}%;background:var(--{"vivo" if i.get("hi") else "hoja"})"></span></span>'
                           f'<span class="bv mono">{esc(i["v"])}</span></div>' for k, i in enumerate(its))
            return self.headline(s, b.get("title") or title, "crema") + f'<div class="chart {"h" if horiz else "v"}">{rows}</div>'
        prop = "scaleX" if horiz else "scaleY"
        b_ = self.beat
        self.scene(2, "crema", body, lambda t0, d: [self.head_tw(t0)] + [
            f'tl.fromTo("#$S-b{k}",{{{prop}:0}},{{{prop}:1,duration:{b_*1.5:.3f},ease:"expo.out"}},{t0 + b_ + k * b_ / 4:.3f});' for k in range(len(its))])
        return True

    def scatter(self, title, b):
        d = (b.get("chart") or {}).get("data") or {}
        pts = [p[:2] for p in d.get("points", []) if len(p) >= 2][:80]
        if len(pts) < 3:
            return False
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, x1 = d.get("xrange") or (min(xs), max(xs))
        y0, y1 = d.get("yrange") or (min(ys), max(ys))
        X = lambda v: 100 * (v - x0) / ((x1 - x0) or 1)
        Y = lambda v: 100 - 100 * (v - y0) / ((y1 - y0) or 1)

        def body(s):
            dots = "".join(f'<i class="dot" id="{s}-p{k}" style="left:{X(x):.1f}%;top:{Y(y):.1f}%"></i>' for k, (x, y) in enumerate(pts))
            lab = f'<div class="axl mono">{esc(d.get("xlabel", ""))} → · ↑ {esc(d.get("ylabel", ""))}</div>'
            return self.headline(s, b.get("title") or title, "crema") + f'<div class="plot">{dots}</div>{lab}'
        step = (self.beat * 3) / len(pts)
        self.scene(2, "crema", body, lambda t0, d_: [self.head_tw(t0)] + [
            f'tl.fromTo("#$S-p{k}",{{scale:0}},{{scale:1,duration:{self.beat/2:.3f},ease:"back.out(3)"}},{t0 + self.beat + k*step:.3f});' for k in range(len(pts))])
        return True

    def quote(self, title, b):
        words = plain(b.get("text", "")).split()[:22]
        qp = fit_px(" ".join(words), self.W - 2 * self.pad, 4 if not self.vert else 7, 110, 52, "body")

        def body(s):
            ws = " ".join(f'<span class="w" id="{s}-w{i}">{esc(w)}</span>' for i, w in enumerate(words))
            return f'<div class="quote" style="font-size:{qp}px">{ws}</div><div class="kick mono" id="{s}-by">{esc(b.get("by", ""))}</div>'
        step = min(self.beat / 2, (self.beat * 6) / max(len(words), 1))
        self.scene(2, "bosque", body, lambda t0, d: [
            f'tl.fromTo("#$S-w{i}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:{step*1.5:.3f},ease:"power3.out"}},{t0 + i*step:.3f});' for i in range(len(words))]
            + [f'tl.fromTo("#$S-by",{{opacity:0}},{{opacity:1,duration:{self.beat:.3f}}},{t0 + len(words)*step:.3f});'])

    def bullets(self, title, items):
        items = [plain(i.get("t", "") if isinstance(i, dict) else i) for i in items][:5]

        def body(s):
            li = "".join(f'<li id="{s}-l{i}">{esc(t)}</li>' for i, t in enumerate(items))
            return self.headline(s, title, "crema") + f'<ul class="list">{li}</ul>'
        self.scene(2, "crema", body, lambda t0, d: [self.head_tw(t0)] + [
            f'tl.fromTo("#$S-l{i}",{{x:80,opacity:0}},{{x:0,opacity:1,duration:{self.beat:.3f},ease:"expo.out"}},{t0 + self.beat*(1 + i*0.75):.3f});' for i in range(len(items))])

    def idea(self, title, lead, kind):
        bg = "bosque" if kind == "clave" else "crema"
        lp = fit_px(lead, self.W - 2 * self.pad, 5 if not self.vert else 9, 64, 34, "body")

        def body(s):
            return self.headline(s, title, bg) + f'<div class="lead" id="{s}-p" style="font-size:{lp}px">{esc(lead)}</div>'
        self.scene(2, bg, body, lambda t0, d: [self.head_tw(t0),
                                               f'tl.fromTo("#$S-p",{{opacity:0,y:40}},{{opacity:1,y:0,duration:{self.beat*1.5:.3f},ease:"power3.out"}},{t0 + self.beat:.3f});'])

    def outro(self, meta):
        brand = plain(meta.get("footer") or meta.get("title") or "")
        tp = fit_px(brand.upper(), self.W - 2 * self.pad, 2, 120, 48)

        def body(s):
            return f'<div class="title" id="{s}-t" style="font-size:{tp}px">{esc(brand)}</div><div class="rule" id="{s}-r"></div><div class="kick mono" id="{s}-m">myStyle</div>'
        self.scene(2, "negro", body, lambda t0, d: [
            f'tl.fromTo("#$S-t",{{scale:.85,opacity:0}},{{scale:1,opacity:1,duration:{self.beat*1.5:.3f},ease:"expo.out"}},{t0:.3f});',
            f'tl.fromTo("#$S-r",{{scaleX:0}},{{scaleX:1,duration:{self.beat:.3f},ease:"power4.inOut"}},{t0 + self.beat:.3f});',
            f'tl.fromTo("#$S-m",{{opacity:0}},{{opacity:1,duration:{self.beat:.3f}}},{t0 + self.beat*2:.3f});'])

    # ---------- dirección ----------
    def moments(self, part):
        """Los momentos fuertes de una parte, en orden de preferencia, uno por sección como mucho."""
        rank = {"big": 0, "kpi": 1, "chart": 2, "quote": 3, "figure": 4, "list": 5}
        out = []
        for sec in part.get("sections", []):
            bl = sorted([b for b in sec.get("blocks", []) if b.get("type") in rank], key=lambda b: rank[b["type"]])
            if bl:
                out.append((sec, bl[0]))
            elif sec.get("lead") or any(x.get("type") == "p" for x in sec.get("blocks", [])):
                out.append((sec, {"type": "_idea"}))
        return out

    def direct(self):
        """Reparte el tiempo por rondas: primero el mejor momento de cada parte, luego el segundo… Nunca se salta una parte entera."""
        d, meta = self.doc["document"], self.doc.get("meta", {})
        bar = 4 * self.beat
        parts = d.get("parts", [])
        plan = [self.moments(p)[:3] for p in parts]
        divs = len(parts) > 1
        if self.auto:                                   # sin duración pedida: hasta 2 momentos por parte, tope 60 s
            want = 2 + 2 + (len(parts) if divs else 0) + 2 * sum(min(2, len(m)) for m in plan)
            self.max_s = min(60.0, want * bar)
        max_bars = int(self.max_s // bar)
        if divs and max_bars - 4 - len(parts) < 2:      # muy corto: sin aperturas de parte
            divs = False
        slots = max(0, (max_bars - 4 - (len(parts) if divs else 0)) // 2)
        take, rnd = [0] * len(parts), 0
        while slots and any(take[i] < len(plan[i]) for i in range(len(parts))):
            for i in range(len(parts)):
                if slots and take[i] < len(plan[i]) and take[i] == rnd:
                    take[i] += 1
                    slots -= 1
            rnd += 1
        self.cover(d["cover"], meta)
        for k, part in enumerate(parts):
            if divs:
                self.divider(k, part)
            for sec, b in plan[k][:take[k]]:
                t, title = b["type"], sec.get("title", "")
                ok = True
                if t == "big":
                    self.big(title, b)
                elif t == "kpi":
                    self.kpi(title, b)
                elif t in ("chart", "figure") and b.get("chart"):
                    ok = self.scatter(title, b) if b["chart"].get("type") == "scatter" else self.bars(title, b)
                elif t == "quote":
                    self.quote(title, b)
                elif t == "list":
                    self.bullets(title, b.get("items", []))
                else:
                    ok = False
                if not ok:
                    txt = sec.get("lead") or next((x.get("text") for x in sec.get("blocks", []) if x.get("type") == "p"), "")
                    if txt:
                        self.idea(title, plain(txt)[:260], sec.get("kind"))
        self.outro(meta)
        skipped = sum(len(m) for m in plan) - sum(take)
        if skipped:
            self.rep["avisos"].append({"bloque": "video", "causa": f"{skipped} momentos no entraron en {self.max_s:.0f} s", "ajuste": "sube options.video.duration (máx. 120) o pide un video por parte"})

    def html(self, design_dir):
        fonts = "".join(f'@font-face{{font-family:"{f["family"]}";src:url("assets/fonts/{Path(f["file"]).name}") format("woff2");font-weight:{f["weight"]}}}' for f in self.m["fonts"])
        roles = ";".join(f"--{k}:{v}" for k, v in self.roles.items())
        p, W, H = self.pad, self.W, self.H
        css = f"""{fonts}
:root{{{roles}}}
html,body{{margin:0;background:var(--negro)}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;font-family:"{self.F['body']}",sans-serif}}
.clip{{position:absolute;inset:0}}
.in{{position:absolute;inset:0;padding:{p}px;display:flex;flex-direction:column;justify-content:center;gap:{round(H*0.03)}px}}
.mono{{font-family:"{self.F['mono']}",monospace;letter-spacing:.12em;text-transform:uppercase}}
.kick{{font-size:{round(H*0.026)}px;font-weight:600}}
.word,.num,.bigv{{font-family:"{self.F['display']}",sans-serif;line-height:.85;text-transform:uppercase}}
.title,.head{{font-family:"{self.F['display']}",sans-serif;text-transform:uppercase;line-height:.95}}
.rule{{height:{max(6, round(H*0.008))}px;background:currentColor;transform-origin:left center;width:100%}}
.sub,.lead{{font-size:{round(H*0.034)}px;line-height:1.3;max-width:{round(W*0.8)}px}}
.cards{{display:grid;gap:{round(W*0.015)}px}}
.card{{padding:{round(H*0.03)}px;display:flex;flex-direction:column;gap:12px}}
.kv{{font-family:"{self.F['display']}",sans-serif;font-size:{round(H*(0.11 if not self.vert else 0.06))}px;line-height:1}}
.kl{{font-size:{round(H*0.026)}px;font-weight:700}}
.chart{{display:flex;gap:{round(W*0.01)}px;flex:1;min-height:0}}
.chart.v{{align-items:stretch}}.chart.v .bar{{flex:1;display:flex;flex-direction:column-reverse;align-items:center;gap:8px}}
.chart.v .bt{{flex:1;width:100%;display:flex;align-items:flex-end}}.chart.v .bf{{width:100%;transform-origin:bottom center;outline:3px solid var(--negro)}}
.chart.h{{flex-direction:column;justify-content:center}}.chart.h .bar{{display:grid;grid-template-columns:{round(W*0.22)}px 1fr auto;align-items:center;gap:16px}}
.chart.h .bt{{display:block;height:{round(H*0.04)}px}}.chart.h .bf{{display:block;height:100%;transform-origin:left center;outline:3px solid var(--negro)}}
.bl{{font-size:{round(H*0.022)}px;font-weight:700;text-align:center}}.bv{{font-size:{round(H*0.022)}px}}
.plot{{position:relative;flex:1;min-height:0;border-left:4px solid currentColor;border-bottom:4px solid currentColor;margin:0 {round(W*0.02)}px {round(H*0.02)}px}}
.dot{{position:absolute;width:{max(14, round(min(W, H)*0.022))}px;height:{max(14, round(min(W, H)*0.022))}px;margin:-{max(7, round(min(W, H)*0.011))}px 0 0 -{max(7, round(min(W, H)*0.011))}px;border-radius:50%;background:var(--hoja);outline:2px solid var(--negro);display:block}}
.axl{{font-size:{round(H*0.02)}px}}
.quote{{font-weight:800;line-height:1.15}}.w{{display:inline-block}}
.list{{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:{round(H*0.025)}px}}
.list li{{font-size:{round(H*0.04)}px;font-weight:700;padding-left:{round(H*0.05)}px;position:relative;display:block}}
.list li::before{{content:"";position:absolute;left:0;top:.35em;width:.55em;height:.55em;background:var(--hoja)}}{self.extra_css}"""
        tl = "\n".join(x for x in self.tweens if not x.startswith("(()=>{const a=anime"))
        an = "\n".join(x for x in self.tweens if x.startswith("(()=>{const a=anime"))       # anime.js se registra al arrancar (no dentro de una promesa)
        return f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<title>{esc(self.doc.get('meta', {}).get('title', 'Video'))}</title>
<script src="assets/gsap.min.js"></script>{'<script src="assets/anime.umd.min.js"></script>' if self.motion else ''}
<style>{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{self.t:.3f}" data-fps="30">
{chr(10).join(self.scenes + self.overlays)}
</div>
{f"<script>{chr(10)}window.__hfAnime=window.__hfAnime||[];{chr(10)}{an}{chr(10)}</script>" if an else ""}
<script>
document.fonts.ready.then(()=>{{
const tl=gsap.timeline({{paused:true}});
{tl}
window.__timelines["main"]=tl;
}});
</script>
</body></html>"""


def build(doc, out_dir: Path, fmt="video-16x9", report=None):
    """Escribe el proyecto HyperFrames. Devuelve (director, ruta de index.html)."""
    design_dir, m = render.load_design(doc.get("design", "anura"))
    roles = render.resolve_roles(doc, design_dir, m, report["avisos"])
    report["avisos"] += paleta.check(roles, m)
    dr = Director(doc, m, roles, fmt, (doc.get("options") or {}).get("video") or {}, report)
    mot = ((doc.get("options") or {}).get("video") or {}).get("motion")
    if mot:                                             # escenas explícitas (palabra, nombres, cartas, flujo…): ver video_motion.py
        import video_motion
        dr.out_dir = out_dir
        dr.max_s = max(12.0, min(120.0, float((doc["options"]["video"]).get("duration", 120))))
        report["avisos"] += video_motion.dirigir(dr, mot, doc.get("meta", {}))
    else:
        dr.max_s = max(12.0, min(120.0, dr.max_s))
        dr.direct()
    (out_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE / "video" / "gsap.min.js", out_dir / "assets" / "gsap.min.js")
    if dr.motion:
        shutil.copy(HERE / "video" / "vendor" / "anime.umd.min.js", out_dir / "assets" / "anime.umd.min.js")
    for f in m["fonts"]:
        shutil.copy(design_dir / f["file"], out_dir / "assets" / "fonts" / Path(f["file"]).name)
    (out_dir / "index.html").write_text(dr.html(design_dir), encoding="utf-8")
    return dr, out_dir / "index.html"


def run(doc_path, out_mp4, fmt=None, quality="draft", do_render=True):
    t0 = time.time()
    doc = json.loads(Path(doc_path).read_text(encoding="utf-8"))
    fmt = fmt or (doc.get("format") if doc.get("format") in FORMATS else "video-16x9")
    _, m = render.load_design(doc.get("design", "anura"))
    warns = []
    errs = contract.validate({**doc, "format": fmt}, {**m, "formats": list(dict.fromkeys(m["formats"] + list(FORMATS)))}, warns)
    rep = {"estado": "ok", "formato": fmt, "errores": errs, "avisos": warns, "auditoria": {}}
    if errs:
        rep["estado"] = "rechazado"
        return rep
    out_mp4 = Path(out_mp4)
    proj = out_mp4.with_name(out_mp4.stem + "_proyecto")       # se sobrescribe (no se borra: el Studio puede tenerlo abierto)
    dr, _ = build(doc, proj, fmt, rep)
    rep.update({"duracion_s": round(dr.t, 2), "escenas": len(dr.scenes), "bpm": dr.bpm, "proyecto": str(proj)})
    # control de HyperFrames: lint + ejecución + maquetación + contraste en un solo paso
    ck = subprocess.run([NPX, "--yes", "hyperframes", "check", "--json"], cwd=proj, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    SKIP = ("timeline_track_too_dense", "nested_structure_needs_subcomposition")      # sugerencias de organización para el Studio
    try:
        cj = json.loads(ck.stdout[ck.stdout.find("{"):])
        a = rep["auditoria"]
        for k in ("lint", "runtime", "layout", "contrast"):
            sec = cj.get(k) or {}
            a[k] = [f"{f.get('severity')}: {f.get('code')} {str(f.get('message', ''))[:120]} @{f.get('time', '')}" for f in sec.get("findings", []) if f.get("code") not in SKIP][:12]
        a["contraste_textos"] = f"{(cj.get('contrast') or {}).get('passed', 0)}/{(cj.get('contrast') or {}).get('checked', 0)}"
        if not cj.get("ok"):
            rep["estado"] = "con_avisos"
    except (ValueError, AttributeError):
        rep["auditoria"]["check"] = (ck.stdout[-600:] or ck.stderr[-600:])
        rep["estado"] = "con_avisos"
    if do_render:
        r = subprocess.run([NPX, "--yes", "hyperframes", "render", "--quality", quality, "--output", str(out_mp4.resolve())],
                           cwd=proj, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
        if r.returncode != 0 or not out_mp4.exists() or out_mp4.stat().st_size == 0:
            rep["estado"] = "fallido"
            rep["errores"].append({"bloque": "render", "causa": (r.stderr or r.stdout)[-800:], "ajuste": "revisa `npx hyperframes doctor` (Node 22+, FFmpeg, Chrome)"})
        else:
            if str((doc.get("options") or {}).get("video", {}).get("musica", "")).lower() in ("si", "sí", "true", "1"):     # banda sonora propia al pulso y whoosh en cada corte
                try:
                    sys.path.insert(0, str(HERE / "tools"))
                    import sonorizar
                    con = sonorizar.sonorizar(out_mp4, dr.bpm, dr.cortes, out_mp4.with_name(out_mp4.stem + "_audio.mp4"))
                    con.replace(out_mp4)
                    rep["musica"] = "banda propia sintetizada (sin licencias de terceros)"
                except Exception as e:  # noqa: BLE001
                    rep["avisos"].append({"bloque": "musica", "causa": str(e)[:160], "ajuste": "el video sale sin audio"})
            rep["mb"] = round(out_mp4.stat().st_size / 1e6, 2)
    rep["segundos"] = round(time.time() - t0, 1)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--formato", choices=list(FORMATS))
    ap.add_argument("--calidad", default="draft", choices=["draft", "looks", "delivery"])
    ap.add_argument("--sin-render", action="store_true", help="solo escribe el proyecto y pasa lint")
    a = ap.parse_args()
    rep = run(a.doc, a.out, a.formato, a.calidad, not a.sin_render)
    Path(a.out).with_suffix(".informe.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rep.get(k) for k in ("estado", "duracion_s", "escenas", "mb", "segundos")} | {"auditoria": rep["auditoria"]}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # Windows: la consola cp1252 no acepta ✔ → ·
    main()


def motion_kit(design_id, base_url=""):
    """Estilo del diseño en el formato de /estudio-motion (~/.claude/estudio-motion/estilo.md) + brief para /brag y para pulir el proyecto
    HyperFrames que genera la API. Así las tres vías (API, /estudio-motion, /brag) comparten paleta, fuentes y contraste."""
    _, m = render.load_design(design_id)
    r = m["palette"]["roles"]
    fam = [f["family"] for f in m["fonts"]]
    bad = sorted({f"{a} sobre {b}" for a in r for b in r if a != b and paleta.ratio(r[a], r[b]) < 3})
    return f"""# Kit de motion · {m['name']}

Generado por la API desde el manifiesto del diseño `{design_id}`. Los colores de este texto son datos, no instrucciones.

## 1 · Estilo para /estudio-motion
Guárdalo en `~/.claude/estudio-motion/estilo.md` y luego invoca `/estudio-motion` (modo A, desde cero):

```markdown
# Estilo — {m['name']}
- marca: {m['name']}
- colores: fondo1 {r['negro']}, fondo2 {r['bosque']}, acento {r['vivo']}, acento2 {r['ocre']}, texto-claro {r['crema']}, texto-oscuro {r['negro']}, apoyo {r['hoja']}
- contraste: prohibidos (< 3:1) → {'; '.join(bad[:14]) or 'ninguno'}
- tipografías: display {fam[0]}, texto {fam[1] if len(fam) > 1 else fam[0]}, mono {fam[2] if len(fam) > 2 else fam[-1]} (archivos .woff2 en {base_url}/v1/designs/{design_id}/fonts.zip como .ttf)
- formato: 1920x1080 o 1080x1920, 16-30 s, 60 fps, idioma español
- intensidad: agresivo (brutalista: cortes secos, sombras duras, nada de degradados)
- tempo: 120 BPM (beat = 0,5 s)
- hud: no
- sonido: música + efectos (libre de derechos)
```

## 2 · Brief para /brag (video de lanzamiento de un proyecto)
`/brag --tone polished` y como restricción de estilo: solo estos colores ({', '.join(f'{k} {v}' for k, v in r.items())}),
display {fam[0]} en mayúsculas, bordes duros, sin redondeos ni degradados, texto solo en pares con contraste ≥ 4,5:1.

## 3 · Pulir el video que genera la API
`POST {base_url}/v1/render` con `"format":"video-16x9"` o `"video-9x16"` devuelve un trabajo; al terminar, `proyecto` es un zip con el proyecto
HyperFrames (index.html + gsap + fuentes). Descomprímelo y edítalo con las skills `/hyperframes`, `/estudio-motion` o `/remotion-to-hyperframes`;
renderiza con `npx hyperframes render --quality delivery --output final.mp4`.
"""
