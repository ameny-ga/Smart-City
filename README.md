# 🏙️ TuniLink - Smart City Platform

**Plateforme intelligente de gestion urbaine pour Tunis** - Intégration multi-protocoles (REST, SOAP, GraphQL, gRPC)

## 📋 Vue d'ensemble

TuniLink orchestre 4 microservices pour gérer :
- 🚍 **Transports publics** (REST API)
- 🌫️ **Qualité de l'air** (SOAP Service)
- 🏛️ **Attractions touristiques** (GraphQL API)
- 🚑 **Services d'urgence** (gRPC Service)

## 🏗️ Architecture en couches

```
┌───────────────────────────────────────────────────────────┐
│              4. FRONTEND (Nginx - Port 80)                │
│                    Interface utilisateur                   │
└─────────────────────────┬─────────────────────────────────┘
                          │ HTTP
                          ▼
┌───────────────────────────────────────────────────────────┐
│          3. API GATEWAY (FastAPI - Port 8888)             │
│   • Authentification HTTP Basic Auth                      │
│   • Point d'entrée unique (Single Entry Point)            │
│   • Routage et orchestration intégrée                     │
│   • 5 scénarios complexes (workflows)                     │
└──┬────────────┬────────────┬────────────┬─────────────────┘
   │            │            │            │
   │ REST       │ SOAP       │ GraphQL    │ gRPC
   ▼            ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Transport │ │Air Quality│ │Tourism   │ │Emergency │
│Port 8000 │ │Port 8001  │ │Port 8002 │ │Port 50051│
└────┬─────┘ └────┬──────┘ └────┬─────┘ └────┬─────┘
     │            │             │            │
     ▼            ▼             ▼            ▼
┌───────────────────────────────────────────────────────────┐
│            1. BASES DE DONNÉES (SQLite)                   │
│  transport.db | air_quality.db | tourisme.db | urgence.db │
└───────────────────────────────────────────────────────────┘
```

### Avantages de cette architecture

✅ **Séparation des responsabilités** - Chaque couche a un rôle défini  
✅ **Scalabilité** - Services indépendants, peuvent être dupliqués  
✅ **Maintenabilité** - Code modulaire et testable  
✅ **Sécurité** - Gateway centralise l'authentification

## 🚀 Démarrage Rapide

### Prérequis
- Docker Desktop
- Docker Compose
- Git

### Installation

```bash
# Cloner le repository
git clone https://github.com/ameny-ga/Smart-City.git
cd Smart-City

# Configurer la clé API OpenWeatherMap
cd api_gateway
cp .env.example .env
# Éditer .env et remplacer your_api_key_here par votre vraie clé
# Obtenir une clé gratuite sur : https://openweathermap.org/api

# Retourner au dossier racine
cd ..

# Démarrer tous les services
docker-compose up -d --build

# Vérifier que tous les services sont opérationnels
docker ps
```

### Accès aux services

| Service | URL | Documentation |
|---------|-----|---------------|
| **Interface Web** | http://localhost | Dashboard principal |
| **Orchestration** | http://localhost/orchestration.html | Tests des scénarios |
| **API Gateway** | http://localhost:8888/docs | Swagger UI |
| **REST Transport** | http://localhost:8000/docs | Swagger UI |
| **SOAP Air** | http://localhost:8001/?wsdl | WSDL |
| **GraphQL Tourism** | http://localhost:8002/graphql | GraphiQL |
| **gRPC Emergency** | localhost:50051 | emergency.proto |

## 🔐 Authentification

Le système utilise HTTP Basic Authentication avec 2 rôles :

### Comptes de test

**Administrateur** (accès complet CRUD) :
- Username: `admin`
- Password: `admin123`

**Utilisateur** (lecture seule) :
- Username: `user`
- Password: `user123`

### Connexion

1. Ouvrir http://localhost
2. Cliquer sur "🔐 Connexion"
3. Entrer les identifiants
4. Les administrateurs voient les boutons "Modifier" et "Supprimer"
5. Les utilisateurs simples ne peuvent que consulter

## 🎭 5 Scénarios d'orchestration

Interface web : http://localhost/orchestration.html

### 1. 🏙️ City Dashboard
**Tableau de bord ville complet** - Agrège tous les services en temps réel
```powershell
$headers = @{Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:admin123"))}
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/city-dashboard" -Headers $headers
```

