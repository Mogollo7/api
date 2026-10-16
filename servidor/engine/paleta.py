# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Revisión de una paleta ANTES de dibujar: contraste de los pares de texto permitidos y distancia en grises entre colores que
se usan para distinguir series (hoja, vivo, arena, negro, crema). Si dos se confunden en escala de grises, avisa."""
import math


def _rgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def lum(h):
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def lstar(h):
    y = lum(h)
    return 116 * (y ** (1 / 3)) - 16 if y > 0.008856 else 903.3 * y


def ratio(a, b):
    x, y = lum(a) + 0.05, lum(b) + 0.05
    return max(x, y) / min(x, y)


def check(roles: dict, manifest: dict) -> list:
    out = []
    mn = manifest["palette"].get("min_contraste_texto", 4.5)
    for fg, bg in manifest["palette"]["pares_texto_permitidos"]:
        r = ratio(roles[fg], roles[bg])
        if r < mn:
            out.append({"bloque": f"paleta {fg} sobre {bg}", "causa": f"contraste {r:.1f}:1 (mínimo {mn})", "ajuste": "oscurece o aclara uno de los dos roles, o saca el par de uso"})
    series = ["negro", "hoja", "vivo", "arena", "crema"]
    for i, a in enumerate(series):
        for b in series[i + 1:]:
            d = abs(lstar(roles[a]) - lstar(roles[b]))
            if d < 12 and {a, b} != {"arena", "crema"}:
                out.append({"bloque": f"paleta {a} / {b}", "causa": f"solo {d:.0f} puntos de claridad (L*) de diferencia: se confunden en escala de grises",
                            "ajuste": "no los uses juntos como series distintas; añade borde negro o diferencia la claridad"})
    return out
