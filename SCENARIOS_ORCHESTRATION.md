# 🎭 Scénarios d'Orchestration - Smart City

## 📋 Vue d'ensemble

Ce document présente les **5 scénarios d'orchestration** développés pour démontrer la coordination entre les différents microservices de la Smart City. Chaque scénario combine plusieurs services utilisant des protocoles différents (REST, SOAP, GraphQL, gRPC) pour répondre à des cas d'usage réels.

---

## 🗺️ Scénario 1: Planification de Trajet Intelligent

**Endpoint:** `GET /api/orchestration/plan-trip?zone={zone}`

### Description
Recommande le meilleur moyen de transport en fonction de la qualité de l'air dans une zone donnée.

### Services Orchestrés
1. **SOAP** - Service Qualité de l'Air
2. **REST** - Service Transport

### Workflow
```
SOAP:GetMeasuresByStation → analyze_AQI → REST:GetTransports → filter_by_air_quality
```

### Logique Métier
- **AQI > 100**: Privilégie les transports fermés (Métro, Bus, Train)
- **AQI ≤ 100**: Tous les transports sont recommandés, y compris vélo

### Exemple de Requête
```bash
GET http://localhost:8888/api/orchestration/plan-trip?zone=Centre-Ville
```

### Résultat
```json
{
  "zone": "Centre-Ville",
  "air_quality": {
    "aqi": 85,
    "status": "Modéré",
    "source": "SOAP service"
  },
  "recommendation": "✅ Excellente qualité de l'air...",
  "transports": [...],
  "orchestration": {
    "services_called": ["air_quality (SOAP)", "transport (REST)"],
    "success": true
  }
}
```

---

## 🏖️ Scénario 2: Journée Touristique Intelligente

**Endpoint:** `GET /api/orchestration/tourist-day?zone={zone}`

### Description
Planifie une journée touristique en fonction de la qualité de l'air, suggère des attractions adaptées et le meilleur transport.

### Services Orchestrés
1. **SOAP** - Service Qualité de l'Air
2. **GraphQL** - Service Tourisme
3. **REST** - Service Transport

### Workflow
```
SOAP:GetMeasures → GraphQL:GetAttractions → filter_by_AQI → REST:GetTransports → generate_day_plan
```

