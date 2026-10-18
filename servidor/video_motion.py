#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Video «motion»: escenas explícitas para piezas tipo Brag, con fondo vivo (partículas, rejilla, trama, anillos, líneas), transiciones entre escenas,
# iconos que se dibujan solos (Lucide, ISC) y cámara que empuja. GSAP lleva la coreografía; anime.js (v4, posiciones sembradas) lleva las partículas y los trazos.
"""Se activa con options.video.motion = [{tipo, texto, extra?, seg}]; en Markdown:

    :::motion
    palabra   | Un solo motor | 2
    nombres   | Claude Code · Codex · OpenCode · tu agente | 4 | MOTOR
    cartas    | list_recipes() · create_pdf() · audit() | 4
    cerebro   | Primero piensa. | 3
    documento | La API hace el trabajo. | 4
    flujo     | Piensa → Elige → Trabaja → Escala | 5
    contador  | 94 % | menos tokens | 3
    estados   | Error → Corregido → Guardado → Aprende | 4
    final     | Build once. | Connect any AI. | 4
    nota      | Todo este video fue hecho con myStyle. | 3
    :::

Una línea = una escena: tipo | texto o lista (« · » o « → ») | [extra] | segundos (1,5–12). La suma no pasa de `duracion` (máx. 120 s).
Colores y fuentes salen del diseño (estilo:). Entre escenas entra una transición (persianas, barrido, bloques) que cubre el corte."""
import html as _html
import json
import math
import random
import re
from pathlib import Path

KINDS = ("palabra", "nombres", "cartas", "cerebro", "captura", "documento", "flujo", "contador", "estados", "final", "nota")
FONDOS = ["negro", "crema", "vivo", "negro", "ocre", "bosque"]
FX = ["particulas", "rejilla", "trama", "anillos", "lineas"]
TRANS = ["persianas", "barrido", "bloques"]
DUR = {"palabra": 2.5, "nombres": 4, "cartas": 4, "cerebro": 3.5, "documento": 4, "flujo": 4.5, "contador": 3, "estados": 4, "final": 4, "nota": 3, "captura": 3.5}
LUCIDE = Path(__file__).resolve().parent / "tools" / "node" / "node_modules" / "lucide-static" / "icons"
ICONOS = [("pdf", "file-text"), ("pptx", "presentation"), ("video", "video"), ("render", "layers"), ("audit", "shield-check"), ("quality", "badge-check"),
          ("search", "search"), ("librar", "book-open"), ("recipe", "chef-hat"), ("receta", "chef-hat"), ("compose", "layers"), ("patch", "wrench"),
          ("style", "sparkles"), ("estilo", "sparkles"), ("resource", "sparkles"), ("excel", "file-spreadsheet"), ("xlsx", "file-spreadsheet"), ("word", "file-text")]


def esc(s):
    return _html.escape(str(s), quote=True)


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


def icono(nombre, cls="ic"):
    """SVG de Lucide en línea, con pathLength=1 en cada trazo para dibujarlo (stroke-dashoffset 1 → 0)."""
    f = LUCIDE / f"{nombre}.svg"
    cuerpo = re.sub(r"<svg[^>]*>|</svg>|<!--.*?-->", "", f.read_text(encoding="utf-8"), flags=re.S) if f.exists() else '<rect x="3" y="3" width="18" height="18" rx="2"/>'
    cuerpo = re.sub(r"<(path|circle|rect|line|polyline|ellipse|polygon)\b", r'<\1 pathLength="1"', cuerpo)
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{cuerpo}</svg>'


def icono_de(txt):
    t = txt.lower()
    return next((ic for k, ic in ICONOS if k in t), "terminal")


def anime(js):
    """Una animación de anime.js registrada para que HyperFrames la busque (seek) en cada cuadro."""
    return f"(()=>{{const a={js};(window.__hfAnime=window.__hfAnime||[]).push(a)}})();"


def draw(sel, t0, dur=0.7, stagger=0.08):
    """Trazos que se dibujan (iconos y líneas con pathLength=1)."""
    return anime(f'anime.animate("{sel}",{{strokeDashoffset:[1,0],duration:{int(dur * 1000)},delay:anime.stagger({int(stagger * 1000)},{{start:{int(t0 * 1000)}}}),ease:"inOutQuad",autoplay:false}})')


