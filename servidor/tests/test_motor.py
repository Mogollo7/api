# [CLAUDE-CONSTRUCTOR] Pruebas del motor creadas por Claude. Ejecutar:  python -m unittest discover -s servidor/tests -v
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import render  # noqa: E402
from engine import contract, text  # noqa: E402

M = json.loads((HERE.parent / "designs/anura/manifest.json").read_text())
EJ = HERE / "ejemplo_minimo.json"


class Texto(unittest.TestCase):
    def test_marcas(self):
        h = text.inline("**a** *b* `c` [FUENTE] dato pendiente <script>")
        self.assertIn("<b>a</b>", h)
        self.assertIn("<em>b</em>", h)
        self.assertIn("<code>c</code>", h)
        self.assertIn('class="et f"', h)
        self.assertIn('class="pend"', h)
        self.assertNotIn("<script>", h)

    def test_coma_decimal(self):
        self.assertEqual(text.num(62.85), "62,85")


class Contrato(unittest.TestCase):
    def doc(self):
        return json.loads(EJ.read_text())

    def test_valido(self):
        self.assertEqual(contract.validate(self.doc(), M), [])

    def test_bloque_desconocido(self):
        d = self.doc()
        d["document"]["parts"][0]["sections"][0]["blocks"].append({"type": "html", "text": "<b>x</b>"})
        e = contract.validate(d, M)
        self.assertEqual(len(e), 1)
        self.assertIn("vocabulario", e[0]["causa"])

    def test_fila_desigual(self):
        d = self.doc()
        d["document"]["parts"][0]["sections"][1]["blocks"].append({"type": "table", "head": ["a", "b"], "rows": [["1"]]})
        self.assertTrue(any("celdas" in x["causa"] for x in contract.validate(d, M)))


class Render(unittest.TestCase):
    def test_pdf_sin_problemas_de_auditoria(self):
        with tempfile.TemporaryDirectory() as t:
            rep = render.run(EJ, Path(t) / "x.pdf", HERE.parent.parent / "teoria/imagenes")
            self.assertEqual(rep["errores"], [])
            self.assertEqual(rep["paginas"], 1 + 1 + 3)  # portada, divisor, 3 hojas
            self.assertEqual(rep["auditoria"], {})
            self.assertEqual(len(rep["imagenes_necesarias"]), 1)  # el ejemplo pide una imagen que no existe


if __name__ == "__main__":
    unittest.main()
