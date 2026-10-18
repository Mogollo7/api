#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Video «motion»: escenas explícitas (palabra, nombres, cartas, flujo, contador, estados, final) para piezas tipo Brag. El agente las escribe en Markdown con :::motion.
"""Se activa con options.video.motion = [{tipo, texto, items?, extra?, seg}]; en Markdown:

    :::motion
    palabra | Un solo motor | 2
    nombres | Claude Code · Codex · OpenCode · tu agente | 4 | MOTOR
    cartas | list_recipes() · create_pdf() · audit() | 4
    flujo | Piensa → Elige → La API trabaja → Escala | 5
    contador | 94 % | menos tokens | 3
    estados | Error → Corregido → Guardado | 4
    final | Build once. | Connect any AI. | 4
    :::

Cada línea es una escena: tipo | texto o lista (separada por « · » o « → ») | segundos (o texto extra) | segundos. Colores y fuentes salen del diseño elegido (estilo:).
Una escena dura lo que dices (mín. 1,5 s, máx. 12 s). La duración total del video es la suma (máx. 120 s)."""
import math
import re

KINDS = ("palabra", "nombres", "cartas", "flujo", "contador", "estados", "final")
FONDOS = ["negro", "vivo", "crema", "bosque"]


def parse(lineas):
    out = []
    for ln in lineas:
        p = [x.strip() for x in ln.split("|")]
        if len(p) < 2 or p[0].lower() not in KINDS:
            continue
        e = {"tipo": p[0].lower(), "texto": p[1], "extra": None, "seg": None}
        for x in p[2:]:
            if re.fullmatch(r"\d+(?:[.,]\d+)?", x):
                e["seg"] = float(x.replace(",", "."))
            elif x:
                e["extra"] = x
        out.append(e)
    return out


def items(txt):
    return [x.strip() for x in re.split(r"\s*(?:·|→|->|;)\s*", txt) if x.strip()]