def fondo(dr, kind, seed, ac, t0, d):
    """Capa de fondo viva. Posiciones sembradas en Python: el mismo cuadro en cada render."""
    rnd = random.Random(seed)
    W, H = dr.W, dr.H
    if kind == "particulas":
        pts = []
        for _ in range(46):
            s = rnd.choice((6, 8, 10, 14, 18))
            pts.append(f'<i class="pt" style="left:{rnd.uniform(0, W):.0f}px;top:{rnd.uniform(0, H):.0f}px;width:{s}px;height:{s}px;background:var(--{ac})" '
                       f'data-dx="{rnd.uniform(-90, 90):.0f}" data-dy="{rnd.uniform(-260, -60):.0f}" data-r="{rnd.choice((0, 45, 90))}"></i>')
        js = [anime(f'anime.animate("#$S .pt",{{x:el=>+el.dataset.dx,y:el=>+el.dataset.dy,rotate:el=>+el.dataset.r,opacity:[0,.7,.7,0],duration:{int(d * 1000)},delay:{int(t0 * 1000)},ease:"linear",autoplay:false}})')]
        return f'<div class="fx">{"".join(pts)}</div>', js
    if kind == "rejilla":
        return (f'<div class="fx"><div class="gr" style="color:var(--{ac})"></div><div class="scan" style="background:var(--{ac})"></div></div>',
                [anime(f'anime.animate("#$S .gr",{{y:[0,-120],opacity:[0,.2],duration:{int(d * 1000)},delay:{int(t0 * 1000)},ease:"linear",autoplay:false}})'),
                 anime(f'anime.animate("#$S .scan",{{x:[-200,{W + 200}],duration:{int(min(d, 2.4) * 1000)},delay:{int(t0 * 1000)},ease:"inOutSine",autoplay:false}})')])
    if kind == "trama":
        cols, rows = 24, 14
        dots = "".join(f'<i class="dt2" style="left:{(c + .5) * W / cols:.0f}px;top:{(r + .5) * H / rows:.0f}px;background:var(--{ac})"></i>' for r in range(rows) for c in range(cols))
        return (f'<div class="fx">{dots}</div>',
                [anime(f'anime.animate("#$S .dt2",{{scale:[0,1,.45],opacity:[0,.35,.15],duration:{int(min(d, 2.6) * 1000)},delay:anime.stagger(18,{{grid:[{cols},{rows}],from:"center",start:{int(t0 * 1000)}}}),ease:"outQuad",autoplay:false}})')])
    if kind == "anillos":
        rings = "".join(f'<i class="rg" style="border-color:var(--{ac})"></i>' for _ in range(5))
        return (f'<div class="fx">{rings}</div>',
                [anime(f'anime.animate("#$S .rg",{{scale:[.1,2.6],opacity:[.45,0],duration:{int(min(d, 2.8) * 1000)},delay:anime.stagger(380,{{start:{int(t0 * 1000)}}}),ease:"outQuad",autoplay:false}})')])
    bars = "".join(f'<i class="ln2" style="top:{rnd.uniform(0, H):.0f}px;height:{rnd.choice((4, 8, 16))}px;width:{rnd.uniform(.2, .7) * W:.0f}px;background:var(--{ac})"></i>' for _ in range(12))
    return (f'<div class="fx">{bars}</div>',
            [anime(f'anime.animate("#$S .ln2",{{x:[-{W},{W}],opacity:[0,.3,0],duration:{int(d * 1000)},delay:anime.stagger(90,{{start:{int(t0 * 1000)}}}),ease:"linear",autoplay:false}})')])


def letras(txt, cls="lt"):
    """Palabras con máscara y letras sueltas (entran letra a letra)."""
    return " ".join('<span class="wd">' + "".join(f'<span class="{cls}">{esc(ch)}</span>' for ch in w) + "</span>" for w in txt.split())


def transicion(dr, n, t_corte, kind, c1, c2):
    """Capa encima del corte entre dos escenas: cubre (0,3 s) y descubre (0,3 s). Va en su propio clip, encima de las escenas."""
    tid, W, H = f"tr{n}", dr.W, dr.H
    t0 = max(0.0, t_corte - 0.3)
    if kind == "persianas":
        k = 8
        body = "".join(f'<i class="tp" style="left:{i * W / k:.0f}px;width:{W / k + 2:.0f}px;background:var(--{c1 if i % 2 else c2})"></i>' for i in range(k))
        tw = [f'tl.fromTo("#{tid} .tp",{{scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,duration:.26,ease:"power3.in",stagger:.025}},{t0:.3f});',
              f'tl.fromTo("#{tid} .tp",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0,duration:.28,ease:"power3.out",stagger:.025,immediateRender:false}},{t_corte + .02:.3f});']
    elif kind == "barrido":
        body = f'<i class="tb" style="background:var(--{c1})"></i><i class="tb" style="background:var(--{c2})"></i>'
        tw = [f'tl.fromTo("#{tid} .tb",{{xPercent:-140,skewX:-18}},{{xPercent:140,skewX:-18,duration:.66,ease:"power3.inOut",stagger:.07}},{t0:.3f});']
    else:
        cols, rows = 12, 7
        body = "".join(f'<i class="tq" style="left:{c * W / cols:.0f}px;top:{r * H / rows:.0f}px;width:{W / cols + 1:.0f}px;height:{H / rows + 1:.0f}px;background:var(--{c1 if (r + c) % 3 else c2})"></i>'
                       for r in range(rows) for c in range(cols))
        tw = [f'tl.fromTo("#{tid} .tq",{{scale:0}},{{scale:1,duration:.24,ease:"power2.in",stagger:{{grid:[{rows},{cols}],from:"center",amount:.1}}}},{t0:.3f});',
              f'tl.fromTo("#{tid} .tq",{{scale:1}},{{scale:0,duration:.24,ease:"power2.out",stagger:{{grid:[{rows},{cols}],from:"edges",amount:.1}},immediateRender:false}},{t_corte + .02:.3f});']
    dr.overlays.append(f'<section id="{tid}" class="clip tr" data-start="{t0:.3f}" data-duration="0.68" data-track-index="3">{body}</section>')
    dr.tweens += tw


def _copiar_captura(dr, ruta):
    """Copia una captura (imagenes/… o una ruta del repositorio) al proyecto del video. Devuelve el src o None."""
    import shutil
    raiz = Path(__file__).resolve().parent.parent
    for f in (raiz / "imagenes" / ruta, raiz / ruta, raiz / "docs" / "media" / Path(ruta).name):
        if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and raiz in f.resolve().parents:
            dst = Path(dr.out_dir) / "assets" / "img"
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, dst / f.name)
            return f"assets/img/{f.name}"
    return None


