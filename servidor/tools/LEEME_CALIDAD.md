# Calidad: instalación de lo que no viene en git
- **svgo** (MIT): `cd servidor/tools/node && npm install`.
- **LanguageTool** (LGPL, ~250 MB, necesita Java 17+): descarga https://languagetool.org/download/LanguageTool-stable.zip y descomprímelo en `servidor/tools/vendor/` (queda `LanguageTool-X.Y/languagetool-commandline.jar`).
- **pikepdf** y **Pillow**: ya están en `requirements.txt`.
Uso: `python servidor/calidad.py pdf|texto|svg|imagen …` o `POST /v1/quality`.