### 2. 🗺️ Plan Trip
**Planification trajet intelligent** - Basé sur qualité d'air + transports disponibles
```powershell
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/plan-trip?zone=Tunis%20Centre-Ville" -Headers $headers
```

### 3. 🏛️ Tourist Day
**Journée touristique** - Attractions + transport + météo
```powershell
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/tourist-day?zone=Tunis" -Headers $headers
```

### 4. 🚑 Emergency Response
**Gestion urgence coordonnée** - Véhicules + trafic + qualité air
```powershell
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/emergency-response?zone=Tunis%20Centre-Ville&emergency_type=accident" -Headers $headers
```

### 5. 🌱 Eco Route
**Trajet écologique optimisé** - Évite zones polluées
```powershell
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/eco-route?start_zone=Tunis%20Centre-Ville&end_zone=La%20Marsa" -Headers $headers
```

## 🔧 Services Individuels

### Service REST - Transport (Port 8000)

**Framework** : FastAPI  
**Base de données** : JSON file  

**Endpoints** :
```bash
# Lister tous les transports
GET http://localhost:8000/transports

# Créer un transport (admin uniquement)
POST http://localhost:8000/transports

# Modifier un transport (admin uniquement)
PUT http://localhost:8000/transports/{id}

# Supprimer un transport (admin uniquement)
DELETE http://localhost:8000/transports/{id}
```

### Service SOAP - Qualité de l'Air (Port 8001)

**Framework** : Spyne  
**Intégration** : OpenWeatherMap API  

**Opérations** :
- `GetAllMeasures` : Toutes les mesures de qualité d'air
- `GetMeasureByStation` : Mesure d'une station spécifique
- `GetStations` : Liste des stations de mesure

**WSDL** : http://localhost:8001/?wsdl

### Service GraphQL - Tourisme (Port 8002)

**Framework** : Strawberry GraphQL  

**Queries** :
```graphql
# Toutes les attractions
query {
  allAttractions {
    id
    name
    type
    zone
    description
    openingHours
    rating
  }
}

# Filtrer par zone
query {
  attractionsByZone(zone: "La Marsa") {
    id
    name
    rating
  }
}

# Filtrer par type
query {
  attractionsByType(type: "Monument historique") {
    id
    name
    description
  }
}
```

### Service gRPC - Urgences (Port 50051)

**Framework** : gRPC Python  
**Protobuf** : emergency.proto  

**Méthodes** :
- `GetAllVehicles` : Tous les véhicules d'urgence
- `GetVehicle` : Véhicule spécifique
- `CreateEmergency` : Créer une urgence
- `UpdateVehicleStatus` : Mettre à jour le statut

**Test avec grpcurl** :
```bash
grpcurl -plaintext -d '{}' localhost:50051 emergency.EmergencyService/GetAllVehicles
```

## 🌍 Zones de Tunis

Le système couvre 10 zones principales :

1. **La Marsa** - Zone côtière nord
2. **Carthage** - Site historique
3. **Sidi Bou Saïd** - Village pittoresque
4. **La Goulette** - Port de Tunis
5. **Tunis Centre** - Centre-ville
6. **Bardo** - Musée national
7. **Ariana** - Banlieue nord
8. **Mégrine** - Zone industrielle
9. **Hammam-Lif** - Banlieue sud
10. **Ben Arous** - Zone résidentielle

## 🧪 Tests

### Script de test automatisé

```powershell
# Windows PowerShell
.\test_services.ps1
```

### Tests manuels

**REST** :
```bash
curl http://localhost:8000/transports
```

**GraphQL** :
```bash
curl -X POST http://localhost:8002/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ allAttractions { id name } }"}'
```

**Gateway avec authentification** :
```bash
curl -u admin:admin123 http://localhost:8888/api/auth/me
```

## 📦 Technologies

### Backend
- **Python 3.11**
- **FastAPI** - REST API & Gateway
- **Spyne** - SOAP Service
- **Strawberry** - GraphQL Service
- **gRPC** - RPC Service
- **httpx** - HTTP client async
- **zeep** - SOAP client

### Frontend
- **HTML5/CSS3/JavaScript**
- **Nginx** - Serveur web
- Vanilla JS (pas de framework)

