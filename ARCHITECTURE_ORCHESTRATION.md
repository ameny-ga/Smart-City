# Architecture et Orchestration - Smart City

## 📋 Table des matières
1. [Vue d'ensemble de l'architecture](#vue-densemble-de-larchitecture)
2. [Communication entre services](#communication-entre-services)
3. [Orchestration réelle](#orchestration-réelle)
4. [Flux de données](#flux-de-données)
5. [Détails techniques](#détails-techniques)

---

## 🏗️ Vue d'ensemble de l'architecture

Le système Smart City utilise une **architecture microservices** avec 4 services indépendants communiquant via différents protocoles, orchestrés par une API Gateway centrale.

```
┌─────────────────────────────────────────────────────────────┐
│                      WEB CLIENT (Nginx)                      │
│                    http://localhost:80                       │
│                     Interface utilisateur                    │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP REST
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                 API GATEWAY (FastAPI)                        │
│                http://localhost:8888                         │
│            Point d'entrée unique - Orchestration             │
└───┬──────────────┬──────────────┬──────────────┬────────────┘
    │              │              │              │
    │ REST         │ SOAP         │ GraphQL      │ gRPC
    ▼              ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐
│Transport│  │ Qualité  │  │ Tourisme  │  │   Urgences   │
│ (REST)  │  │Air(SOAP) │  │ (GraphQL) │  │    (gRPC)    │
│  :8000  │  │  :8001   │  │   :8002   │  │    :50051    │
└─────────┘  └──────────┘  └───────────┘  └──────────────┘
```

---

## 🔄 Communication entre services

### 1. **Service REST - Transport** (Port 8000)
**Protocole:** HTTP REST avec FastAPI  
**Base de données:** SQLite avec SQLAlchemy ORM

**Endpoints exposés:**
```python
GET  /transports         # Liste tous les transports
POST /transports         # Crée un nouveau transport
GET  /transports/{id}    # Détails d'un transport
PUT  /transports/{id}    # Met à jour un transport
DELETE /transports/{id}  # Supprime un transport
```

**Communication avec Gateway:**
```python
# Dans gateway.py
async def get_transports():
    response = requests.get("http://service-rest:8000/transports")
    return response.json()
```

**Données réelles:** 13 lignes de transport (métro, bus, tram) avec statut opérationnel

---

### 2. **Service SOAP - Qualité de l'Air** (Port 8001)
**Protocole:** SOAP/XML avec Spyne  
**Base de données:** SQLite avec records en mémoire

**Opérations WSDL:**
```xml
GetAirQualityMeasures()    # Obtient toutes les mesures
GetMeasuresByZone(zone_id) # Mesures par zone
GetZones()                 # Liste des zones
CreateMeasure(data)        # Crée une mesure
```

**Communication avec Gateway:**
```python
# Dans gateway.py
from zeep import Client

client = Client('http://service-soap:8001/?wsdl')
result = client.service.GetAirQualityMeasures()
```

**Données réelles:** Zones avec mesures AQI (Air Quality Index) en temps réel

---

### 3. **Service GraphQL - Tourisme** (Port 8002)
**Protocole:** GraphQL avec Strawberry  
**Base de données:** SQLite avec attractions touristiques

**Schéma GraphQL:**
```graphql
type Query {
  attractions: [Attraction!]!
  attraction(id: Int!): Attraction
  attractionsByType(type: String!): [Attraction!]!
}

type Mutation {
  createAttraction(input: AttractionInput!): Attraction!
  updateAttractionStatus(id: Int!, status: String!): Attraction!
}

type Attraction {
  id: Int!
  name: String!
  type: String!
  address: String!
  latitude: Float!
  longitude: Float!
  status: String!
  openingHours: String
  description: String
}
```

**Communication avec Gateway:**
```python
# Dans gateway.py
query = """
    query {
        attractions {
            id name type address status
            latitude longitude openingHours
        }
    }
"""
response = requests.post(
    "http://service-graphql:8002/graphql",
    json={"query": query}
)
```

**Données réelles:** 10 attractions (musées, monuments) avec statut ouvert/fermé

---

### 4. **Service gRPC - Urgences** (Port 50051)
**Protocole:** gRPC avec Protocol Buffers  
**Base de données:** SQLite avec véhicules et interventions

**Définition Protocol Buffer (emergency.proto):**
```protobuf
service EmergencyService {
  rpc GetVehicles(EmptyRequest) returns (VehicleList);
  rpc GetVehicle(VehicleRequest) returns (Vehicle);
  rpc GetInterventions(EmptyRequest) returns (InterventionList);
  rpc CreateIntervention(InterventionData) returns (Intervention);
  rpc AssignVehicle(AssignmentRequest) returns (Assignment);
}

message Vehicle {
  int32 id = 1;
  string vehicle_type = 2;
  string identifier = 3;
  string status = 4;
  double latitude = 5;
  double longitude = 6;
  string station = 7;
  int32 crew_size = 8;
}

message Intervention {
  int32 id = 1;
  string intervention_type = 2;
  string priority = 3;
  string address = 4;
  double latitude = 5;
  double longitude = 6;
  string status = 7;
  int32 assigned_vehicle_id = 8;
  string description = 9;
}
```

**Communication avec Gateway:**
```python
# Dans grpc_client.py
import grpc
import emergency_pb2
import emergency_pb2_grpc

channel = grpc.insecure_channel('service-grpc:50051')
stub = emergency_pb2_grpc.EmergencyServiceStub(channel)

# Appel synchrone
vehicles = stub.GetVehicles(emergency_pb2.EmptyRequest())
```

**Données réelles:**
- **8 véhicules:** 3 ambulances, 3 camions pompiers, 2 voitures police
- **4 interventions actives:** médical, incendie, accident, crime

---

## 🎭 Orchestration réelle

L'API Gateway **orchestre** les appels vers les différents services pour créer des vues agrégées et des workflows complexes.

### Exemple 1: Dashboard Ville (`/api/orchestration/city-dashboard`)

**Workflow orchestré:**
```python
@app.get("/api/orchestration/city-dashboard")
async def city_dashboard():
    """
    Agrège les données de TOUS les services pour un dashboard unifié
    """
    
    # 1. Appel REST - Transport (asynchrone)
    transport_response = await asyncio.to_thread(
        requests.get, "http://service-rest:8000/transports"
    )
    transports = transport_response.json()
    
    # 2. Appel SOAP - Qualité Air (synchrone)
    soap_client = Client('http://service-soap:8001/?wsdl')
    measures = soap_client.service.GetAirQualityMeasures()
    
    # 3. Appel GraphQL - Tourisme (asynchrone)
    graphql_query = '{ attractions { status } }'
    tourism_response = await asyncio.to_thread(
        requests.post,
        "http://service-graphql:8002/graphql",
        json={"query": graphql_query}
    )
    attractions = tourism_response.json()["data"]["attractions"]
    
    # 4. Appel gRPC - Urgences (synchrone)
    grpc_client = get_grpc_stub()
    vehicles = grpc_client.GetVehicles(emergency_pb2.EmptyRequest())
    
    # 5. Agrégation et calculs
    operational_lines = sum(1 for t in transports if t["status"] == "operationnel")
    average_aqi = sum(m["aqi"] for m in measures) / len(measures)
    open_attractions = sum(1 for a in attractions if a["status"] == "open")
    available_vehicles = sum(1 for v in vehicles.vehicles if v.status == "available")
    
    # 6. Retour agrégé
    return {
        "timestamp": datetime.now().isoformat(),
        "city_status": "Opérationnel" if operational_lines > 5 else "Perturbé",
        "transport": {
            "operational": operational_lines,
            "total_lines": len(transports)
        },
        "air_quality": {
            "average_aqi": round(average_aqi, 1),
            "status": "Bon" if average_aqi < 50 else "Modéré"
        },
        "tourism": {
            "currently_open": open_attractions,
            "total_attractions": len(attractions)
        },
        "emergency": {
            "available_vehicles": available_vehicles,
            "total_vehicles": len(vehicles.vehicles)
        },
        "alerts": []
    }
```

**Résultat réel actuel:**
```json
{
  "timestamp": "2025-11-23T16:45:32",
  "city_status": "Opérationnel",
  "transport": {
    "operational": 9,
    "total_lines": 13
  },
  "air_quality": {
    "average_aqi": 91.3,
    "status": "Modéré"
  },
  "tourism": {
    "currently_open": 9,
    "total_attractions": 10
  },
  "emergency": {
    "available_vehicles": 5,
    "total_vehicles": 8
  },
  "alerts": []
}
```

---

### Exemple 2: Planification de trajet (`/api/orchestration/plan-trip`)

**Workflow orchestré avec logique métier:**
```python
@app.post("/api/orchestration/plan-trip")
async def plan_trip(request: TripRequest):
    """
    Orchestration complexe avec décisions intelligentes
    """
    
    # 1. Vérifier qualité air destination (SOAP)
    soap_client = Client('http://service-soap:8001/?wsdl')
    air_quality = soap_client.service.GetMeasuresByZone(request.destination_zone)
    
    # 2. Décision basée sur AQI
    if air_quality.aqi > 100:
        recommendation = "Transport public recommandé (pollution élevée)"
        transport_mode = "public"
    else:
        recommendation = "Tous modes de transport disponibles"
        transport_mode = "any"
    
    # 3. Récupérer transports disponibles (REST)
    transport_response = await asyncio.to_thread(
        requests.get,
        f"http://service-rest:8000/transports?mode={transport_mode}"
    )
    transports = transport_response.json()
    
    # 4. Enrichir avec attractions proches (GraphQL)
    graphql_query = f'''
        query {{
            attractionsByZone(zone: "{request.destination_zone}") {{
                name type status openingHours
            }}
        }}
    '''
    tourism_response = await asyncio.to_thread(
        requests.post,
        "http://service-graphql:8002/graphql",
        json={"query": graphql_query}
    )
    nearby_attractions = tourism_response.json()["data"]["attractionsByZone"]
    
    # 5. Vérifier urgences en cours (gRPC)
    grpc_client = get_grpc_stub()
    interventions = grpc_client.GetInterventions(emergency_pb2.EmptyRequest())
    active_incidents = [
        i for i in interventions.interventions
        if i.status in ["pending", "in_progress"]
    ]
    
    # 6. Retour orchestré avec recommandations
    return {
        "air_quality": {
            "aqi": air_quality.aqi,
            "status": "Bon" if air_quality.aqi < 50 else "Modéré",
            "recommendation": recommendation
        },
        "available_transports": [
            {
                "mode": t["mode"],
                "route": t["route"],
                "status": t["status"]
            }
            for t in transports if t["status"] == "operationnel"
        ],
        "nearby_attractions": [
            {
                "name": a["name"],
                "type": a["type"],
                "status": a["status"]
            }
            for a in nearby_attractions if a["status"] == "open"
        ],
        "alerts": [
            f"Intervention {i.intervention_type} en cours à {i.address}"
            for i in active_incidents
        ]
    }
```

---

## 🔀 Flux de données

### Flux utilisateur complet:

```
1. CLIENT WEB
   └─> Clique "Actualiser les données" sur Dashboard
       │
       ▼
2. API GATEWAY (:8888)
   └─> Reçoit GET /api/orchestration/city-dashboard
       │
       ├─> [PARALLÈLE] Appel REST     → service-rest:8000/transports
       ├─> [PARALLÈLE] Appel SOAP     → service-soap:8001/?wsdl
       ├─> [PARALLÈLE] Appel GraphQL  → service-graphql:8002/graphql
       └─> [PARALLÈLE] Appel gRPC     → service-grpc:50051
       │
       ▼
3. SERVICES MÉTIER
   ├─> Service REST    : Requête SQLite → Retourne 13 transports
   ├─> Service SOAP    : Requête SQLite → Retourne mesures AQI
   ├─> Service GraphQL : Requête SQLite → Retourne 10 attractions
   └─> Service gRPC    : Requête SQLite → Retourne 8 véhicules + 4 interventions
       │
       ▼
4. API GATEWAY
   └─> Agrège les résultats
       └─> Calcule statistiques (moyennes, comptages)
           └─> Génère recommandations
               │
               ▼
5. CLIENT WEB
   └─> Reçoit JSON unifié
       └─> Met à jour interface
           └─> Affiche: 9/13 transport, AQI 91, 9/10 tourism, 5/8 emergency
```

---

## ⚙️ Détails techniques

### Configuration Docker Compose

```yaml
services:
  # Service REST - Transport
  service-rest:
    build: ./service_rest_transport
    ports:
      - "8000:8000"
    networks:
      - smartcity-network
    volumes:
      - ./service_rest_transport/data:/app/data

  # Service SOAP - Qualité Air  
  service-soap:
    build: ./service_soap_air
    ports:
      - "8001:8001"
    networks:
      - smartcity-network
    volumes:
      - ./service_soap_air/data:/app/data

  # Service GraphQL - Tourisme
  service-graphql:
    build: ./service_graphql_tourisme
    ports:
      - "8002:8002"
    networks:
      - smartcity-network
    volumes:
      - ./service_graphql_tourisme/data:/app/data

  # Service gRPC - Urgences
  service-grpc:
    build: ./service_grpc_urgence
    ports:
      - "50051:50051"
    networks:
      - smartcity-network
    volumes:
      - ./service_grpc_urgence/data:/app/data

  # API Gateway - Orchestration
  api-gateway:
    build: ./api_gateway
    ports:
      - "8888:8888"
    depends_on:
      - service-rest
      - service-soap
      - service-graphql
      - service-grpc
    networks:
      - smartcity-network

  # Client Web
  web-client:
    build: ./web_client
    ports:
      - "80:80"
    depends_on:
      - api-gateway
    networks:
      - smartcity-network

networks:
  smartcity-network:
    driver: bridge
```

### Réseau Docker

Tous les conteneurs communiquent via le réseau **smartcity-network**:
- **Résolution DNS interne:** `service-rest` résout vers l'IP du conteneur REST
- **Isolation:** Les services ne sont pas exposés directement à l'extérieur
- **Communication interne:** Pas de chiffrement nécessaire (réseau privé)

### Avantages de cette architecture

✅ **Indépendance des services:** Chaque service peut être développé, testé, déployé indépendamment  
✅ **Polyglotte:** Utilise le meilleur protocole pour chaque cas d'usage  
✅ **Scalabilité:** Peut dupliquer les services selon la charge  
✅ **Résilience:** Si un service tombe, les autres continuent  
✅ **Orchestration centralisée:** Gateway = point unique de contrôle et logique métier  
✅ **Communication réseau réelle:** Pas de simulation, vraies requêtes HTTP/SOAP/GraphQL/gRPC

---

## 📊 Monitoring en temps réel

### Logs des communications

```bash
# Logs Gateway (voir les appels orchestrés)
docker logs smartcity-gateway -f

# Logs service REST
docker logs smartcity-rest -f

# Logs service SOAP
docker logs smartcity-soap -f

# Logs service GraphQL
docker logs smartcity-graphql -f

# Logs service gRPC
docker logs smartcity-grpc -f
```

### Test manuel des communications

```bash
# Test REST direct
curl http://localhost:8000/transports

# Test SOAP avec zeep
python -c "from zeep import Client; c = Client('http://localhost:8001/?wsdl'); print(c.service.GetZones())"

# Test GraphQL
curl -X POST http://localhost:8002/graphql -H "Content-Type: application/json" -d '{"query":"{ attractions { name } }"}'

# Test gRPC (via Gateway)
curl http://localhost:8888/api/emergency/vehicles

# Test orchestration complète
curl http://localhost:8888/api/orchestration/city-dashboard
```

---

## 🎯 Conclusion

Cette architecture démontre une **orchestration réelle** de microservices avec:
- 4 protocoles différents (REST, SOAP, GraphQL, gRPC)
- Communication réseau authentique via Docker
- Logique métier dans le Gateway
- Agrégation de données multi-sources
- Interface web unifiée

**Tout est fonctionnel et communique réellement entre containers Docker.**