def dirigir(dr, escenas, meta):
    """Añade al director las escenas pedidas (una por línea) y las transiciones entre ellas. Devuelve la lista de avisos."""
    avisos, total, cortes = [], 0.0, []
    fit = dr.fit
    W, H = dr.W, dr.H
    for n, e in enumerate(escenas):
        k = e["tipo"]
        seg = max(1.5, min(12.0, e.get("seg") or DUR[k]))
        if total + seg > dr.max_s:
            avisos.append({"bloque": "video.motion", "causa": f"las escenas pasan de {dr.max_s:.0f} s; se omiten desde la {n + 1}", "ajuste": "sube `duracion` (máx. 120) o acorta las escenas"})
            break
        total += seg
        bars = seg / (4 * dr.beat)
        bg = "negro" if k in ("final", "nota") else FONDOS[n % len(FONDOS)]
        ac = dr.acc(bg)
        t = e["texto"]
        fxk = FX[n % len(FX)]
        semilla = 1000 + n * 37

        def con_fondo(contenido, fxk=fxk, ac=ac, semilla=semilla, seg=seg):
            def body(s):
                fx_html, _ = fondo(dr, fxk, semilla, ac, 0, seg)
                return fx_html + f'<div class="ct" id="{s}-ct">{contenido(s)}</div>'
            return body

        def tw_fondo(t0, d, fxk=fxk, ac=ac, semilla=semilla):
            _, js = fondo(dr, fxk, semilla, ac, t0, d)
            return js + [f'tl.fromTo("#$S-ct",{{scale:1}},{{scale:1.045,duration:{d:.3f},ease:"none"}},{t0:.3f});']   # la cámara empuja despacio

        if k == "palabra":
            larga = max(t.upper().split(), key=len) if t.split() else t
            px = min(fit(t.upper(), (W - 2 * dr.pad) * .8, 2, 280, 80),      # margen: Anton es más ancha que la estimación
                     fit(larga + "  ", (W - 2 * dr.pad) * .8, 1, 280, 60))   # la palabra más larga cabe entera en una línea
            pal = t.split()
            ok = "vivo" if bg != "vivo" else "negro"                       # la última palabra termina «aprobada»: caja verde y check

            def cont(s, pal=pal, px=px, ac=ac, bg=bg, ok=ok):
                cuerpo = letras(" ".join(pal[:-1]).upper())
                if pal:
                    cuerpo += (f' <span class="wd hlw" id="{s}-hw" style="color:var(--{bg})"><span class="hl" id="{s}-hl" style="background:var(--{ac})"></span>'
                               + "".join(f'<span class="lt">{esc(ch)}</span>' for ch in pal[-1].upper()) + "</span>"
                               + f'<span class="okc" id="{s}-ok" style="color:var(--{ok})">{icono("circle-check", "ic okic")}</span>')
                return f'<div class="mw" style="font-size:{px}px">{cuerpo}</div><div class="rule" id="{s}-r" style="color:var(--{ac})"></div>'

            def tw(t0, d, ok=ok, ac=ac, tw_fondo=tw_fondo):
                out = tw_fondo(t0, d) + [
                    f'tl.fromTo("#$S .lt",{{yPercent:115,rotation:8}},{{yPercent:0,rotation:0,duration:.5,ease:"expo.out",stagger:.025}},{t0 + .05:.3f});',
                    f'tl.fromTo("#$S-hl",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"power4.inOut"}},{t0 + .45:.3f});',
                    f'tl.fromTo("#$S-r",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"power4.inOut"}},{t0 + .55:.3f});']
                ta = t0 + min(1.0, d * .45)
                if ok != ac:
                    out.append(f'tl.to("#$S-hl",{{backgroundColor:"var(--{ok})",duration:.25,ease:"power2.out"}},{ta:.3f});')
                    out.append(f'tl.to("#$S-hw",{{color:"var(--{"negro" if ok == "vivo" else "vivo"})",duration:.25}},{ta:.3f});')
                out.append(f'tl.fromTo("#$S-ok",{{scale:0,rotation:-40}},{{scale:1,rotation:0,duration:.4,ease:"back.out(2)"}},{ta + .05:.3f});')
                out.append(draw("#$S-ok .okic *", ta + .1, .4, .08))
                return out
            dr.scene(bars, bg, con_fondo(cont), tw)
        elif k == "nombres":
            nom = items(t)[:6]
            hub = e.get("extra") or "MOTOR"
            cx, cy = W / 2, H * .5
            rx, ry = W * .36, H * .33
            pos = [(cx + rx * math.cos(-math.pi / 2 + 2 * math.pi * i / len(nom)), cy + ry * math.sin(-math.pi / 2 + 2 * math.pi * i / len(nom))) for i in range(len(nom))]
            AG = {"claude": "square-terminal", "codex": "code-xml", "opencode": "braces", "antigravity": "rocket", "agente": "user"}
            ics = [next((v for k2, v in AG.items() if k2 in x.lower()), "bot") for x in nom]
            fs = round(H * .046)

            def cont(s, nom=nom, hub=hub, pos=pos, fs=fs, ac=ac, bg=bg, ics=ics):
                wires = "".join(f'<path pathLength="1" d="M{x:.0f},{y:.0f} L{cx:.0f},{cy:.0f}"/>' for x, y in pos)
                h = (f'<div class="hub2" id="{s}-h" style="left:{cx:.0f}px;top:{cy:.0f}px;background:var(--{ac});color:var(--{bg})">{icono("server", "ic hic")}'
                     f'<div><b>{esc(hub)}</b><small class="mono">MCP · HTTP · CLI</small></div></div>'
                     f'<i class="pulse" id="{s}-pu" style="left:{cx:.0f}px;top:{cy:.0f}px;border-color:var(--{ac})"></i>')
                pk = "".join(f'<i class="pk" id="{s}-k{i}" style="left:{x:.0f}px;top:{y:.0f}px;background:var(--{ac})"></i>' for i, (x, y) in enumerate(pos))
                chips = "".join(f'<div class="ag" id="{s}-n{i}" style="left:{x:.0f}px;top:{y:.0f}px;font-size:{fs}px;border-color:var(--{ac})">'
                                f'<span class="agi" style="background:var(--{ac});color:var(--{bg})">{icono(ic, "ic nic")}</span><span>{esc(x_)}</span></div>'
                                for i, ((x, y), x_, ic) in enumerate(zip(pos, nom, ics)))
                return f'<svg class="wires" viewBox="0 0 {W} {H}" style="color:var(--{ac})">{wires}</svg>' + pk + h + chips

            def tw(t0, d, nom=nom, pos=pos, tw_fondo=tw_fondo):
                g = min(.35, (d - 2.4) / max(1, len(nom)))
                out = tw_fondo(t0, d)
                out.append(f'tl.fromTo("#$S-h",{{xPercent:-50,yPercent:-50,scale:0,rotation:-8}},{{xPercent:-50,yPercent:-50,scale:1,rotation:0,duration:.55,ease:"back.out(1.8)"}},{t0 + .1:.3f});')
                out.append(draw("#$S-h .hic *", t0 + .25, .5, 0))
                for i, (x, y) in enumerate(pos):
                    ti = t0 + .45 + i * g
                    out.append(f'tl.fromTo("#$S-n{i}",{{xPercent:-50,yPercent:-50,scale:2.2,opacity:0,filter:"blur(22px)"}},{{xPercent:-50,yPercent:-50,scale:1,opacity:1,filter:"blur(0px)",duration:.5,ease:"expo.out"}},{ti:.3f});')
                    out.append(draw(f"#$S-n{i} .nic *", ti + .2, .45, 0))
                    out.append(draw(f"#$S .wires path:nth-child({i + 1})", ti + .25, .45, 0))
                    for r in range(3):                                   # paquetes que viajan del agente al motor
                        tp = ti + .7 + r * .55
                        if tp + .5 < t0 + d - .2:
                            out.append(f'tl.fromTo("#$S-k{i}",{{x:0,y:0,opacity:1,scale:1}},{{x:{cx - x:.0f},y:{cy - y:.0f},opacity:.2,scale:.5,duration:.5,ease:"power1.in",immediateRender:false}},{tp:.3f});')
                out.append(f'tl.fromTo("#$S-pu",{{scale:.5,opacity:.9}},{{scale:3.4,opacity:0,duration:.8,ease:"power2.out",repeat:2}},{t0 + .7 + len(nom) * g:.3f});')
                return out
            dr.scene(bars, bg, con_fondo(cont), tw)
        elif k == "cartas":
            it = items(t)[:8]
            cols = 4 if len(it) > 4 else (min(len(it), 4) or 1)
            rnd = random.Random(semilla)
            dirs = [(rnd.choice((-1, 1)) * rnd.uniform(200, 500), rnd.uniform(200, 420), rnd.uniform(-14, 14)) for _ in it]

            def cont(s, it=it, cols=cols, ac=ac):
                c = "".join(f'<div class="cd" id="{s}-c{i}" style="border-color:var(--{ac})">{icono(icono_de(x), "ic cic")}<span>{esc(x)}</span></div>' for i, x in enumerate(it))
                return f'<div class="cds" style="grid-template-columns:repeat({cols},1fr)">{c}</div>'

            def tw(t0, d, it=it, ac=ac, bg=bg, dirs=dirs, tw_fondo=tw_fondo):
                g = max(.25, (d - 1.4 - len(it) * .12) / max(1, len(it)))
                out = tw_fondo(t0, d)
                for i, (dx, dy, rot) in enumerate(dirs):
                    out.append(f'tl.fromTo("#$S-c{i}",{{x:{dx:.0f},y:{dy:.0f},rotation:{rot:.1f},opacity:0}},{{x:0,y:0,rotation:0,opacity:1,duration:.55,ease:"back.out(1.4)"}},{t0 + .1 + i * .12:.3f});')
                    out.append(draw(f"#$S-c{i} .cic *", t0 + .3 + i * .12, .5, 0))
                    tt = t0 + .9 + len(it) * .12 + i * g
                    out.append(f'tl.to("#$S-c{i}",{{backgroundColor:"var(--{ac})",color:"var(--{bg})",scale:1.07,duration:.18,ease:"power2.out"}},{tt:.3f});')
                    out.append(f'tl.to("#$S-c{i}",{{scale:1,duration:.22,ease:"power2.inOut"}},{tt + .2:.3f});')
                return out
            dr.scene(bars, bg, con_fondo(cont), tw)
        elif k == "cerebro":
            rnd = random.Random(semilla)
            cx, cy = W * .5, H * .36
            nodes = [(cx, cy)] + [(cx + rnd.uniform(-1, 1) * W * .38, cy + rnd.uniform(-1, 1) * H * .22) for _ in range(26)]
            radios = [22] + [rnd.choice((7, 9, 12)) for _ in nodes[1:]]
            edges = [(a, b) for a in range(len(nodes)) for b in range(a + 1, len(nodes)) if math.dist(nodes[a], nodes[b]) < W * .16][:60]
            px = fit(t.upper(), W - 2 * dr.pad, 1, 140, 60)

            def cont(s, nodes=nodes, radios=radios, edges=edges, ac=ac, px=px, t=t):
                ln = "".join(f'<line pathLength="1" x1="{nodes[a][0]:.0f}" y1="{nodes[a][1]:.0f}" x2="{nodes[b][0]:.0f}" y2="{nodes[b][1]:.0f}"/>' for a, b in edges)
                nd = "".join(f'<circle class="nd" cx="{x:.0f}" cy="{y:.0f}" r="{r}"/>' for (x, y), r in zip(nodes, radios))
                ring = f'<circle class="rn" cx="{nodes[0][0]:.0f}" cy="{nodes[0][1]:.0f}" r="40" pathLength="1"/>'
                return (f'<svg class="net" viewBox="0 0 {W} {H}" style="color:var(--{ac})">{ln}{nd}{ring}</svg>'
                        f'<div class="mw cap2" id="{s}-t" style="font-size:{px}px">{esc(t.upper())}</div>')
            dr.scene(bars, bg, con_fondo(cont), lambda t0, d, tw_fondo=tw_fondo: tw_fondo(t0, d) + [
                anime(f'anime.animate("#$S .nd",{{scale:[0,1.5,1],duration:600,delay:anime.stagger(35,{{from:"first",start:{int((t0 + .1) * 1000)}}}),ease:"outBack",autoplay:false}})'),
                draw("#$S .net line", t0 + .2, .45, .02),
                draw("#$S .net .rn", t0 + .3, .6, 0),
                anime(f'anime.animate("#$S .nd",{{opacity:[1,.3,1],duration:650,loop:2,delay:anime.stagger(45,{{from:"first",start:{int((t0 + 1.1) * 1000)}}}),ease:"inOutSine",autoplay:false}})'),
                f'tl.fromTo("#$S-t",{{y:80,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"expo.out"}},{t0 + .6:.3f});'])
        elif k == "captura":
            src = _copiar_captura(dr, t)
            lab = e.get("extra") or ""
            px = fit(lab.upper(), W * .3, 4, 120, 50)

            def cont(s, src=src, lab=lab, px=px, ac=ac):
                img = f'<img src="{src}" alt="">' if src else '<div class="nocap"></div>'
                return (f'<div class="capw"><div class="mw capt" id="{s}-t" style="font-size:{px}px">{letras(lab.upper())}</div>'
                        f'<div class="capi" id="{s}-i" style="box-shadow:22px 22px 0 var(--{ac})">{img}</div></div>')
            dr.scene(bars, bg, con_fondo(cont), lambda t0, d, tw_fondo=tw_fondo: tw_fondo(t0, d) + [
                f'tl.fromTo("#$S-i",{{x:420,rotationY:-28,opacity:0,transformPerspective:1600}},{{x:0,rotationY:-8,opacity:1,duration:.7,ease:"expo.out",transformPerspective:1600}},{t0 + .05:.3f});',
                f'tl.fromTo("#$S-i img",{{scale:1,yPercent:0}},{{scale:1.08,yPercent:-3,duration:{d:.3f},ease:"none"}},{t0:.3f});',
                f'tl.fromTo("#$S .lt",{{yPercent:115}},{{yPercent:0,duration:.45,ease:"expo.out",stagger:.02}},{t0 + .3:.3f});'])
        elif k == "documento":
            rnd = random.Random(semilla)
            widths = [rnd.uniform(.55, .95) for _ in range(7)]
            px = fit(t.upper(), W * .42, 3, 140, 56)

            def cont(s, widths=widths, ac=ac, px=px, t=t):
                lines = "".join(f'<i class="dl" style="width:{w * 100:.0f}%"></i>' for w in widths)
                barras = "".join(f'<i class="db" style="height:{h}%;background:var(--{ac})"></i>' for h in (45, 70, 55, 92))
                return (f'<div class="docw"><div class="mw dtxt" id="{s}-t" style="font-size:{px}px">{esc(t.upper())}</div>'
                        f'<div class="doc" id="{s}-d"><div class="dh" style="background:var(--{ac})"></div>{lines}<div class="dch">{barras}</div>'
                        f'<div class="stamp" id="{s}-st" style="color:var(--{ac});border-color:var(--{ac})">{icono("check", "ic sic")}<b>PDF</b></div></div></div>')
            dr.scene(bars, bg, con_fondo(cont), lambda t0, d, tw_fondo=tw_fondo: tw_fondo(t0, d) + [
                f'tl.fromTo("#$S-t",{{x:-120,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"expo.out"}},{t0 + .05:.3f});',
                f'tl.fromTo("#$S-d",{{y:220,rotation:6,opacity:0}},{{y:0,rotation:-2,opacity:1,duration:.6,ease:"back.out(1.3)"}},{t0 + .15:.3f});',
                f'tl.fromTo("#$S .dh",{{scaleX:0}},{{scaleX:1,duration:.35,ease:"power3.out"}},{t0 + .6:.3f});',
                f'tl.fromTo("#$S .dl",{{scaleX:0}},{{scaleX:1,duration:.28,ease:"power2.out",stagger:.12}},{t0 + .8:.3f});',
                f'tl.fromTo("#$S .db",{{scaleY:0}},{{scaleY:1,duration:.4,ease:"back.out(1.6)",stagger:.1}},{t0 + 1.7:.3f});',
                f'tl.fromTo("#$S-st",{{scale:2.6,rotation:-25,opacity:0}},{{scale:1,rotation:-12,opacity:1,duration:.35,ease:"power4.in"}},{t0 + min(d - .9, 2.4):.3f});',
                draw("#$S-st .sic *", t0 + min(d - .6, 2.7), .35, 0)])
        elif k == "flujo":
            it = items(t)[:6]
            fs = round(H * 0.04)

            def cont(s, it=it, fs=fs, ac=ac):
                parts = []
                for i, x in enumerate(it):
                    parts.append(f'<div class="fn" id="{s}-f{i}" style="font-size:{fs}px;border-color:var(--{ac})">{icono(["brain", "search", "zap", "layers", "sparkles", "check"][i % 6], "ic fic")}<b>{i + 1:02d}</b><span>{esc(x)}</span></div>')
                    if i < len(it) - 1:
                        parts.append(f'<div class="fa" id="{s}-a{i}" style="background:var(--{ac});color:var(--{ac})"><i></i></div>')
                return f'<div class="fl">{"".join(parts)}</div>'

            def tw(t0, d, it=it, ac=ac, bg=bg, tw_fondo=tw_fondo):
                g = max(.35, (d - 1.0) / max(1, len(it)))
                out = tw_fondo(t0, d)
                for i in range(len(it)):
                    out.append(f'tl.fromTo("#$S-f{i}",{{y:70,opacity:0,scale:.85}},{{y:0,opacity:1,scale:1,duration:.45,ease:"back.out(1.6)"}},{t0 + .15 + i * g:.3f});')
                    out.append(draw(f"#$S-f{i} .fic *", t0 + .3 + i * g, .45, 0))
                    out.append(f'tl.to("#$S-f{i}",{{backgroundColor:"var(--{ac})",color:"var(--{bg})",duration:.2}},{t0 + .55 + i * g:.3f});')
                    if i < len(it) - 1:
                        out.append(f'tl.fromTo("#$S-a{i}",{{scaleX:0}},{{scaleX:1,duration:.3,ease:"power3.out",transformOrigin:"left center"}},{t0 + .6 + i * g:.3f});')
                return out
            dr.scene(bars, bg, con_fondo(cont), tw)
        elif k == "contador":
            lab = e.get("extra") or ""
            px = round(H * 0.36)

            def cont(s, t=t, lab=lab, px=px, ac=ac):
                return (f'<div class="cnt"><div class="mw" id="{s}-v" style="font-size:{px}px">{esc(t)}</div>'
                        f'<div class="ml" id="{s}-l"><i class="mk" id="{s}-mk" style="background:var(--{ac})"></i>{esc(lab)}</div></div>')
            dr.scene(bars, bg, con_fondo(cont), lambda t0, d, t=t, tw_fondo=tw_fondo: tw_fondo(t0, d) + [
                f'tl.fromTo("#$S-v",{{scale:.6,opacity:0,filter:"blur(20px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:.6,ease:"expo.out"}},{t0:.3f});',
                dr.counter("#$S-v", t, t0 + .05, min(1.4, d * .5)),
                f'tl.fromTo("#$S-mk",{{scaleX:0}},{{scaleX:1,duration:.4,ease:"power4.inOut"}},{t0 + .6:.3f});',
                f'tl.fromTo("#$S-l",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.45,ease:"power3.out"}},{t0 + .7:.3f});'])
        elif k == "estados":
            it = items(t)[:4]
            tonos = ["#ff3b4e", "#2ee66d", "#7aa2ff", "#ffd23f"]
            ics = ["circle-x", "circle-check", "database", "sparkles"]

            def cont(s, it=it):
                return '<div class="es">' + "".join(f'<div class="eb" id="{s}-e{i}" style="border-color:{tonos[i]}"><span class="ei" style="color:{tonos[i]}">{icono(ics[i], "ic eic")}</span><span>{esc(x)}</span></div>'
                                                   for i, x in enumerate(it)) + "</div>"

            def tw(t0, d, it=it, tw_fondo=tw_fondo):
                g = max(.5, (d - 1.0) / max(1, len(it)))
                out = tw_fondo(t0, d)
                for i in range(len(it)):
                    out.append(f'tl.fromTo("#$S-e{i}",{{x:-160,opacity:0,skewX:-12}},{{x:0,opacity:1,skewX:0,duration:.45,ease:"expo.out"}},{t0 + .15 + i * g:.3f});')
                    out.append(draw(f"#$S-e{i} .eic *", t0 + .3 + i * g, .5, 0))
                    if i == 0:
                        out.append(f'tl.to("#$S-e0",{{x:14,duration:.06,repeat:5,yoyo:true,ease:"none"}},{t0 + .7:.3f});')   # el error tiembla
                return out
            dr.scene(bars, bg, con_fondo(cont), tw)
        elif k == "final":
            l2 = e.get("extra") or ""
            px = fit(t.upper(), W - 2 * dr.pad, 1, 230, 70)
            px2 = fit(l2.upper(), W - 2 * dr.pad, 1, 230, 70)

            def cont(s, t=t, l2=l2, px=px, px2=px2, ac=ac):
                return (f'<div class="mw" style="font-size:{px}px">{letras(t.upper())}</div>'
                        f'<div class="mw l2" style="font-size:{px2}px;color:var(--{ac})">{letras(l2.upper(), "lt2")}</div><div class="rule" id="{s}-r" style="color:var(--{ac})"></div>')
            dr.scene(bars, "negro", con_fondo(cont), lambda t0, d, tw_fondo=tw_fondo: tw_fondo(t0, d) + [
                f'tl.fromTo("#$S .lt",{{yPercent:115}},{{yPercent:0,duration:.5,ease:"expo.out",stagger:.03}},{t0 + .05:.3f});',
                f'tl.fromTo("#$S .lt2",{{yPercent:-115}},{{yPercent:0,duration:.5,ease:"expo.out",stagger:.03}},{t0 + .55:.3f});',
                f'tl.fromTo("#$S-r",{{scaleX:0}},{{scaleX:1,duration:.6,ease:"power4.inOut"}},{t0 + 1.0:.3f});'])
        elif k == "nota":
            def cont(s, t=t, ac=ac):
                return f'<div class="nota"><span class="mono">{"".join(f"<span class=ch>{esc(c)}</span>" for c in t)}</span><i class="caret" id="{s}-c" style="background:var(--{ac})"></i></div>'
            dr.scene(bars, "negro", con_fondo(cont), lambda t0, d, t=t, tw_fondo=tw_fondo: tw_fondo(t0, d) + [
                f'tl.fromTo("#$S .ch",{{opacity:0}},{{opacity:1,duration:.01,stagger:{min(.045, (d - 1.2) / max(1, len(t))):.3f}}},{t0 + .2:.3f});',
                f'tl.fromTo("#$S-c",{{opacity:1}},{{opacity:0,duration:.25,repeat:{max(1, int(d * 2) - 1)},yoyo:true,ease:"steps(1)"}},{t0:.3f});'])
        cortes.append((dr.t, bg))
    for i, (tc, _) in enumerate(cortes[:-1]):                           # una transición en cada corte, sin la última escena
        nxt = cortes[i + 1][1]
        a = dr.acc(nxt)
        transicion(dr, i + 1, tc, TRANS[i % len(TRANS)], a if a != nxt else "vivo", "negro" if nxt != "negro" else "crema")
    dr.motion = True
    dr.extra_css += MOTION_CSS(dr)
    dr.cortes = [round(c[0], 3) for c in cortes]
    return avisos


