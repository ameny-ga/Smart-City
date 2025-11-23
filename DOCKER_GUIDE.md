# 🐳 Guide Docker - Smart City Microservices

## 📋 Architecture

```
┌─────────────────┐
│   Client Web    │ :80
│    (Nginx)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Gateway   │ :8080
│    (FastAPI)    │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐
│  REST  │ │ SOAP │ │GraphQL│ │ gRPC │
│  :8000 │ │ :8001│ │ :8002 │ │:50051│
└────────┘ └──────┘ └───────┘ └──────┘
```

## 🚀 Lancement

### Construire et démarrer tous les services :
```bash
docker-compose up --build -d
```

### Vérifier les conteneurs :
```bash
docker-compose ps
```

### Voir les logs :
```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f api-gateway
docker-compose logs -f service-rest
```

### Arrêter tous les services :
```bash
docker-compose down
```

### Arrêter et supprimer les volumes (⚠️ supprime les données) :
```bash
docker-compose down -v
```

## 🌐 Accès aux services

| Service | URL | Description |
|---------|-----|-------------|
| **Client Web** | http://localhost | Interface utilisateur |
| **API Gateway** | http://localhost:8080 | Point d'entrée centralisé |
| **REST** | http://localhost:8000 | Service Transport |
| **SOAP** | http://localhost:8001/?wsdl | Service Air Quality |
| **GraphQL** | http://localhost:8002/graphql | Service Tourisme |
| **gRPC** | localhost:50051 | Service Urgences |

## 📊 Health Checks

```bash
# Gateway health
curl http://localhost:8080/health

# REST service
curl http://localhost:8000/health

# GraphQL service
curl http://localhost:8002/health
```

## 🔧 Commandes utiles

### Reconstruire un service spécifique :
```bash
docker-compose up --build -d service-rest
```

### Entrer dans un conteneur :
```bash
docker exec -it smartcity-gateway sh
docker exec -it smartcity-rest sh
```

### Inspecter le réseau :
```bash
docker network inspect smartcity-network
```

### Voir les volumes :
```bash
docker volume ls | findstr smartcity
```

## 🐛 Troubleshooting

### Les services ne démarrent pas :
```bash
# Voir les logs d'erreur
docker-compose logs

# Reconstruire sans cache
docker-compose build --no-cache
docker-compose up -d
```

### Port déjà utilisé :
```bash
# Voir les processus sur le port
netstat -ano | findstr :8080

# Arrêter le processus (Windows)
taskkill /PID <PID> /F
```

### Problème de réseau :
```bash
# Recréer le réseau
docker-compose down
docker network prune
docker-compose up -d
```

## 📦 Volumes persistants

Les données sont stockées dans des volumes Docker :
- `smartcity-rest-data` : Base SQLite du service Transport
- `smartcity-soap-data` : Base SQLite du service Air Quality
- `smartcity-graphql-data` : Base SQLite du service Tourisme
- `smartcity-grpc-data` : Base SQLite du service Urgences

Les données persistent même après `docker-compose down` (sauf si vous utilisez `-v`).

## 🧪 Tests

### Tester via l'API Gateway :
```bash
# Liste des transports
curl http://localhost:8080/api/transport/transports

# Créer un transport
curl -X POST http://localhost:8080/api/transport/transports \
  -H "Content-Type: application/json" \
  -d "{\"mode\":\"Bus\",\"route\":\"Ligne 10\",\"status\":\"operationnel\"}"

# Liste des attractions
curl http://localhost:8080/api/tourism/attractions
```

### Tester directement les services :
```bash
# REST
curl http://localhost:8000/transports/

# GraphQL Playground
# Ouvrez dans le navigateur : http://localhost:8002/graphql
```

## 🎯 Architecture microservices

✅ **Isolation** : Chaque service dans son propre conteneur  
✅ **Communication** : Réseau Docker interne `smartcity-network`  
✅ **Gateway** : Point d'entrée unique pour le client  
✅ **Persistance** : Volumes Docker pour les bases de données  
✅ **Health checks** : Monitoring automatique  
✅ **Auto-restart** : Redémarrage automatique en cas d'erreur  

## 📝 Notes

- Le client web communique **uniquement** avec l'API Gateway
- L'API Gateway route les requêtes vers les microservices appropriés
- Les microservices communiquent entre eux via le réseau Docker `smartcity-network`
- Les services ne sont pas directement accessibles depuis l'extérieur (sauf pour les tests)
