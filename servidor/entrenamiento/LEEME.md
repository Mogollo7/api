# Fase 4 · entrenamiento con Soup (lo haces tú, en tu GPU)

Yo dejo listos los datos y los scripts; **no se entrena nada desde aquí**. Una noche alcanza para un LoRA pequeño si el objetivo y el criterio de éxito están fijados antes.

```powershell
# 0) línea base ANTES de entrenar (con el modelo actual, API y Ollama encendidos)
python servidor/evaluacion/evaluar.py --guardar-base

# 1) dataset con lo ya validado (tool-calling de las evaluaciones + correcciones)
python servidor/entrenamiento/preparar_dataset.py

# 2) instalar y fijar versión (anótala: Soup cambia rápido)
pip install soup==<versión>          # confirma el nombre del paquete y la versión en su documentación
# 3) revisar servidor/entrenamiento/soup.yaml (claves sin verificar) y correr una prueba corta
soup train --config servidor/entrenamiento/soup.yaml     # comprueba el comando exacto en `soup --help`

# 4) evaluar contra el conjunto fijo; si mejora la línea base, exportar a GGUF para Ollama; si no, conservar el modelo anterior
python servidor/evaluacion/evaluar.py --modelo <el-modelo-nuevo>
```
Criterio de éxito: supera la línea base de `servidor/evaluacion/linea_base.json` en herramienta y segmentación. Si no cabe en 6 GB, alquila una GPU unas horas y exporta el resultado.