### Logique Métier
- **AQI > 100**: Recommande attractions en intérieur (musées, monuments)
- **AQI ≤ 100**: Toutes attractions, priorité aux parcs et activités extérieures
- Sélection automatique du transport adapté (vélo si bonne qualité d'air)

### Exemple de Requête
```bash
GET http://localhost:8888/api/orchestration/tourist-day?zone=Zone%20Sud
```

### Résultat
```json
{
  "zone": "Zone Sud",
  "air_quality": {"aqi": 45, "status": "Bon"},
  "recommendation": "✅ Bonne qualité d'air (45). Profitez des parcs...",
  "attractions": [8 attractions triées par rating],
  "suggested_transport": {"mode": "Vélo", "route": "..."},
  "day_plan": {
    "morning": "Visite des attractions principales",
    "lunch": "Pause déjeuner en zone à faible AQI",
    "afternoon": "Utiliser Vélo pour se déplacer",
    "evening": "Retour avec transports en commun"
  }
}
```

---

## 🚑 Scénario 3: Gestion d'Urgence Coordonnée

**Endpoint:** `GET /api/orchestration/emergency-response?zone={zone}&emergency_type={type}`

### Description
Coordonne la réponse d'urgence en tenant compte de la qualité de l'air, disponibilité des véhicules et impact sur le trafic.

### Services Orchestrés
1. **SOAP** - Service Qualité de l'Air
2. **gRPC** - Service Urgences
3. **REST** - Service Transport

### Workflow
```
SOAP:CheckAirQuality → gRPC:DispatchVehicle → REST:RerouteTransport → coordinate_response
```

### Logique Métier
- Vérifie la qualité de l'air pour alerter le personnel d'urgence
- Dispatche le véhicule approprié (ambulance, pompiers)
- Identifie les lignes de transport à dévier
- Génère des recommandations de sécurité

### Exemple de Requête
```bash
GET http://localhost:8888/api/orchestration/emergency-response?zone=Zone%20Nord&emergency_type=medical
```

### Résultat
```json
{
  "zone": "Zone Nord",
  "emergency_type": "medical",
  "air_quality": {
    "aqi": 120,
    "alert": "⚠️ Qualité d'air mauvaise - masques recommandés"
  },
  "emergency_vehicles": {
    "type": "ambulance",
    "eta": "5 minutes",
    "route": "En direction de Zone Nord"
  },
  "traffic_impact": {
    "affected_lines": 1,
    "action": "Déviation temporaire pendant l'intervention"
  },
  "recommendations": [
    "🚑 Véhicule d'urgence en route vers Zone Nord",
    "🚦 Dégager les voies d'accès principales",
    "😷 Personnel: utiliser équipement de protection respiratoire"
  ]
}
```

---

## 🌱 Scénario 4: Trajet Écologique Optimisé

**Endpoint:** `GET /api/orchestration/eco-route?start_zone={start}&end_zone={end}`

### Description
Calcule le trajet le plus écologique entre deux zones en analysant la qualité de l'air sur le parcours.

### Services Orchestrés
1. **SOAP** - Service Qualité de l'Air (multiple zones)
2. **REST** - Service Transport
3. **GraphQL** - Service Tourisme (optionnel)

### Workflow
```
SOAP:GetMultipleAQI → analyze_pollution_zones → REST:GetEcoTransports → calculate_best_path
```

### Logique Métier
- Analyse AQI de plusieurs zones sur le parcours
- Privilégie transports écologiques (vélo, métro, tramway)
- Calcule un score écologique basé sur:
  - AQI moyen du parcours
  - Type de transport utilisé
  - Distance parcourue
- Propose alternatives (rapide vs écologique)

### Exemple de Requête
```bash
GET http://localhost:8888/api/orchestration/eco-route?start_zone=Zone%20Sud&end_zone=Gare
```

### Résultat
```json
{
  "start": "Zone Sud",
  "end": "Gare",
  "route_analysis": {
    "Zone Sud": {"aqi": 45, "status": "Bon"},
    "Centre-Ville": {"aqi": 85, "status": "Modéré"},
    "Gare": {"aqi": 95, "status": "Modéré"}
  },
  "eco_score": 95,
  "recommended_path": [
    {"step": 1, "zone": "Zone Sud", "aqi": 45},
    {"step": 2, "zone": "Centre-Ville", "action": "Utiliser Métro Ligne A"},
    {"step": 3, "zone": "Gare", "aqi": 95}
  ],
  "alternatives": [
    {
      "name": "Route directe (rapide)",
      "duration": "15 min",
      "eco_score": 75
    },
    {
      "name": "Route écologique (recommandée)",
      "duration": "25 min",
      "eco_score": 95
    }
  ]
}
```

---

## 🏙️ Scénario 5: Tableau de Bord Complet de la Ville

**Endpoint:** `GET /api/orchestration/city-dashboard`

### Description
Vue d'ensemble temps réel de tous les services de la Smart City avec analyse de santé globale.

### Services Orchestrés
1. **REST** - Service Transport
2. **SOAP** - Service Qualité de l'Air
3. **GraphQL** - Service Tourisme
4. **gRPC** - Service Urgences

### Workflow
```
parallel_queries → aggregate_data → analyze_city_health → generate_alerts
```

### Logique Métier
- Récupère les données des 4 services en parallèle
- Calcule des métriques agrégées:
  - Taux d'opérationnalité des transports
  - AQI moyen de la ville
  - Disponibilité des attractions touristiques
  - État des services d'urgence
- Génère un statut global de la ville
- Produit des alertes automatiques si nécessaire

### Exemple de Requête
```bash
GET http://localhost:8888/api/orchestration/city-dashboard
```

### Résultat
```json
{
  "timestamp": "2025-11-23T14:00:00Z",
  "transport": {
    "total_lines": 13,
    "operational": 9,
    "status": "⚠️ Perturbations",
    "availability": "69%"
  },
  "air_quality": {
    "average_aqi": 91,
    "status": "⚠️ Modéré",
    "zones_monitored": 5,
    "polluted_zones": 2
  },
  "tourism": {
    "total_attractions": 10,
    "currently_open": 9,
    "status": "✅ Actif",
    "occupancy": "90%"
  },
  "emergency": {
    "status": "✅ Standby",
    "active_interventions": 0,
    "available_vehicles": 12,
    "response_time_avg": "4.5 min"
  },
  "city_status": "⚠️ Perturbations importantes détectées",
  "alerts": [
    "⚠️ 2 zone(s) avec pollution élevée",
    "🚨 Plusieurs services nécessitent attention"
  ],
  "orchestration": {
    "services_called": ["transport (REST)", "air_quality (SOAP)", "tourism (GraphQL)", "emergency (gRPC)"],
    "data_sources": 4,
    "success": true
  }
}
```

---

## 📊 Tableau Comparatif des Scénarios

| Scénario | Services | Protocoles | Complexité | Cas d'Usage |
|----------|----------|------------|-----------|-------------|
| Plan Trip | 2 | SOAP + REST | ⭐⭐ | Quotidien - Choix transport |
| Tourist Day | 3 | SOAP + GraphQL + REST | ⭐⭐⭐ | Tourisme - Planification journée |
| Emergency | 3 | SOAP + gRPC + REST | ⭐⭐⭐⭐ | Critique - Coordination urgence |
| Eco Route | 3 | SOAP (multi) + REST + GraphQL | ⭐⭐⭐⭐ | Environnement - Optimisation |
| City Dashboard | 4 | Tous (REST + SOAP + GraphQL + gRPC) | ⭐⭐⭐⭐⭐ | Monitoring - Vue globale |

---

## 🎯 Bénéfices de l'Orchestration

### 1. **Intelligence Contextuelle**
Les décisions sont prises en combinant des données de sources multiples:
- Qualité de l'air + Disponibilité transport → Recommandation intelligente
- Urgence + Trafic + Qualité d'air → Coordination optimale

### 2. **Réutilisabilité**
Les services individuels restent indépendants et réutilisables:
- Service SOAP air utilisé dans 5 scénarios
- Service REST transport intégré dans 4 scénarios
- Chaque service peut être appelé individuellement

### 3. **Scalabilité**
L'architecture permet d'ajouter de nouveaux scénarios facilement:
- Nouveaux endpoints d'orchestration sans modifier les services
- Combinaisons illimitées possibles
- Ajout de nouveaux services facilité

### 4. **Interopérabilité**
Démonstration de la communication entre protocoles hétérogènes:
- SOAP (legacy) communique avec REST (moderne)
- GraphQL permet requêtes flexibles
- gRPC offre performance pour urgences

---

## 🧪 Tests des Scénarios

### PowerShell
```powershell
# Scénario 1
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/plan-trip?zone=Centre-Ville"

# Scénario 2
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/tourist-day?zone=Zone%20Sud"

# Scénario 3
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/emergency-response?zone=Zone%20Nord&emergency_type=medical"

# Scénario 4
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/eco-route?start_zone=Zone%20Sud&end_zone=Gare"

# Scénario 5
Invoke-RestMethod -Uri "http://localhost:8888/api/orchestration/city-dashboard"
```

### cURL
```bash
# Scénario 1
curl "http://localhost:8888/api/orchestration/plan-trip?zone=Centre-Ville"

# Scénario 2
curl "http://localhost:8888/api/orchestration/tourist-day?zone=Zone%20Sud"

# Scénario 3
curl "http://localhost:8888/api/orchestration/emergency-response?zone=Zone%20Nord&emergency_type=medical"

# Scénario 4
curl "http://localhost:8888/api/orchestration/eco-route?start_zone=Zone%20Sud&end_zone=Gare"

# Scénario 5
curl "http://localhost:8888/api/orchestration/city-dashboard"
```

---

## 🔗 Intégration Client Web

Tous les scénarios sont accessibles via l'interface web à `http://localhost:80`.

Le client web actuel inclut:
- ✅ Section "Planificateur de Trajet" (Scénario 1)
- 🔜 Sections à ajouter pour scénarios 2-5

---

## 📝 Notes Techniques

### Gestion des Erreurs
- Chaque scénario inclut un try/except pour chaque appel de service
- Les erreurs sont tracées dans les logs du Gateway
- Les réponses incluent toujours `"orchestration": {"success": true/false}`

### Performance
- Scénarios 1-4: Exécution séquentielle (dépendances entre étapes)
- Scénario 5: Exécution parallèle des 4 appels de services
- Temps de réponse moyen: < 1 seconde

### Extensibilité
Pour ajouter un nouveau scénario:
1. Créer une nouvelle fonction async dans `api_gateway/gateway.py`
2. Décorer avec `@app.get("/api/orchestration/nom-scenario")`
3. Implémenter la logique d'orchestration
4. Ajouter metadata `orchestration` dans la réponse
5. Tester et documenter

---

**Date de création:** 23 Novembre 2025  
**Version:** 1.0  
**Auteur:** Smart City Team
