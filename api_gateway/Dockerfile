# Dockerfile pour l'API Gateway
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements et installer d'abord
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer grpc_tools pour générer les fichiers proto
RUN pip install --no-cache-dir grpcio-tools==1.60.0

# Créer répertoire proto
RUN mkdir -p proto

# Copier les fichiers proto générés (seront créés par docker-compose build context)
COPY proto/ ./proto/

# Revenir au répertoire app
WORKDIR /app

# Copier le code de l'application
COPY gateway.py .
COPY auth.py .
COPY grpc_client.py .

# Exposer le port de la Gateway
EXPOSE 8080

# Commande de démarrage
CMD ["uvicorn", "gateway:app", "--host", "0.0.0.0", "--port", "8080"]
