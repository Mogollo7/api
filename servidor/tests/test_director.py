# [CLAUDE-CONSTRUCTOR] Pruebas de la capa del director: biblioteca, Markdown, ids estables, correcciones, auditoría y herramientas.
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import auditar  # noqa: E402
import biblioteca  # noqa: E402
import correcciones  # noqa: E402
import herramientas  # noqa: E402
from engine import contract, ids, markdown  # noqa: E402

EJ = HERE / "ejemplo_minimo.json"
MD = """---
titulo: Plan de prueba
objetivo: Probar la conversión
estilo: anura
formato: pptx
---
## Cifras
Texto con **negrita**.
:::kpi
- 80 % de aciertos
150 kg | de residuos
:::
| Uso | kWh |
|---|---|
| Climatización | 1 600 |
| Luz | 900 |
{grafico: bar}
- uno
  - sub
- dos
> [!NOTA] Ojo
![pie de foto](img/a.png "El pie")
"""


class Biblioteca(unittest.TestCase):
    def test_busca_por_similitud(self):
        r = biblioteca.buscar("cifras clave", "componente", n=5)
        self.assertTrue(any(x["id"] == "kpi" for x in r))
        self.assertTrue(biblioteca.buscar("aparecer subiendo", "animacion")[0]["id"] == "fade-up")

    def test_ficha_con_skill_corto(self):
        e = biblioteca.obtener("kpi", "componente")
        self.assertIn("skill", e)
        self.assertLessEqual(len(e["skill"].splitlines()), 40)               # «máximo una pantalla»

    def test_guardar_versiona_y_no_pisa(self):
        d0 = biblioteca.DIR
        with tempfile.TemporaryDirectory() as t:
            biblioteca.DIR = Path(t)
            try:
                e = {"tipo": "estilo", "id": "azul-test", "nombre": "Azul", "descripcion": "estilo azul"}
                self.assertEqual(biblioteca.guardar(e)["version"], "1")
                with self.assertRaisesRegex(ValueError, "ya existe"):
                    biblioteca.guardar(e)
                self.assertEqual(biblioteca.guardar({**e, "descripcion": "estilo azul v2"}, sobrescribir=True)["version"], "2")
                self.assertTrue((Path(t) / "estilos" / "_versiones" / "azul-test@1.json").exists())
                with self.assertRaises(ValueError):
                    biblioteca.guardar({"tipo": "estilo", "id": "../x", "nombre": "a", "descripcion": "b"})
            finally:
                biblioteca.DIR = d0


