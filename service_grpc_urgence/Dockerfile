# Dockerfile pour le service gRPC - Urgences
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY app/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le proto file d'abord
COPY app/emergency.proto ./app/

# Régénérer les fichiers protobuf
WORKDIR /app/app
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. emergency.proto

# Copier le reste du code
WORKDIR /app
COPY app/*.py ./app/

# Créer le répertoire pour la base de données SQLite
RUN mkdir -p /app/data

# Exposer le port gRPC
EXPOSE 50051

# Variable d'environnement pour SQLite
ENV DATABASE_PATH=/app/data/urgence.db

# Démarrer le serveur (l'initialisation se fait au démarrage du serveur)
CMD ["python", "app/server.py"]