def dirigir(dr, escenas, meta):
    """Añade al director las escenas pedidas. Devuelve la lista de avisos."""
    avisos, total = [], 0.0
    esc, fit = dr.esc, dr.fit
    for n, e in enumerate(escenas):
        seg = max(1.5, min(12.0, e.get("seg") or {"palabra": 2.2, "nombres": 4, "cartas": 4, "flujo": 5, "contador": 3, "estados": 4, "final": 4}[e["tipo"]]))
        if total + seg > dr.max_s:
            avisos.append({"bloque": "video.motion", "causa": f"las escenas pasan de {dr.max_s:.0f} s; se omiten desde la {n + 1}", "ajuste": "sube `duracion` (máx. 120) o acorta las escenas"})
            break
        total += seg
        bars = seg / (4 * dr.beat)
        bg = FONDOS[n % len(FONDOS)] if e["tipo"] != "final" else "negro"
        ac = dr.acc(bg)
        t, b = e["texto"], dr.beat
        k = e["tipo"]
        if k == "palabra":
            px = fit(t.upper(), dr.W - 2 * dr.pad, 2, 330, 70)

            def body(s, t=t, px=px, ac=ac):
                return f'<div class="mw" id="{s}-w" style="font-size:{px}px">{esc(t.upper())}</div><div class="rule" id="{s}-r" style="color:var(--{ac})"></div>'
            dr.scene(bars, bg, body, lambda t0, d: [
                f'tl.fromTo("#$S-w",{{scale:1.7,opacity:0,filter:"blur(28px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:{min(0.7, d / 3):.3f},ease:"expo.out"}},{t0:.3f});',
                f'tl.fromTo("#$S-r",{{scaleX:0}},{{scaleX:1,duration:{min(0.6, d / 3):.3f},ease:"power4.inOut"}},{t0 + 0.35:.3f});'])
        elif k == "nombres":
            nom = items(t)[:8]
            hub = e.get("extra")
            cx, cy = dr.W / 2, dr.H / 2
            rx, ry = dr.W * 0.34, dr.H * 0.3
            pos = [(cx + rx * math.cos(-math.pi / 2 + 2 * math.pi * i / len(nom)), cy + ry * math.sin(-math.pi / 2 + 2 * math.pi * i / len(nom))) for i in range(len(nom))]
            fs = round(dr.H * 0.06)

            def body(s, nom=nom, hub=hub, pos=pos, fs=fs, ac=ac):
                h = f'<div class="hub" id="{s}-h" style="left:{cx:.0f}px;top:{cy:.0f}px;background:var(--{ac});color:var(--{bg})">{esc(hub)}</div>' if hub else ""
                return h + "".join(f'<div class="nm" id="{s}-n{i}" style="left:{x:.0f}px;top:{y:.0f}px;font-size:{fs}px;border-color:var(--{ac})">{esc(x_)}</div>' for i, ((x, y), x_) in enumerate(zip(pos, nom)))
            dr.scene(bars, bg, body, lambda t0, d, nom=nom, hub=hub: ([f'tl.fromTo("#$S-h",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:0.6,ease:"back.out(1.7)"}},{t0 + 0.1:.3f});'] if hub else []) + [
                f'tl.fromTo("#$S-n{i}",{{scale:2.2,opacity:0,filter:"blur(22px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:0.6,ease:"expo.out"}},{t0 + 0.5 + i * min(0.5, (d - 1.5) / max(1, len(nom))):.3f});' for i in range(len(nom))])
        elif k == "cartas":
            it = items(t)[:8]
            cols = 4 if len(it) > 4 and not dr.vert else (2 if dr.vert else min(len(it), 4))

            def body(s, it=it, cols=cols, ac=ac):
                c = "".join(f'<div class="cd" id="{s}-c{i}" style="border-color:var(--{ac})"><i class="dt" style="background:var(--{ac})"></i>{esc(x)}</div>' for i, x in enumerate(it))
                return f'<div class="cds" style="grid-template-columns:repeat({cols},1fr)">{c}</div>'
            dr.scene(bars, bg, body, lambda t0, d, it=it, ac=ac: [
                f'tl.fromTo("#$S-c{i}",{{y:90,rotation:{-5 + 10 * (i % 2)},opacity:0,scale:.8}},{{y:0,rotation:0,opacity:1,scale:1,duration:0.55,ease:"back.out(1.5)"}},{t0 + 0.2 + i * 0.16:.3f});' for i in range(len(it))] + [
                f'tl.to("#$S-c{i}",{{backgroundColor:"var(--{ac})",color:"var(--{bg})",scale:1.06,duration:0.2,ease:"power2.out"}},{t0 + 0.4 + len(it) * 0.16 + i * max(0.25, (d - 1.2 - len(it) * 0.16) / max(1, len(it))):.3f});'
                f'tl.to("#$S-c{i}",{{scale:1,duration:0.2}},{t0 + 0.6 + len(it) * 0.16 + i * max(0.25, (d - 1.2 - len(it) * 0.16) / max(1, len(it))):.3f});' for i in range(len(it))])
        elif k == "flujo":
            it = items(t)[:6]
            fs = round(dr.H * (0.045 if not dr.vert else 0.034))

            def body(s, it=it, fs=fs, ac=ac):
                parts = []
                for i, x in enumerate(it):
                    parts.append(f'<div class="fn" id="{s}-f{i}" style="font-size:{fs}px;border-color:var(--{ac})"><b>{i + 1:02d}</b>{esc(x)}</div>')
                    if i < len(it) - 1:
                        parts.append(f'<div class="fa" id="{s}-a{i}" style="background:var(--{ac})"></div>')
                return f'<div class="fl{" v" if dr.vert else ""}">{"".join(parts)}</div>'
            def tw(t0, d, it=it, ac=ac, bg=bg):
                g = max(0.3, (d - 1.0) / max(1, len(it)))
                out = []
                for i in range(len(it)):
                    out.append(f'tl.fromTo("#$S-f{i}",{{y:50,opacity:0}},{{y:0,opacity:1,duration:0.45,ease:"expo.out"}},{t0 + 0.2 + i * g:.3f});')
                    out.append(f'tl.to("#$S-f{i}",{{backgroundColor:"var(--{ac})",color:"var(--{bg})",duration:0.2}},{t0 + 0.5 + i * g:.3f});')
                    if i < len(it) - 1:
                        out.append(f'tl.fromTo("#$S-a{i}",{{scaleX:0}},{{scaleX:1,duration:0.3,ease:"power3.out"}},{t0 + 0.5 + i * g:.3f});')
                return out
            dr.scene(bars, bg, body, tw)
        elif k == "contador":
            lab = e.get("extra") or ""
            px = round(dr.H * 0.34)

            def body(s, t=t, lab=lab, px=px):
                return f'<div class="mw" id="{s}-v" style="font-size:{px}px">{esc(t)}</div><div class="ml" id="{s}-l">{esc(lab)}</div>'
            dr.scene(bars, bg, body, lambda t0, d, t=t: [
                f'tl.fromTo("#$S-l",{{y:30,opacity:0}},{{y:0,opacity:1,duration:0.5,ease:"power3.out"}},{t0 + 0.7:.3f});',
                dr.counter("#$S-v", t, t0 + 0.05, min(1.4, d * 0.5))])
        elif k == "estados":
            it = items(t)[:4]
            tonos = ["#ff3b4e", "#2ee66d", "#7aa2ff", "#ffd23f"]
            iconos = ["✕", "✓", "◆", "★"]

            def body(s, it=it):
                return '<div class="es">' + "".join(f'<div class="eb" id="{s}-e{i}" style="border-color:{tonos[i]}"><span class="ei" style="background:{tonos[i]};color:#0b0b0c">{iconos[i]}</span>{esc(x)}</div>' for i, x in enumerate(it)) + "</div>"
            dr.scene(bars, bg, body, lambda t0, d, it=it: [
                f'tl.fromTo("#$S-e{i}",{{x:-120,opacity:0}},{{x:0,opacity:1,duration:0.5,ease:"expo.out"}},{t0 + 0.3 + i * max(0.5, (d - 1.2) / max(1, len(it))):.3f});' for i in range(len(it))])
        elif k == "final":
            l2 = e.get("extra") or ""
            px = fit(t.upper(), dr.W - 2 * dr.pad, 1, 230, 70)
            px2 = fit(l2.upper(), dr.W - 2 * dr.pad, 1, 230, 70)

            def body(s, t=t, l2=l2, px=px, px2=px2, ac=ac):
                return (f'<div class="mw" id="{s}-a" style="font-size:{px}px">{esc(t.upper())}</div>'
                        f'<div class="mw" id="{s}-b" style="font-size:{px2}px;color:var(--{ac})">{esc(l2.upper())}</div>')
            dr.scene(bars, "negro", body, lambda t0, d: [
                f'tl.fromTo("#$S-a",{{x:-140,opacity:0}},{{x:0,opacity:1,duration:0.7,ease:"expo.out"}},{t0:.3f});',
                f'tl.fromTo("#$S-b",{{x:140,opacity:0,filter:"blur(18px)"}},{{x:0,opacity:1,filter:"blur(0px)",duration:0.8,ease:"expo.out"}},{t0 + 0.5:.3f});'])
    dr.extra_css += MOTION_CSS(dr)
    return avisos


