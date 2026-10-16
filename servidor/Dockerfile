# [CLAUDE-CONSTRUCTOR] Imagen del servidor para que corra igual en tu PC y en un servidor. Construir desde la RAÍZ del repo:
#   docker build -f servidor/Dockerfile -t servidor-documentos .
#   docker run -p 8765:8765 -e API_KEY=cambia-esto -v "$PWD/teoria/imagenes:/imagenes:ro" servidor-documentos
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends poppler-utils ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY servidor/requirements.txt /app/servidor/requirements.txt
RUN pip install --no-cache-dir -r servidor/requirements.txt && python -m playwright install --with-deps chromium
COPY servidor /app/servidor
EXPOSE 8765
CMD ["python", "servidor/api.py", "--host", "0.0.0.0", "--puerto", "8765", "--imagenes", "/imagenes"]