class Markdown(unittest.TestCase):
    def test_asigna_bloques_y_valida(self):
        doc, av = markdown.a_contrato(MD)
        self.assertEqual((doc["design"], doc["format"]), ("anura", "pptx-16x9"))
        tipos = [b["type"] for p in doc["document"]["parts"] for s in p["sections"] for b in s["blocks"]]
        self.assertEqual(tipos, ["p", "kpi", "chart", "list", "callout", "image"])
        kpi = doc["document"]["parts"][0]["sections"][0]["blocks"][1]["items"]
        self.assertEqual([k["v"] for k in kpi], ["80 %", "150 kg"])
        m = json.loads((HERE.parent / "designs/anura/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(contract.validate(doc, m, []), [])

    def test_cuerpo_gana_sobre_cabecera(self):
        doc, _ = markdown.expandir({"markdown": MD, "design": "editorial", "format": "pdf-a4"})
        self.assertEqual((doc["design"], doc["format"]), ("editorial", "pdf-a4"))


class Ids(unittest.TestCase):
    def test_ids_deterministas_y_parche_por_id(self):
        import api
        doc = json.loads(EJ.read_text(encoding="utf-8"))
        a, b = ids.asegurar(doc), ids.asegurar(doc)
        self.assertEqual(a, b)
        sec = a["document"]["parts"][0]["sections"][0]
        bid = sec["blocks"][0]["id"]
        api.apply_patch(a, [{"op": "set", "section": sec["id"], "block": bid, "value": {"type": "p", "text": "cambiado"}}])
        self.assertEqual(sec["blocks"][0]["text"], "cambiado")
        self.assertEqual(sec["blocks"][0]["id"], bid)                         # conserva la identidad
        with self.assertRaises(ValueError):
            api.apply_patch(a, [{"op": "delete", "section": sec["id"], "block": "no-existe"}])


class Correcciones(unittest.TestCase):
    def test_guardar_buscar_y_dataset(self):
        a0 = correcciones.ARCHIVO
        with tempfile.TemporaryDirectory() as t:
            correcciones.ARCHIVO = Path(t) / "c.jsonl"
            try:
                with self.assertRaises(ValueError):
                    correcciones.guardar({"seccion": "s1"})                  # sin motivo no se aprende nada
                correcciones.guardar({"seccion": "s1.kpi", "antes": {"v": 1}, "despues": {"v": 2}, "motivo": "la cifra principal no tenía nota de fuente"})
                self.assertEqual(correcciones.buscar("cifra sin nota fuente")[0]["seccion"], "s1.kpi")
                self.assertEqual(correcciones.dataset(Path(t) / "d.jsonl"), 1)
            finally:
                correcciones.ARCHIVO = a0


class Auditoria(unittest.TestCase):
    def test_detecta_margen_solape_contraste(self):
        import pymupdf
        d = pymupdf.open()
        p = d.new_page()
        p.insert_text((10, 30), "pegado al borde", fontsize=12)
        p.insert_text((100, 200), "Titular uno largo", fontsize=20)
        p.insert_text((110, 205), "texto encima", fontsize=20)
        p.insert_text((60, 335), "gris claro", fontsize=14, color=(.85, .85, .85))
        r = auditar.auditar(datos=d.tobytes())
        for k in ("margen", "solape", "contraste"):
            self.assertGreaterEqual(r["resumen"][k], 1, k)


class Herramientas(unittest.TestCase):
    def test_perfil_minimo_ofrece_markdown(self):
        mini = {t["function"]["name"]: t["function"]["parameters"] for t in herramientas.openai_tools(core_only=True)}
        self.assertIn("create_pdf", mini)
        self.assertNotIn("document", mini["create_pdf"]["properties"])
        self.assertIn("markdown", mini["create_pdf"]["required"])
        self.assertLess(len(mini), len(herramientas.openai_tools()))
        self.assertEqual({t["name"] for t in herramientas.mcp_tools()}, {t["name"] for t in herramientas.TOOLS})


class FuentesPorRol(unittest.TestCase):
    def test_font_roles_del_manifiesto(self):
        from engine import assets
        roles = {"negro": "#000000"}
        self.assertIn('--font-display:"Anton"', assets.root_css(roles))                       # sin font_roles: valores históricos
        css = assets.root_css(roles, {"font_roles": {"display": "Archivo", "mono": "Archivo"}})
        self.assertIn('--font-display:"Archivo"', css)
        self.assertIn('--font-mono:"Archivo"', css)


class Tokens(unittest.TestCase):
    def test_forma_de_tokens_json(self):
        f = HERE.parent / "web" / "stats" / "tokens.json"
        if not f.exists():
            self.skipTest("genera servidor/web/stats/tokens.json con servidor/tools/tokens.py")
        d = json.loads(f.read_text(encoding="utf-8"))
        for k in ("metodo_conteo", "estimado", "factor_iteraciones", "formatos", "estilo_nuevo", "agentes", "documentos"):
            self.assertIn(k, d)
        for fmt in ("pdf", "pptx", "docx", "xlsx", "video"):
            v = d["formatos"][fmt]
            self.assertLess(v["con"]["min"], v["sin"]["max"])
            self.assertTrue(all(isinstance(v["con"][x], int) for x in ("media", "min", "max")))
            self.assertLessEqual(v["ahorro_pct"], 100)


class PresetsVideo(unittest.TestCase):
    def test_entrada_y_aviso_de_preset_desconocido(self):
        import render_video
        doc = json.loads((HERE.parent.parent / "contenido" / "informe_ventas.json").read_text(encoding="utf-8"))
        res = {}
        for ent in ("slide", "wipe-reveal", "no-existe"):
            d = {**doc, "format": "video-16x9", "options": {"video": {"entrada": ent}}}
            rep = {"avisos": [], "estado": "ok", "errores": [], "auditoria": {}}
            with tempfile.TemporaryDirectory() as t:
                _, idx = render_video.build(d, Path(t), "video-16x9", rep)
                res[ent] = (idx.read_text(encoding="utf-8").count("inset(0 100%"), [a for a in rep["avisos"] if "preset" in a["causa"]])
        self.assertGreater(res["wipe-reveal"][0], res["slide"][0])
        self.assertEqual(len(res["no-existe"][1]), 1)
        self.assertEqual(res["no-existe"][0], res["slide"][0])               # cae al preset por defecto


if __name__ == "__main__":
    unittest.main()
