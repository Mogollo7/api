# [CLAUDE-CONSTRUCTOR] Video «motion»: el Markdown :::motion llega a options.video.motion y el director construye una escena por línea, con la duración pedida.
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import render_video  # noqa: E402
import video_motion  # noqa: E402
from engine import markdown  # noqa: E402

MD = """---
titulo: Prueba
formato: video
estilo: editorial
duracion: 40
---

:::motion
palabra | Un solo motor | 2
nombres | A · B · C | 3 | MOTOR
cartas | a() · b() | 3
flujo | Uno → Dos → Tres | 4
contador | 94 % | menos tokens | 3
estados | Error → Corregido → Guardado | 3
final | Build once. | Connect any AI. | 3
:::
"""


class TestMotion(unittest.TestCase):
    def test_parse(self):
        ev = video_motion.parse(["palabra | Hola | 2", "nombres | A · B | 4 | CENTRO", "inventado | x | 1"])
        self.assertEqual([e["tipo"] for e in ev], ["palabra", "nombres"])
        self.assertEqual(ev[1]["extra"], "CENTRO")
        self.assertEqual(ev[1]["seg"], 4.0)

    def test_markdown_a_opciones(self):
        doc, av = markdown.a_contrato(MD)
        self.assertEqual(av, [])
        self.assertEqual(len(doc["options"]["video"]["motion"]), 7)
        self.assertEqual(doc["options"]["video"]["duration"], 40)

    def test_director_una_escena_por_linea(self):
        doc, _ = markdown.a_contrato(MD)
        rep = {"estado": "ok", "errores": [], "avisos": [], "auditoria": {}}
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)
            (out / "assets").mkdir()
            dr, idx = render_video.build(doc, out, "video-16x9", rep)
            self.assertEqual(len(dr.scenes), 7)
            self.assertAlmostEqual(dr.t, 21.0, delta=0.2)
            self.assertIn("window.__timelines", idx.read_text(encoding="utf-8"))

    def test_avisa_si_se_pasa(self):
        doc, _ = markdown.a_contrato(MD.replace("duracion: 40", "duracion: 12"))
        rep = {"estado": "ok", "errores": [], "avisos": [], "auditoria": {}}
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)
            (out / "assets").mkdir()
            render_video.build(doc, out, "video-16x9", rep)
        self.assertTrue(any("se omiten" in a["causa"] for a in rep["avisos"]))


if __name__ == "__main__":
    unittest.main()
