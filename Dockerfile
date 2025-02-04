# Usa la imagen oficial de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de dependencias al contenedor
COPY requirements.txt .

# Copia todo el código fuente de tu proyecto al contenedor (incluyendo la carpeta Webpage)
COPY . .

# Verificar si Webpage/webpage.py existe en el contenedor
RUN ls -l /app/Webpage

# Instala las dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python desde el requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Establecer variable de entorno para MLflow
ENV MLFLOW_TRACKING_URI=http://127.0.0.1:5000

# Expone los puertos necesarios
EXPOSE 8501 5000 5001

# Inicia el servidor de MLflow en segundo plano y luego lanza Streamlit.
CMD mlflow server --backend-store-uri file:///app/MLflow/mlruns --default-artifact-root file:///app/MLflow/mlruns --host 0.0.0.0 --port 5000 & \
    mlflow models serve -m "models:/ALS_Recommender_Model_with_Predict_1/1" -p 5001 --no-conda & \
    streamlit run /app/Webpage/webpage.py
