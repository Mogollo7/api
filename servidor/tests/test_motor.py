# [CLAUDE-CONSTRUCTOR] Pruebas del motor creadas por Claude. Ejecutar:  python -m unittest discover -s servidor/tests -v
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "tools"))

import render  # noqa: E402
from engine import blocks, charts, contract, diagram, paleta, text, variants  # noqa: E402

DD = HERE.parent / "designs/anura"
M = json.loads((DD / "manifest.json").read_text())
EJ = HERE / "ejemplo_minimo.json"
IMG = HERE.parent.parent / "teoria/imagenes"


class Texto(unittest.TestCase):
    def test_marcas(self):
        h = text.inline("**a** *b* `c` [FUENTE] dato pendiente <script>")
        for s in ("<b>a</b>", "<em>b</em>", "<code>c</code>", 'class="et f"', 'class="pend"'):
            self.assertIn(s, h)
        self.assertNotIn("<script>", h)

    def test_coma_decimal(self):
        self.assertEqual(text.num(62.85), "62,85")


class Contrato(unittest.TestCase):
    def doc(self):
        return json.loads(EJ.read_text())

    def test_valido(self):
        w = []
        self.assertEqual(contract.validate(self.doc(), M, w), [])
        self.assertEqual(w, [])

    def test_no_estandar_es_aviso_no_error(self):
        d, w = self.doc(), []
        d["document"]["parts"][0]["sections"][0]["blocks"].append({"type": "html", "text": "<b>x</b>"})
        self.assertEqual(contract.validate(d, M, w), [])
        self.assertTrue(any("vocabulario" in x["causa"] for x in w))

    def test_sin_portada_se_rechaza(self):
        d = self.doc()
        del d["document"]["cover"]
        self.assertTrue(contract.validate(d, M, []))


class Graficos(unittest.TestCase):
    R = M["palette"]["roles"]

    def test_todos_los_tipos_dibujan(self):
        datos = {
            "bar": {"items": [{"l": "a", "v": 1}]}, "hbar": {"items": [{"l": "a", "v": 1}]}, "line": {"points": [[1, 1], [2, 2]]},
            "stack": {"rows": [{"l": "a", "v": [1, 2, 3]}]}, "hist": {"bars": [[1, 2], [2, 3]]},
            "box": {"groups": [{"l": "a", "lo": 1, "q1": 2, "med": 3, "q3": 4, "hi": 5, "out": [9]}]}, "scatter": {"points": [[1, 1], [2, 3], [3, 2]], "trend": "auto"},
            "heat": {"labels": ["a", "b"], "matrix": [[1, .2], [.2, 1]]},
            "map": {"outline": "colombia", "points": [{"lon": -74, "lat": 4.7}]},
        }
        out = {}
        for t, d in datos.items():
            out[t] = charts.draw({"type": t, "data": d}, self.R, {"colombia": json.loads((DD / "geo/colombia.json").read_text())["poligonos"]})
            self.assertTrue(out[t].startswith("<svg"), t)

    def test_limites(self):
        with self.assertRaises(charts.ChartError):
            charts.draw({"type": "bar", "data": {"items": [{"l": str(i), "v": i} for i in range(30)]}}, self.R)

    def test_flowchart_ciclo_y_limite(self):
        n = [{"id": "a", "label": "A"}, {"id": "b", "label": "B", "kind": "decision"}]
        self.assertIn("polygon", diagram.draw({"nodes": n, "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a", "label": "no"}]}))
        with self.assertRaises(diagram.DiagramError):
            diagram.draw({"nodes": [{"id": str(i), "label": "x"} for i in range(15)], "edges": []})


class Paleta(unittest.TestCase):
    def test_anura_y_cine_sin_avisos_de_contraste(self):
        pals = json.loads((DD / "palettes.json").read_text())
        for k in ("anura", "cine"):
            r = dict(M["palette"]["roles"])
            r.update(pals[k])
            self.assertEqual([x for x in paleta.check(r, M) if "contraste" in x["causa"]], [], k)

    def test_detecta_gris_confundible(self):
        r = dict(M["palette"]["roles"])
        r.update({"hoja": "#7a7a7a", "vivo": "#7c7c7c"})
        self.assertTrue(any("hoja / vivo" in x["bloque"] for x in paleta.check(r, M)))


class Variantes(unittest.TestCase):
    def test_resolver(self):
        reg = variants.Registry(DD)
        w = []
        self.assertEqual(reg.resolve("portada", "auto", w), "CV-1")
        self.assertEqual(reg.resolve("portada", "CV-9", w), "CV-1")
        self.assertTrue(w)
        reg.set_state("DV-E", "rechazada")
        self.assertEqual(reg.resolve("divisor", "DV-E", w), "DV-A")


class Render(unittest.TestCase):
    def run_doc(self, p):
        with tempfile.TemporaryDirectory() as t:
            rep = render.run(p, Path(t) / "x.pdf", IMG)
            html = (Path(t) / "x.html").read_text(encoding="utf-8") if (Path(t) / "x.html").exists() else ""
            return rep, html

    def test_minimo_sin_problemas(self):
        rep, _ = self.run_doc(EJ)
        self.assertEqual(rep["errores"], [])
        self.assertEqual(rep["paginas"], 5)
        self.assertEqual(rep["auditoria"], {})

    def test_no_estandar_no_rompe(self):
        rep, html = self.run_doc(HERE / "no_estandar.json")
        self.assertEqual(rep["errores"], [])
        self.assertGreater(rep["paginas"], 3)
        self.assertEqual(rep["auditoria"], {})
        self.assertGreaterEqual(len(rep["avisos"]), 10)
        self.assertNotIn("<script>alert", html)
        self.assertNotIn("onclick", html)

    def test_correccion_de_contraste(self):
        d = json.loads(EJ.read_text())
        d["palette"] = {"hoja": "#bdbdbd"}   # texto en 'hoja' sobre papel: no se lee
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "d.json"
            p.write_text(json.dumps(d))
            rep = render.run(p, Path(t) / "x.pdf", IMG)
        self.assertTrue(rep["correcciones_contraste"])
        for c in rep["correcciones_contraste"]:
            self.assertGreaterEqual(c["ratio_despues"], 3)


class Comons(unittest.TestCase):
    def test_parse_sin_red(self):
        import commons
        resp = {"query": {"pages": {"1": {"title": "File:Rana.jpg", "imageinfo": [{"thumburl": "https://x/y.jpg", "descriptionurl": "https://c/Rana", "extmetadata": {
            "LicenseShortName": {"value": "CC BY-SA 4.0"}, "Artist": {"value": "<a>Ana</a>"}, "ImageDescription": {"value": "Una rana"}}}]},
            "2": {"title": "File:No.jpg", "imageinfo": [{"thumburl": "https://x/n.jpg", "extmetadata": {"LicenseShortName": {"value": "All rights reserved"}}}]}}}}
        r = commons.parse(resp)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["autor"], "Ana")


if __name__ == "__main__":
    unittest.main()