def MOTION_CSS(dr):
    H, W = dr.H, dr.W
    d = dr.F["display"]
    return f"""
.mw{{font-family:"{d}",sans-serif;line-height:.9;text-transform:uppercase;letter-spacing:-.01em}}
.ml{{font-size:{round(H * 0.05)}px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}}
.hub{{position:absolute;transform:translate(-50%,-50%);padding:{round(H * 0.035)}px {round(H * 0.06)}px;border-radius:999px;font-family:"{d}",sans-serif;font-size:{round(H * 0.07)}px;letter-spacing:.04em}}
.nm{{position:absolute;transform:translate(-50%,-50%);padding:{round(H * 0.018)}px {round(H * 0.035)}px;border:4px solid;border-radius:999px;font-family:"{d}",sans-serif;text-transform:uppercase;white-space:nowrap}}
.cds{{display:grid;gap:{round(W * 0.014)}px;align-items:center}}
.cd{{border:4px solid;border-radius:{round(H * 0.012)}px;padding:{round(H * 0.035)}px {round(H * 0.025)}px;font-family:"{dr.F['mono']}",monospace;font-weight:600;font-size:{round(H * 0.036)}px;display:flex;align-items:center;gap:14px;min-height:{round(H * 0.2)}px}}
.dt{{display:inline-block;width:{round(H * 0.018)}px;height:{round(H * 0.018)}px;border-radius:50%;flex:none}}
.fl{{display:flex;align-items:center;gap:0}}.fl.v{{flex-direction:column}}
.fn{{border:4px solid;padding:{round(H * 0.03)}px {round(H * 0.025)}px;border-radius:{round(H * 0.01)}px;font-family:"{d}",sans-serif;text-transform:uppercase;display:flex;flex-direction:column;gap:10px;min-width:{round(W * 0.12)}px}}
.fn b{{font-family:"{dr.F['mono']}",monospace;font-size:.5em;opacity:.8}}
.fa{{height:6px;flex:1;min-width:{round(W * 0.02)}px;transform-origin:left center}}
.es{{display:flex;flex-direction:column;gap:{round(H * 0.03)}px}}
.eb{{border:5px solid;border-radius:{round(H * 0.012)}px;padding:{round(H * 0.025)}px {round(H * 0.035)}px;font-family:"{d}",sans-serif;font-size:{round(H * 0.07)}px;text-transform:uppercase;display:flex;align-items:center;gap:{round(H * 0.03)}px}}
.ei{{width:{round(H * 0.09)}px;height:{round(H * 0.09)}px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:.8em;flex:none}}
"""
