#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Conecta un agente (Claude Code, Codex, OpenCode, Antigravity, Claude Desktop, cualquiera) con la API de myStyle y comprueba que responde.
"""python servidor/conectar.py comprobar                 revisa requisitos y que la API responde (qué falta y cómo instalarlo)
python servidor/conectar.py <agente> [--escribir]       muestra la configuración del agente (claude-code | codex | opencode | antigravity | claude-desktop | http)
                                                        --escribir la guarda en el archivo del agente (si ya existe, hace copia .bak y solo añade `mystyle`)
python servidor/conectar.py skill [--destino ruta]      copia el manual skills/mystyle/ a la carpeta de skills del agente (por defecto ~/.claude/skills/mystyle)

Una sola definición de herramientas (servidor/herramientas.py) sirve a MCP, a function calling estilo OpenAI y a la terminal:
python servidor/herramientas.py call <herramienta> '<json>'."""
import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MCP = (RAIZ / "servidor" / "mcp_server.py").as_posix()
URL = os.environ.get("MYSTYLE_URL", "http://127.0.0.1:8765")
PY = "python"


def cfg_claude_code():
    return f'claude mcp add mystyle -e MYSTYLE_URL={URL} -- {PY} {MCP}', None


def cfg_codex():
    return (f'[mcp_servers.mystyle]\ncommand = "{PY}"\nargs = ["{MCP}"]\nenv = {{ MYSTYLE_URL = "{URL}" }}\n', Path.home() / ".codex" / "config.toml")


def cfg_opencode():
    return (json.dumps({"$schema": "https://opencode.ai/config.json", "mcp": {"mystyle": {"type": "local", "command": [PY, MCP], "environment": {"MYSTYLE_URL": URL}, "enabled": True}}}, indent=2),
            RAIZ / "opencode.json")


def cfg_mcpservers():
    return json.dumps({"mcpServers": {"mystyle": {"command": PY, "args": [MCP], "env": {"MYSTYLE_URL": URL}}}}, indent=2)


def cfg_antigravity():
    return cfg_mcpservers(), Path.home() / ".gemini" / "antigravity" / "mcp_config.json"


def cfg_claude_desktop():
    return cfg_mcpservers(), Path(os.environ.get("APPDATA", str(Path.home()))) / "Claude" / "claude_desktop_config.json"


def cfg_http():
    return (f"# sin MCP: function calling estilo OpenAI (Ollama, LM Studio, cualquier cliente)\ncurl -s {URL}/v1/tools?perfil=minimo\n# HTTP directo\ncurl -s {URL}/v1/openapi.json\n"
            f"# una herramienta desde la terminal\n{PY} servidor/herramientas.py call list_recipes '{{\"q\":\"informe de ventas\"}}'", None)


AGENTES = {"claude-code": cfg_claude_code, "codex": cfg_codex, "opencode": cfg_opencode, "antigravity": cfg_antigravity, "claude-desktop": cfg_claude_desktop, "http": cfg_http}


def escribir(agente, texto, destino):
    if destino is None:
        return "este agente se configura con el comando mostrado (no hay archivo que escribir)"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists():
        shutil.copy(destino, destino.with_suffix(destino.suffix + ".bak"))
    if destino.suffix == ".toml":
        ya = destino.read_text(encoding="utf-8") if destino.exists() else ""
        if "[mcp_servers.mystyle]" in ya:
            return f"{destino} ya tiene mystyle"
        destino.write_text(ya.rstrip() + "\n\n" + texto, encoding="utf-8")
    else:
        datos = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() and destino.read_text(encoding="utf-8").strip() else {}
        nuevo = json.loads(texto)
        for k, v in nuevo.items():
            if isinstance(v, dict):
                datos.setdefault(k, {}).update(v)
            else:
                datos[k] = v
        destino.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"escrito en {destino} (copia: .bak si existía)"


def comprobar():
    ok = True

    def linea(bueno, texto, arreglo=""):
        nonlocal ok
        ok &= bool(bueno)
        print(("✔ " if bueno else "✘ ") + texto + ("" if bueno else f"   → {arreglo}"))
    v = sys.version_info
    linea(v >= (3, 10), f"Python {v.major}.{v.minor}", "instala Python 3.10 o superior")
    for mod, pip in (("playwright", "playwright"), ("pymupdf", "pymupdf"), ("pikepdf", "pikepdf"), ("PIL", "pillow"), ("pptx", "python-pptx"), ("docx", "python-docx"), ("openpyxl", "openpyxl")):
        try:
            __import__(mod)
            linea(True, mod)
        except ImportError:
            linea(False, mod, f"pip install -r servidor/requirements.txt   (falta {pip})")
    linea(shutil.which("node"), "Node 22+ (video con HyperFrames)", "instala Node 22 o superior desde nodejs.org")
    linea(shutil.which("ffmpeg"), "FFmpeg (video)", "winget install ffmpeg   /   brew install ffmpeg")
    linea(shutil.which("java"), "Java (opcional: ortografía con LanguageTool)", "opcional; ver servidor/tools/LEEME_CALIDAD.md")
    try:
        with urllib.request.urlopen(URL + "/v1/tools", timeout=5) as r:
            n = len(json.loads(r.read()))
        linea(True, f"API en {URL} responde ({n} herramientas)")
    except Exception:  # noqa: BLE001
        linea(False, f"API en {URL}", "python servidor/api.py --puerto 8765 --imagenes imagenes")
    print("\nTodo listo." if ok else "\nFalta algo (✘): arréglalo y vuelve a correr `python servidor/conectar.py comprobar`.")
    return 0 if ok else 1


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__)
    elif a[0] == "comprobar":
        sys.exit(comprobar())
    elif a[0] == "skill":
        dst = Path(sys.argv[sys.argv.index("--destino") + 1]) if "--destino" in sys.argv else Path.home() / ".claude" / "skills" / "mystyle"
        shutil.copytree(RAIZ / "skills" / "mystyle", dst, dirs_exist_ok=True)
        print(f"manual copiado a {dst}")
    elif a[0] in AGENTES:
        r = AGENTES[a[0]]()
        texto, destino = r if isinstance(r, tuple) else (r, None)
        print(texto)
        if destino:
            print(f"\n# archivo: {destino}")
        if "--escribir" in sys.argv:
            print("\n" + escribir(a[0], texto, destino))
    else:
        print(f"agente desconocido. Usa: {', '.join(AGENTES)}")


if __name__ == "__main__":
    main()
