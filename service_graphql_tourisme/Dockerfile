# Dockerfile pour le service GraphQL - Tourisme
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY app/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app/ ./app/

# Créer le répertoire pour la base de données SQLite
RUN mkdir -p /app/data

# Exposer le port
EXPOSE 8002

# Variable d'environnement pour SQLite
ENV DATABASE_PATH=/app/data/tourisme.db

# Commande de démarrage
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8002"]
