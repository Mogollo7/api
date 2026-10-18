# [CLAUDE-CONSTRUCTOR] Identificadores de bloque estables: los parches y las correcciones apuntan a `sección.bloque` sin depender del índice.
"""asegurar(doc): pone `id` a cada bloque que no lo tenga (determinista: mismo contenido → mismo id). Un bloque con id propio lo conserva."""
import hashlib
import json


def asegurar(doc):
    """Devuelve el documento con ids de bloque (copia superficial; no muta la entrada)."""
    try:
        parts = doc["document"]["parts"]
    except (KeyError, TypeError):
        return doc
    usados = set()
    for p in parts:
        for s in p.get("sections", []):
            for b in s.get("blocks", []):
                if isinstance(b, dict) and b.get("id"):
                    usados.add(str(b["id"]))
    out = json.loads(json.dumps(doc))
    for p in out["document"]["parts"]:
        for s in p.get("sections", []):
            for i, b in enumerate(s.get("blocks", [])):
                if not isinstance(b, dict) or b.get("id"):
                    continue
                h = hashlib.sha1((str(s.get("id")) + json.dumps(b, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()[:5]
                bid, n = f"{b.get('type', 'b')}-{h}", 1
                while bid in usados:
                    n += 1
                    bid = f"{b.get('type', 'b')}-{h}{n}"
                usados.add(bid)
                b["id"] = bid
    return out


def indice(doc, sec, block):
    """Posición de un bloque dentro de su sección: `block` puede ser un entero (índice), su texto o un id estable."""
    bl = sec.get("blocks", [])
    if isinstance(block, int) or (isinstance(block, str) and block.lstrip("-").isdigit()):
        return int(block)
    for i, b in enumerate(bl):
        if isinstance(b, dict) and b.get("id") == block:
            return i
    raise ValueError(f"bloque '{block}' no existe en la sección '{sec.get('id')}'; ids: {', '.join(str(b.get('id')) for b in bl if isinstance(b, dict))}")
