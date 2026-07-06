# Dockerfile para el Backend de AmazoníaSearch
FROM python:3.12-slim

# Instalar dependencias del sistema necesarias para compilar hnswlib (C++)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependencias de Python
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copiar el código del backend y el dataset
COPY backend/ ./backend/
COPY data/ ./data/

# Ejecutar la generación de datos (descarga el modelo y crea el índice HNSW)
RUN python -m backend.scripts.generate_data

# Exponer el puerto de la API FastAPI
EXPOSE 8000

# Comando para iniciar la API con Uvicorn
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
