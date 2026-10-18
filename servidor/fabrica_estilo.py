#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Fábrica de estilos: un acento (o 7 colores) + una «piel» → diseño completo con 4 variantes, sin escribir CSS a mano.
"""python servidor/fabrica_estilo.py estilo <id> --acento "#C2410C" [--piel suave|recta|redonda|editorial] [--modo claro|oscuro] [--nombre "…"] [--paleta JSON con los 7 roles]
python servidor/fabrica_estilo.py variante <id> --tipo portada|divisor --fondo acento|claro|oscuro --nuevo CV-3 [--nombre "…"]

Parte del diseño `prompt-master` (4 variantes, una sola fuente Archivo), recolorea su capa CSS con la paleta derivada del acento y añade la piel
(radio, trazo, sombra, peso y mayúsculas de títulos). Después corre `validar_diseno.py <id>` y debe salir todo ✔ (la fábrica lo ejecuta y lo informa).
Lo que no cubre una piel (formas nuevas, fuentes nuevas) sigue siendo trabajo de diseño: ver designs/LEEME.md."""
import argparse
import colorsys
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "prompt-master"
PIELES = {  # radio y trazo en cqw; sombra CSS; peso de títulos; mayúsculas
    "suave": dict(radio=1.2, trazo=.2, sombra="none", peso=800, mayus=False, desc="esquinas suaves, trazo fino (el SaaS de prompt-master)"),
    "recta": dict(radio=0, trazo=.35, sombra="none", peso=900, mayus=True, desc="esquinas rectas, trazo grueso, títulos en mayúsculas"),
    "redonda": dict(radio=2.6, trazo=0, sombra="0 .5cqw 2cqw rgba(0,0,0,.10)", peso=800, mayus=False, desc="muy redondeada, sin trazo, con sombra suave"),
    "editorial": dict(radio=.3, trazo=.15, sombra="none", peso=700, mayus=False, desc="casi recta, trazo fino, títulos de peso medio"),
}


