# [CLAUDE-CONSTRUCTOR] Código creado por Claude como constructor del servidor. El agente de contenido no lo escribe ni lo edita.
"""Registro de variantes de plantilla (designs/<id>/variantes.json) y su flujo de aprobación.

estado: propuesta | aprobada | rechazada.  'auto' elige la variante `defecto` del tipo, o la primera aprobada si hay.
Una variante rechazada no se usa (se avisa y se cae a la de por defecto). Usar una 'propuesta' funciona, pero queda anotada
en el informe (`variantes_no_aprobadas`) para que se apruebe o se descarte.
"""
import json
from pathlib import Path


class Registry:
    def __init__(self, design_dir: Path):
        self.path = Path(design_dir) / "variantes.json"
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.by_id = {v["id"]: v for v in self.data["variantes"]}
        self.used = {}

    def default(self, kind):
        vs = [v for v in self.data["variantes"] if v["tipo"] == kind and v["estado"] != "rechazada"]
        for v in vs:
            if v["estado"] == "aprobada" and v.get("defecto"):
                return v["id"]
        for v in vs:
            if v.get("defecto"):
                return v["id"]
        return vs[0]["id"] if vs else None

    def resolve(self, kind, wanted, warn, alias=None):
        """wanted puede ser un id completo ('DV-E'), una letra ('E') o 'auto'/None."""
        alias = alias or (lambda w: w)
        if wanted in (None, "auto"):
            vid = self.default(kind)
        else:
            vid = alias(wanted)
            v = self.by_id.get(vid)
            if not v or v["tipo"] != kind:
                warn.append({"bloque": f"variante {wanted}", "causa": f"no existe como {kind}", "ajuste": f"se usó {self.default(kind)}"})
                vid = self.default(kind)
            elif v["estado"] == "rechazada":
                warn.append({"bloque": vid, "causa": "variante rechazada", "ajuste": f"se usó {self.default(kind)}"})
                vid = self.default(kind)
        if vid:
            self.used[vid] = self.by_id[vid]["estado"]
        return vid

    def not_approved(self):
        return sorted(k for k, e in self.used.items() if e != "aprobada")

    def set_state(self, vid, estado):
        self.by_id[vid]["estado"] = estado

    def save(self):
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
