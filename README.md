# Smart City - Projet Microservices

Projet d'architecture microservices pour une ville intelligente utilisant différents protocoles de communication (REST, SOAP, GraphQL, gRPC).

## 🏗️ Architecture

Ce projet implémente **4 microservices** couvrant différents aspects d'une smart city:

| Service | Protocole | Domaine | Port | Status |
|---------|-----------|---------|------|--------|
| **Transport** | REST (FastAPI) | Mobilité urbaine | 8000 | ✅ |
| **Qualité de l'Air** | SOAP (Spyne) | Environnement | 8001 | ✅ |
| **Tourisme** | GraphQL | Attractions | 8002 | 🔄 |
| **Urgence** | gRPC | Services médicaux | 8003 | 🔄 |

## 🚀 Installation

### Prérequis
- Python 3.11+
- pip

### Setup
```powershell
# Cloner le repository
git clone <url>
cd Projet_SmartCity

# Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\activate

# Installer les dépendances globales
pip install -r requirements.txt
```

## 📦 Services

### 1. Service REST - Transport (Port 8000)
Gestion des transports urbains (bus, tram, métro, vélo).

```powershell
# Installer dépendances
pip install -r service_rest_transport\app\requirements.txt

# Lancer le service
.\venv\Scripts\python.exe -m uvicorn service_rest_transport.app.app:app --host 0.0.0.0 --port 8000 --reload
```

**Documentation Swagger**: http://127.0.0.1:8000/docs

**Endpoints principaux**:
- `GET /transport` - Liste tous les transports
- `POST /transport` - Créer un nouveau transport
- `GET /health` - Health check

### 2. Service SOAP - Qualité de l'Air (Port 8001)
Mesures de pollution atmosphérique (PM2.5, PM10, O3, NO2, CO, AQI).

```powershell
# Installer dépendances
pip install -r service_soap_air\app\requirements.txt

# Lancer le service
.\venv\Scripts\python.exe service_soap_air\app\soap_server.py
```

**WSDL**: http://127.0.0.1:8001/?wsdl

**Opérations SOAP**:
- `GetAllMeasures` - Liste toutes les mesures
- `GetAirQuality(measure_id)` - Récupère une mesure
- `AddMeasure(...)` - Ajoute une mesure

## 🛠️ Technologies

- **FastAPI** - Framework REST moderne avec validation Pydantic
- **Spyne** - Framework SOAP pour Python
- **SQLAlchemy** - ORM pour bases de données
- **SQLite** - Base de données légère
- **Uvicorn** - Serveur ASGI haute performance

## 📊 Structure du Projet

```
Projet_SmartCity/
├── service_rest_transport/
│   ├── app/
│   │   ├── app.py              # API FastAPI
│   │   ├── database.py         # Configuration SQLAlchemy
│   │   ├── models.py           # Modèles ORM
│   │   ├── crud.py             # Opérations CRUD
│   │   └── requirements.txt
│   ├── transport.db            # Base SQLite
│   └── README.md
├── service_soap_air/
│   ├── app/
│   │   ├── soap_server.py      # Service SOAP standalone
│   │   └── requirements.txt
│   ├── air_quality.db          # Base SQLite
│   └── README.md
├── service_graphql_tourisme/   # En cours
├── service_grpc_urgence/       # En cours
├── .gitignore
└── README.md
```

## 🧪 Tests

### Service REST
```powershell
# Health check
curl.exe http://127.0.0.1:8000/health

# Liste transports
curl.exe http://127.0.0.1:8000/transport
```

### Service SOAP
```powershell
# Télécharger WSDL
curl.exe http://127.0.0.1:8001/?wsdl

# Test avec Python zeep
pip install zeep
python -c "from zeep import Client; c = Client('http://127.0.0.1:8001/?wsdl'); print(c.service.GetAllMeasures())"
```

## 📝 TODO

- [ ] Implémenter service GraphQL Tourisme
- [ ] Implémenter service gRPC Urgence
- [ ] Ajouter tests unitaires
- [ ] Dockeriser les services
- [ ] Créer docker-compose orchestration
- [ ] Ajouter monitoring (Prometheus/Grafana)
- [ ] Implémenter API Gateway

## 📄 Licence

Projet académique - Smart City Microservices Architecture

## 👥 Auteur

Développé dans le cadre d'un projet d'architecture microservices