### Infrastructure
- **Docker** - Conteneurisation
- **Docker Compose** - Orchestration
- **GitHub** - Version control

### APIs Externes
- **OpenWeatherMap Air Pollution API** - Données de qualité d'air en temps réel

## 📂 Structure du projet

```
Smart-City/
├── api_gateway/                    # Point d'entrée (Port 8888)
│   ├── gateway.py                 # Gateway avec orchestration intégrée
│   ├── auth.py                    # Authentification HTTP Basic
│   ├── grpc_client.py             # Client gRPC
│   ├── proto/                     # Fichiers Protobuf générés
│   └── Dockerfile
│
├── service_rest_transport/         # Microservice Transport (Port 8000)
│   ├── app/app.py                 # API REST FastAPI
│   ├── transport.db               # Base SQLite
│   └── Dockerfile
│
├── service_soap_air/               # Microservice Qualité Air (Port 8001)
│   ├── app/soap_server.py         # Service SOAP Spyne
│   ├── air_quality.db             # Base SQLite
│   └── Dockerfile
│
├── service_graphql_tourisme/       # Microservice Tourisme (Port 8002)
│   ├── app/app.py                 # API GraphQL Strawberry
│   ├── tourisme.db                # Base SQLite
│   └── Dockerfile
│
├── service_grpc_urgence/           # Microservice Urgence (Port 50051)
│   ├── app/server.py              # Serveur gRPC
│   ├── urgence.db                 # Base SQLite
│   └── Dockerfile
│
├── web_client/                     # Frontend (Port 80)
│   ├── index.html                 # Page principale
│   ├── orchestration.html         # Tests scénarios
│   ├── app.js                     # Logique frontend
│   └── Dockerfile
│
├── export_database/                # Backups bases de données
│   ├── transport.db
│   ├── air_quality.db
│   ├── tourisme.db
│   └── urgence.db
│
├── docker-compose.yml              # Orchestration Docker
└── README.md                       # Documentation
```

## 🔧 Commandes Docker

```powershell
# Démarrer tous les services
docker-compose up -d --build

# Vérifier l'état
docker-compose ps

# Voir les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f api-gateway

# Arrêter tous les services
docker-compose down

# Arrêter ET supprimer les volumes (⚠️ supprime les données)
docker-compose down -v

# Rebuild un service spécifique
docker-compose up -d --build api-gateway

# Entrer dans un conteneur
docker exec -it smartcity-gateway /bin/bash
```

## 🐛 Dépannage

### Services ne démarrent pas
```powershell
# Vérifier les logs
docker-compose logs

# Nettoyer et redémarrer
docker-compose down
docker-compose up -d --build
```

### Port déjà utilisé
```powershell
# Windows - Trouver le processus sur port 8888
netstat -ano | findstr :8888

# Arrêter le processus
taskkill /PID <PID> /F
```

### Bases de données corrompues
```powershell
# Copier les backups propres
Copy-Item "export_database\*.db" "service_*\" -Force -Recurse

# Redémarrer sans volumes
docker-compose down
docker-compose up -d --build
```

## 📊 Statistiques du projet

- **6 services** Docker (4 microservices + gateway + frontend)
- **4 protocoles** (REST, SOAP, GraphQL, gRPC)
- **5 scénarios** d'orchestration complexes
- **10 zones** de Tunis couvertes
- **19 transports** opérationnels
- **17 attractions** touristiques
- **12 véhicules** d'urgence
- **Architecture 4 couches** (DB → Microservices → API Gateway → Frontend)

## 👥 Auteur

**Ameni Abdelli**
- GitHub: [@ameny-ga](https://github.com/ameny-ga)

## 📝 Licence

Projet académique - Décembre 2025
1. ✅ Maîtrise de **4 architectures de services** (REST, SOAP, GraphQL, gRPC)
2. ✅ **Orchestration** de microservices hétérogènes
3. ✅ **Authentification et autorisation** (RBAC)
4. ✅ Intégration d'**APIs externes** (OpenWeatherMap)
5. ✅ **Conteneurisation** avec Docker
6. ✅ Architecture **client-serveur** moderne
7. ✅ **Tests** automatisés et documentation

---

**🏙️ TuniLink - Connecter la ville intelligente de demain**
