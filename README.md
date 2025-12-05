# 🏙️ TuniLink - Smart City Platform

Plateforme de gestion intelligente pour la ville de Tunis intégrant 4 architectures de services : REST, SOAP, GraphQL et gRPC.

## 📋 Vue d'ensemble

TuniLink est un système d'information urbain qui orchestre plusieurs services pour gérer :
- 🚍 **Transports publics** (REST)
- 🌫️ **Qualité de l'air** (SOAP)
- 🏛️ **Attractions touristiques** (GraphQL)
- 🚑 **Services d'urgence** (gRPC)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              WEB CLIENT (Nginx)                     │
│                 Port: 80                            │
└────────────────────┬────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────┐
│           API GATEWAY (FastAPI)                     │
│              Port: 8888                             │
│  ┌────────────────────────────────────────────┐    │
│  │  • Authentification (admin/user)           │    │
│  │  • Orchestration de 5 scénarios            │    │
│  │  • Agrégation des services                 │    │
│  └────────────────────────────────────────────┘    │
└──┬──────────┬──────────┬──────────┬───────────────┘
   │          │          │          │
   │ REST     │ SOAP     │ GraphQL  │ gRPC
   ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌───────────┐
│Transport│ │Air     │ │Tourisme  │ │Urgence    │
│8000    │ │8001    │ │8002      │ │50051      │
└────────┘ └────────┘ └──────────┘ └───────────┘
```

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

## 🎭 Scénarios d'Orchestration

Testez les 5 scénarios via http://localhost/orchestration.html

### 1. 🏙️ City Dashboard
Agrège en temps réel :
- Tous les transports disponibles
- Qualité de l'air (OpenWeatherMap API)
- Attractions touristiques
- Véhicules d'urgence

**Test** :
```bash
curl http://localhost:8888/api/orchestration/city-dashboard
```

### 2. 🗺️ Plan Trip
Planifie un trajet optimal selon :
- Zone de départ et d'arrivée
- Transports disponibles filtrés géographiquement
- Qualité de l'air sur le trajet

**Test** :
```bash
curl "http://localhost:8888/api/orchestration/plan-trip?origin=Carthage&destination=Bardo"
```

### 3. 🚑 Emergency Response
Coordonne une intervention d'urgence :
- Dispatch du véhicule le plus proche
- Impact sur le trafic
- Qualité de l'air à l'emplacement

**Test** :
```bash
curl -X POST http://localhost:8888/api/orchestration/emergency-response \
  -H "Content-Type: application/json" \
  -d '{
    "emergency_type": "accident",
    "severity": "high",
    "location": "Avenue Bourguiba",
    "latitude": 36.8065,
    "longitude": 10.1815
  }'
```

### 4. 🏛️ Tourist Day
Recommande des attractions selon :
- Zone souhaitée
- Qualité de l'air actuelle
- Transports disponibles

**Test** :
```bash
curl "http://localhost:8888/api/orchestration/tourist-day?zone=La%20Marsa"
```

### 5. 🌱 Eco Route
Calcule un itinéraire écologique :
- Évite les zones polluées
- Privilégie les transports verts
- Recommandations environnementales

**Test** :
```bash
curl "http://localhost:8888/api/orchestration/eco-route?origin=Tunis&destination=Carthage"
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

## 📂 Structure du Projet

```
Smart-City/
├── api_gateway/                # Orchestrateur principal
│   ├── gateway.py             # API Gateway FastAPI
│   ├── auth.py                # Système d'authentification
│   ├── grpc_client.py         # Client gRPC
│   ├── proto/                 # Fichiers Protobuf
│   └── Dockerfile
├── service_rest_transport/     # Service REST
│   ├── app/
│   │   ├── app.py             # FastAPI application
│   │   └── data/              # Base de données JSON
│   └── Dockerfile
├── service_soap_air/           # Service SOAP
│   ├── app/
│   │   ├── soap_server.py     # Serveur Spyne
│   │   └── data/              # Données qualité air
│   └── Dockerfile
├── service_graphql_tourisme/   # Service GraphQL
│   ├── app/
│   │   ├── app.py             # Serveur Strawberry
│   │   ├── schema.py          # Schéma GraphQL
│   │   └── data/              # Données attractions
│   └── Dockerfile
├── service_grpc_urgence/       # Service gRPC
│   ├── app/
│   │   ├── server.py          # Serveur gRPC
│   │   ├── emergency.proto    # Définition Protobuf
│   │   └── data/              # Données urgences
│   └── Dockerfile
├── web_client/                 # Interface utilisateur
│   ├── index.html             # Page principale
│   ├── orchestration.html     # Tests orchestration
│   ├── app.js                 # Logique métier
│   ├── auth.js                # Gestion authentification
│   ├── style.css              # Styles
│   └── Dockerfile
├── docker-compose.yml          # Configuration Docker
├── test_services.ps1           # Script de tests
└── README.md
```

## 🔧 Commandes Utiles

### Docker

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter tous les services
docker-compose down

# Reconstruire un service
docker-compose up -d --build service-rest

# Voir l'état des services
docker ps

# Entrer dans un conteneur
docker exec -it smartcity-gateway /bin/bash
```

### Git

```bash
# Vérifier le statut
git status

# Ajouter les modifications
git add .

# Commit
git commit -m "Description"

# Push vers GitHub
git push origin main
```

## 🐛 Dépannage

### Les services ne démarrent pas
```bash
# Vérifier les logs
docker-compose logs

# Nettoyer et redémarrer
docker-compose down -v
docker-compose up -d --build
```

### Port déjà utilisé
```bash
# Trouver le processus utilisant le port 8000
netstat -ano | findstr :8000

# Arrêter le processus (Windows)
taskkill /PID <PID> /F
```

### Données corrompues
```bash
# Supprimer les volumes et redémarrer
docker-compose down -v
docker-compose up -d --build
```

## 📊 Métriques du Projet

- **6 services** Docker
- **4 architectures** différentes (REST, SOAP, GraphQL, gRPC)
- **5 scénarios** d'orchestration
- **10 zones** de Tunis couvertes
- **19 transports** disponibles
- **20 attractions** touristiques
- **8 véhicules** d'urgence
- **2 rôles** utilisateurs

## 📝 Licence

Projet académique - Université de Tunis

## 👥 Auteur

- **GitHub** : [@ameny-ga](https://github.com/ameny-ga)
- **Repository** : [Smart-City](https://github.com/ameny-ga/Smart-City)

## 🎯 Objectifs Pédagogiques

Ce projet démontre :
1. ✅ Maîtrise de **4 architectures de services** (REST, SOAP, GraphQL, gRPC)
2. ✅ **Orchestration** de microservices hétérogènes
3. ✅ **Authentification et autorisation** (RBAC)
4. ✅ Intégration d'**APIs externes** (OpenWeatherMap)
5. ✅ **Conteneurisation** avec Docker
6. ✅ Architecture **client-serveur** moderne
7. ✅ **Tests** automatisés et documentation

---

**🏙️ TuniLink - Connecter la ville intelligente de demain**