def MOTION_CSS(dr):
    H, W = dr.H, dr.W
    d = dr.F["display"]
    m = dr.F["mono"]
    return f"""
.fx{{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:0}}
.ct{{position:relative;z-index:1;display:flex;flex-direction:column;justify-content:center;gap:{round(H * .03)}px;height:100%;transform-origin:50% 50%}}
.pt{{position:absolute;display:block;opacity:0}}
.gr{{position:absolute;left:0;right:0;top:0;height:{H + 240}px;background-image:linear-gradient(currentColor 2px,transparent 2px),linear-gradient(90deg,currentColor 2px,transparent 2px);background-size:120px 120px;opacity:0}}
.scan{{position:absolute;top:0;bottom:0;width:140px;opacity:.18;filter:blur(30px)}}
.dt2{{position:absolute;display:block;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:50%;opacity:0}}
.rg{{position:absolute;left:50%;top:50%;width:{round(H * .5)}px;height:{round(H * .5)}px;margin:-{round(H * .25)}px 0 0 -{round(H * .25)}px;border:6px solid;border-radius:50%;opacity:0;display:block}}
.ln2{{position:absolute;left:0;display:block;opacity:0}}
.ic{{display:block;flex:none}}.ic *{{stroke-dasharray:1;stroke-dashoffset:1}}
.mw{{font-family:"{d}",sans-serif;line-height:.92;text-transform:uppercase;letter-spacing:-.01em}}
.wd{{display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:.04em;position:relative}}.lt,.lt2{{display:inline-block}}
.hlw .lt{{position:relative;z-index:1}}.hl{{position:absolute;left:-.06em;right:-.06em;top:.08em;bottom:.02em;transform-origin:left center;z-index:0;display:block}}
.ml{{font-size:{round(H * .05)}px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;display:flex;align-items:center;gap:22px}}
.mk{{display:block;width:{round(H * .09)}px;height:{round(H * .02)}px;transform-origin:left center}}
.wires{{position:absolute;inset:0;width:100%;height:100%;fill:none;stroke:currentColor;stroke-width:4}}.wires line{{stroke-dasharray:1;stroke-dashoffset:1}}
.hub{{position:absolute;display:flex;align-items:center;gap:18px;padding:{round(H * .03)}px {round(H * .05)}px;border-radius:999px;font-family:"{d}",sans-serif;font-size:{round(H * .065)}px;letter-spacing:.04em;z-index:2}}
.hic{{width:{round(H * .07)}px;height:{round(H * .07)}px}}
.pulse{{position:absolute;width:{round(H * .2)}px;height:{round(H * .2)}px;margin:-{round(H * .1)}px 0 0 -{round(H * .1)}px;border:5px solid;border-radius:50%;opacity:0;display:block}}
.nm{{position:absolute;display:flex;align-items:center;gap:14px;padding:{round(H * .016)}px {round(H * .03)}px;border:5px solid;font-family:"{d}",sans-serif;text-transform:uppercase;white-space:nowrap;box-shadow:10px 10px 0 currentColor;z-index:2}}
.nic{{width:1em;height:1em}}
.cds{{display:grid;gap:{round(W * .016)}px;align-items:stretch}}
.cd{{border:5px solid;padding:{round(H * .032)}px {round(H * .026)}px;font-family:"{m}",monospace;font-weight:600;font-size:{round(H * .034)}px;display:flex;flex-direction:column;gap:18px;min-height:{round(H * .2)}px;box-shadow:12px 12px 0 currentColor}}
.cic{{width:{round(H * .07)}px;height:{round(H * .07)}px}}
.net{{position:absolute;inset:0;width:100%;height:100%;stroke:currentColor;stroke-width:3;fill:none}}.net line{{stroke-dasharray:1;stroke-dashoffset:1}}.net .nd{{fill:currentColor;stroke:none;transform-box:fill-box;transform-origin:center}}
.brain{{position:absolute;width:{round(H * .26)}px;height:{round(H * .26)}px}}.bic{{width:100%;height:100%}}
.cap2{{position:absolute;left:0;right:0;bottom:0;text-align:center}}
.docw{{display:grid;grid-template-columns:1fr {round(W * .3)}px;gap:{round(W * .05)}px;align-items:center}}
.doc{{position:relative;background:#fff;color:#121212;border:6px solid #121212;box-shadow:18px 18px 0 #121212;padding:{round(H * .04)}px;display:flex;flex-direction:column;gap:{round(H * .018)}px;height:{round(H * .62)}px}}
.dh{{height:{round(H * .05)}px;transform-origin:left center}}.dl{{display:block;height:{round(H * .016)}px;background:#121212;opacity:.75;transform-origin:left center}}
.dch{{flex:1;display:flex;align-items:flex-end;gap:14px;border-bottom:4px solid #121212}}.db{{flex:1;display:block;transform-origin:bottom center;border:3px solid #121212}}
.stamp{{position:absolute;right:{round(W * .02)}px;bottom:{round(H * .05)}px;display:flex;align-items:center;gap:10px;padding:10px 18px;border:6px solid;background:#121212;font-family:"{d}",sans-serif;font-size:{round(H * .06)}px}}
.sic{{width:{round(H * .06)}px;height:{round(H * .06)}px;stroke-width:3}}
.fl{{display:flex;align-items:center}}
.fn{{border:5px solid;padding:{round(H * .03)}px {round(H * .024)}px;font-family:"{d}",sans-serif;text-transform:uppercase;display:flex;flex-direction:column;gap:12px;min-width:{round(W * .13)}px;box-shadow:10px 10px 0 currentColor}}
.fn b{{font-family:"{m}",monospace;font-size:.5em;opacity:.8}}.fic{{width:{round(H * .06)}px;height:{round(H * .06)}px}}
.fa{{position:relative;height:8px;flex:1;min-width:{round(W * .02)}px;transform-origin:left center}}.fa i{{position:absolute;right:-14px;top:-10px;border-top:14px solid transparent;border-bottom:14px solid transparent;border-left:18px solid currentColor;display:block;width:0;height:0}}
.es{{display:flex;flex-direction:column;gap:{round(H * .026)}px}}
.eb{{border:6px solid;padding:{round(H * .022)}px {round(H * .034)}px;font-family:"{d}",sans-serif;font-size:{round(H * .072)}px;text-transform:uppercase;display:flex;align-items:center;gap:{round(H * .03)}px;box-shadow:12px 12px 0 currentColor}}
.ei{{display:flex}}.eic{{width:{round(H * .085)}px;height:{round(H * .085)}px;stroke-width:2.6}}
.cnt{{display:flex;flex-direction:column;gap:20px}}
.l2{{margin-top:-.05em}}
.nota{{display:flex;align-items:center;justify-content:center;gap:16px;height:100%;font-size:{round(H * .045)}px;white-space:nowrap}}
.nota .mono{{letter-spacing:.06em;text-transform:none;font-weight:600}}
.caret{{display:inline-block;width:{round(H * .03)}px;height:{round(H * .06)}px}}
.okc{{display:inline-block;width:.62em;height:.62em;margin-left:.14em;vertical-align:.08em}}.okic{{width:100%;height:100%;stroke-width:2.6}}
.hub2{{position:absolute;display:flex;align-items:center;gap:22px;padding:{round(H * .03)}px {round(H * .045)}px;border:6px solid #121212;box-shadow:14px 14px 0 #121212;font-family:"{d}",sans-serif;z-index:3}}
.hub2 b{{display:block;font-weight:400;font-size:{round(H * .07)}px;line-height:1;letter-spacing:.03em}}.hub2 small{{display:block;font-size:{round(H * .022)}px;margin-top:8px;letter-spacing:.14em}}
.ag{{position:absolute;display:flex;align-items:center;gap:16px;padding:{round(H * .012)}px {round(H * .024)}px {round(H * .012)}px {round(H * .012)}px;border:5px solid;font-family:"{d}",sans-serif;text-transform:uppercase;white-space:nowrap;box-shadow:10px 10px 0 currentColor;z-index:2}}
.agi{{display:flex;padding:10px}}.ag .nic{{width:1.05em;height:1.05em}}
.pk{{position:absolute;width:16px;height:16px;margin:-8px 0 0 -8px;display:block;opacity:0;z-index:1}}
.wires path{{stroke-dasharray:1;stroke-dashoffset:1}}
.net .rn{{fill:none;stroke:currentColor;stroke-width:4;stroke-dasharray:1;stroke-dashoffset:1}}
.capw{{display:grid;grid-template-columns:{round(W * .3)}px 1fr;gap:{round(W * .04)}px;align-items:center;height:100%}}
.capi{{overflow:hidden;border:6px solid #121212;background:#121212}}.capi img{{display:block;width:100%;height:auto;transform-origin:50% 30%}}
.nocap{{height:{round(H * .5)}px}}
.tr{{pointer-events:none;overflow:hidden}}.tp,.tq{{position:absolute;display:block}}.tp{{top:0;bottom:0}}
.tb{{position:absolute;top:-20%;bottom:-20%;left:-15%;width:130%;display:block}}
"""
