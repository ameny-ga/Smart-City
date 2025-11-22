# service_rest_transport — API REST Mobilité (FastAPI)

Service REST pour la gestion des transports urbains dans le cadre du projet Smart City.

## Fonctionnalités

- **CRUD complet** : Create, Read, Update, Delete sur les transports
- **Validation automatique** : via Pydantic
- **Documentation Swagger/OpenAPI** : générée automatiquement par FastAPI
- **Endpoints REST** : conformes aux standards

## Installation & Lancement

```powershell
# Activer l'environnement virtuel (si nécessaire)
venv\Scripts\activate

# Installer les dépendances
pip install -r service_rest_transport/app/requirements.txt

# Lancer le service avec uvicorn (hot-reload activé)
cd service_rest_transport/app
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Le service démarre sur : **http://127.0.0.1:8000**

## Documentation interactive

- **Swagger UI** : http://127.0.0.1:8000/docs (interface graphique pour tester l'API)
- **ReDoc** : http://127.0.0.1:8000/redoc (documentation alternative)
- **OpenAPI JSON** : http://127.0.0.1:8000/openapi.json

## Endpoints disponibles

| Méthode | Endpoint              | Description                           |
|---------|-----------------------|---------------------------------------|
| GET     | `/health`             | Vérification de l'état du service     |
| GET     | `/transport`          | Liste tous les transports             |
| GET     | `/transport/{id}`     | Récupère un transport par ID          |
| POST    | `/transport`          | Crée un nouveau transport             |
| PUT     | `/transport/{id}`     | Met à jour un transport existant      |
| DELETE  | `/transport/{id}`     | Supprime un transport                 |

## Tests manuels (PowerShell)

```powershell
# Health check
curl.exe http://127.0.0.1:8000/health

# Liste tous les transports
curl.exe http://127.0.0.1:8000/transport

# Récupère un transport spécifique
curl.exe http://127.0.0.1:8000/transport/1

# Créer un nouveau transport
curl.exe -X POST http://127.0.0.1:8000/transport -H "Content-Type: application/json" -d '{\"mode\":\"metro\",\"route\":\"E-F\",\"status\":\"on-time\"}'

# Mettre à jour un transport
curl.exe -X PUT http://127.0.0.1:8000/transport/1 -H "Content-Type: application/json" -d '{\"status\":\"delayed\"}'

# Supprimer un transport
curl.exe -X DELETE http://127.0.0.1:8000/transport/2
```

## Structure du projet

```
service_rest_transport/
├── app/
│   ├── app.py              # Application FastAPI principale
│   └── requirements.txt    # Dépendances Python
└── README.md               # Ce fichier
```

## Prochaines étapes

- [ ] Ajouter une base de données SQLite/PostgreSQL
- [ ] Implémenter des tests unitaires (pytest)
- [ ] Dockeriser le service
- [ ] Ajouter authentification JWT
- [ ] Intégrer des données temps réel (open data)