def hexa(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, max(0, min(1, l)), max(0, min(1, s)))
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def paleta_desde(acento):
    r, g, b = (int(acento[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    vivo = hexa(h, s, min(l, .45))                  # el acento se oscurece si hace falta para que el texto claro sobre él pase el contraste
    return {"negro": "#0B0B0C", "bosque": hexa(h, min(s, .45), .10), "hoja": hexa(h, s, max(.18, min(l, .45) - .12)), "vivo": vivo,
            "ocre": hexa(h, min(s, .6), .92), "crema": "#FFFFFF", "arena": hexa(h, min(s, .4), .96)}


def paleta_oscura(acento):
    """Tema oscuro = se invierte la claridad de cada rol (tinta clara, papel casi negro, panel claro, línea oscura): los pares de texto permitidos siguen valiendo."""
    r, g, b = (int(acento[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return {"negro": hexa(h, .15, .95), "crema": hexa(h, min(s, .5), .06), "arena": hexa(h, min(s, .4), .10), "bosque": hexa(h, min(s, .6), .88), "ocre": hexa(h, min(s, .5), .20),
            "vivo": hexa(h, s, .72), "hoja": hexa(h, s, .58)}


def rgb(h):
    return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))


def estilo(a):
    dst, src = HERE / "designs" / a.id, HERE / "designs" / BASE
    if dst.exists():
        sys.exit(f"ya existe {dst}")
    oscuro = a.modo == "oscuro"
    pal = (paleta_oscura if oscuro else paleta_desde)(a.acento) if a.acento else {}
    pal.update(json.loads(a.paleta) if a.paleta else {})
    if len(pal) < 7:
        sys.exit("da --acento '#rrggbb' o una --paleta con los 7 roles")
    piel = PIELES[a.piel]
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".cache", "__pycache__", "_*.json"))
    m = json.loads((dst / "manifest.json").read_text(encoding="utf-8"))
    m.update({"id": a.id, "name": a.nombre or a.id, "version": "0.1.0", "base": BASE, "estado": "propuesta", "estilo": a.piel, "modo": a.modo,
              "_marca": f"[CLAUDE-CONSTRUCTOR] Diseño '{a.id}' generado por fabrica_estilo.py (acento {pal['vivo']}, piel {a.piel}) desde '{BASE}'."})
    m["palette"]["roles"] = pal
    (dst / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    (dst / "palettes.json").write_text(json.dumps({"_marca": f"Paletas del diseño {a.id}.", a.id: pal}, ensure_ascii=False, indent=2), encoding="utf-8")
    v = json.loads((dst / "variantes.json").read_text(encoding="utf-8"))
    for x in v["variantes"]:
        x["estado"] = "propuesta"
        x["origen"] = f"fabrica_estilo ({a.piel})"
    (dst / "variantes.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    css = (dst / "extras.css").read_text(encoding="utf-8")
    for viejo, nuevo in (("#7C3AED", pal["vivo"]), ("#F2E6F8", pal["ocre"]), ("#E3DFEA", pal["ocre"]), ("#D9D3E3", pal["ocre"])):   # recoloreo de la capa SaaS
        css = css.replace(viejo, nuevo).replace(viejo.lower(), nuevo)
    if oscuro:                                                                          # grises fijos de la capa SaaS → grises claros
        css = css.replace("#6B6B72", "#A1A1AA").replace("#3f3f46", "#D4D4D8")
    css = css.replace("rgba(124,58,237", f"rgba({rgb(pal['vivo'])}").replace("rgba(242,230,248", f"rgba({rgb(pal['ocre'])}").replace("rgba(167,139,250", f"rgba({rgb(pal['ocre'])}")
    css += f"""
/* ----- piel «{a.piel}»: {piel['desc']} ----- */
.kpi,.kpi>div,.stats>div,.co,.ch,.tab,.cmp .col,.flow .st,.ladder .rg{{border-radius:{piel['radio']}cqw;border-width:{piel['trazo']}cqw;box-shadow:{piel['sombra']}}}
.lp h3,.lp h3.sec,.ps-title,.ps-ttl,.kpi b,.bigd .big{{font-weight:{piel['peso']};{'text-transform:uppercase;' if piel['mayus'] else ''}}}
"""
    (dst / "extras.css").write_text(css, encoding="utf-8")
    (dst / "LEEME_DISENO.md").write_text(f"# Diseño {a.id} (fábrica)\n\nAcento {pal['vivo']}, piel «{a.piel}» ({piel['desc']}). Regenerable: `python servidor/fabrica_estilo.py estilo {a.id} --acento {a.acento or pal['vivo']} --piel {a.piel}`.\n"
                                         f"Variantes nuevas: `python servidor/fabrica_estilo.py variante {a.id} --tipo portada --fondo acento --nuevo CV-3`.\n", encoding="utf-8")
    print(f"creado {dst}")
    valida(a.id)


def variante(a):
    dd = HERE / "designs" / a.id
    es_p = a.tipo == "portada"
    modelo = dd / "templates" / ("cover.CV-1.html" if es_p else "divider.DV-A.html")
    cls_old = "ps-c1" if es_p else "ps-dA"
    c = "ps-x" + a.nuevo.lower().replace("-", "")
    (dd / "templates" / f"{'cover' if es_p else 'divider'}.{a.nuevo}.html").write_text(modelo.read_text(encoding="utf-8").replace(cls_old, c), encoding="utf-8")
    f = {"acento": ("var(--vivo)", "var(--crema)", "var(--ocre)"), "oscuro": ("var(--bosque)", "var(--crema)", "var(--ocre)"), "claro": ("var(--arena)", "var(--negro)", "#3f3f46")}[a.fondo]
    css = f"\n/* variante {a.nuevo} ({a.fondo}) */\n.{c}{{background:{f[0]};color:{f[1]}}}\n.{c} .ps-sub,.{c} .ps-desc,.{c} .ps-ver,.{c} .ps-hd,.{c} .ps-foot{{color:{f[2]}}}\n"
    if a.fondo == "acento":
        css += f".{c} .ps-eye i,.{c}::before{{background:{f[1]}}}\n.{c} .ps-num{{color:{f[1]}}}\n"
    with (dd / "extras.css").open("a", encoding="utf-8") as fh:
        fh.write(css)
    vf = dd / "variantes.json"
    v = json.loads(vf.read_text(encoding="utf-8"))
    v["variantes"].append({"id": a.nuevo, "tipo": a.tipo, "nombre": a.nombre or f"{a.tipo.capitalize()} fondo {a.fondo}", "uso": f"{a.tipo.capitalize()} con fondo {a.fondo}, generada por fabrica_estilo.py.",
                           "estado": "propuesta", "defecto": False, "origen": "fabrica_estilo", "nivel": "organismo"})
    vf.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    m = json.loads((dd / "manifest.json").read_text(encoding="utf-8"))          # símbolos de la portada: los de CV-1
    sbv = m["templates"].get("cover", {}).get("symbols_by_variant")
    if es_p and isinstance(sbv, dict):
        sbv[a.nuevo] = m["templates"]["cover"]["symbols"]
        (dd / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"variante {a.nuevo} añadida a {a.id}")
    valida(a.id)


def valida(i):
    r = subprocess.run([sys.executable, str(HERE / "validar_diseno.py"), i, "--rapido"], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=HERE.parent)
    sal = [ln for ln in r.stdout.splitlines() if ln.strip()]
    print("\n".join(sal[-14:]))
    print("VALIDACIÓN:", "todo ✔" if r.returncode == 0 and "✘" not in r.stdout else "hay ✘ (ver arriba)")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("estilo")
    e.add_argument("id")
    e.add_argument("--acento")
    e.add_argument("--paleta")
    e.add_argument("--piel", default="suave", choices=list(PIELES))
    e.add_argument("--modo", default="claro", choices=["claro", "oscuro"], help="oscuro: papel casi negro y tinta clara")
    e.add_argument("--nombre")
    v = sp.add_parser("variante")
    v.add_argument("id")
    v.add_argument("--tipo", required=True, choices=["portada", "divisor"])
    v.add_argument("--fondo", required=True, choices=["acento", "claro", "oscuro"])
    v.add_argument("--nuevo", required=True)
    v.add_argument("--nombre")
    a = ap.parse_args()
    (estilo if a.cmd == "estilo" else variante)(a)


if __name__ == "__main__":
    main()
