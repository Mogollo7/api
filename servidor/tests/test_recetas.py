# [CLAUDE-CONSTRUCTOR] Supermercado: cada receta sale completa con sus valores por defecto; los huecos se sustituyen; un hueco inventado avisa.
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import biblioteca  # noqa: E402
from engine import markdown, recetas  # noqa: E402


class TestRecetas(unittest.TestCase):
    def test_defectos_completos(self):
        for r in biblioteca.todos("receta"):
            md, av, _ = recetas.receta(r["id"])
            self.assertNotIn("{{", md, r["id"])
            self.assertEqual(av, [], r["id"])
            doc, av2 = markdown.a_contrato(md)
            self.assertEqual(av2, [], r["id"])
            self.assertTrue(doc["document"]["parts"], r["id"])

    def test_hueco_y_aviso(self):
        md, av, _ = recetas.receta("informe_negocio", {"titulo": "Mi informe", "inventado": 1, "medidas": ["Una", "Dos"]})
        self.assertIn("# Mi informe", md)
        self.assertIn("- Dos", md)
        self.assertEqual(len(av), 1)

    def test_compone(self):
        ing = biblioteca.todos("ingrediente")
        if ing:
            md, _ = recetas.componer([{"id": ing[0]["id"]}], {"titulo": "X"})
            self.assertTrue(md.startswith("---\ntitulo: X"))


if __name__ == "__main__":
    unittest.main()
