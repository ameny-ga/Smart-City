"""API Gateway - Centralise l'accès aux 4 microservices."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Dict, Any
import asyncio
from zeep import Client
from zeep.exceptions import Fault
from grpc_client import EmergencyClient

app = FastAPI(
    title="🌐 API Gateway - Smart City",
    description="Point d'entrée centralisé pour tous les microservices",
    version="1.0.0"
)

# Configuration CORS pour permettre l'accès depuis le client Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs des microservices (dans Docker network)
SERVICES = {
    "transport": "http://service-rest:8000",
    "air_quality": "http://service-soap:8001",
    "tourism": "http://service-graphql:8002",
    "emergency": "service-grpc:50051"  # gRPC
}


@app.get("/")
def root():
    """Page d'accueil de la Gateway."""
    return {
        "service": "API Gateway - Smart City",
        "version": "1.0.0",
        "architecture": "microservices",
        "services": {
            "transport": f"{SERVICES['transport']} (REST)",
            "air_quality": f"{SERVICES['air_quality']} (SOAP)",
            "tourism": f"{SERVICES['tourism']} (GraphQL)",
            "emergency": f"{SERVICES['emergency']} (gRPC)"
        },
        "endpoints": {
            "transport": "/api/transport/*",
            "air_quality": "/api/air-quality/*",
            "tourism": "/api/tourism/*",
            "emergency": "/api/emergency/*"
        }
    }


@app.get("/health")
async def health_check():
    """Vérifie la santé de tous les services."""
    health_status = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Check REST service
        try:
            response = await client.get(f"{SERVICES['transport']}/health")
            health_status["transport"] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception as e:
            health_status["transport"] = f"unavailable: {str(e)}"
        
        # Check GraphQL service
        try:
            response = await client.get(f"{SERVICES['tourism']}/health")
            health_status["tourism"] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception as e:
            health_status["tourism"] = f"unavailable: {str(e)}"
        
        # Check SOAP service
        try:
            response = await client.get(f"{SERVICES['air_quality']}/?wsdl")
            health_status["air_quality"] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception as e:
            health_status["air_quality"] = f"unavailable: {str(e)}"
    
    health_status["emergency"] = "gRPC - use client to check"
    
    return {
        "gateway": "healthy",
        "services": health_status
    }


# ============================================
# ROUTES POUR LE SERVICE TRANSPORT (REST)
# ============================================

@app.get("/api/transport/transports")
async def get_transports():
    """Liste tous les transports."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['transport']}/transports/")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service transport indisponible: {str(e)}")


@app.get("/api/transport/transports/{transport_id}")
async def get_transport(transport_id: int):
    """Récupère un transport par ID."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['transport']}/transports/{transport_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Transport non trouvé")
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"Service transport indisponible: {str(e)}")


@app.post("/api/transport/transports")
async def create_transport(data: Dict[str, Any]):
    """Crée un nouveau transport."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['transport']}/transports/",
                json=data
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service transport indisponible: {str(e)}")


@app.put("/api/transport/transports/{transport_id}")
async def update_transport(transport_id: int, data: Dict[str, Any]):
    """Met à jour un transport."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{SERVICES['transport']}/transports/{transport_id}",
                json=data
            )
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Transport non trouvé")
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"Service transport indisponible: {str(e)}")


@app.delete("/api/transport/transports/{transport_id}")
async def delete_transport(transport_id: int):
    """Supprime un transport."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{SERVICES['transport']}/transports/{transport_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Transport non trouvé")
            return {"message": "Transport supprimé avec succès"}
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"Service transport indisponible: {str(e)}")


# ============================================
# ROUTES POUR LE SERVICE TOURISME (GraphQL)
# ============================================

@app.post("/api/tourism/graphql")
async def tourism_graphql(query_data: Dict[str, Any]):
    """Proxy pour les requêtes GraphQL."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['tourism']}/graphql",
                json=query_data
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service tourisme indisponible: {str(e)}")


@app.get("/api/tourism/attractions")
async def get_attractions():
    """Liste toutes les attractions (helper REST pour GraphQL)."""
    query = """
    query {
        attractions {
            id
            name
            category
            description
            address
            city
            latitude
            longitude
            rating
            priceLevel
            openingHours
            isOpen
        }
    }
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['tourism']}/graphql",
                json={"query": query}
            )
            result = response.json()
            if "data" in result:
                return result["data"]["attractions"]
            return result
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service tourisme indisponible: {str(e)}")


# ============================================
# ROUTES POUR LE SERVICE AIR QUALITY (SOAP)
# ============================================

@app.get("/api/air-quality/measures")
async def get_air_quality_measures():
    """Liste toutes les mesures de qualité de l'air."""
    # Note: Pour SOAP, il faudrait utiliser zeep ou requests avec XML
    # Pour simplifier, on retourne un message indiquant d'utiliser SOAP directement
    return {
        "message": "Service SOAP - Utilisez un client SOAP ou SoapUI",
        "wsdl": f"{SERVICES['air_quality']}/?wsdl",
        "operations": ["GetAllMeasures", "GetAirQuality", "GetMeasuresByStation", "AddMeasure", "UpdateMeasureStatus"]
    }


# ============================================
# ROUTES POUR LE SERVICE URGENCES (gRPC)
# ============================================

@app.get("/api/emergency/vehicles")
async def get_all_vehicles():
    """Récupère tous les véhicules d'urgence via gRPC."""
    try:
        client = EmergencyClient(SERVICES['emergency'])
        vehicles = client.get_all_vehicles()
        client.close()
        return {"vehicles": vehicles, "count": len(vehicles)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service gRPC indisponible: {str(e)}")


@app.get("/api/emergency/vehicles/available")
async def get_available_vehicles(vehicle_type: str = None):
    """Récupère les véhicules disponibles via gRPC."""
    try:
        client = EmergencyClient(SERVICES['emergency'])
        vehicles = client.get_available_vehicles(vehicle_type)
        client.close()
        return {
            "vehicles": vehicles,
            "count": len(vehicles),
            "filter": vehicle_type or "all"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service gRPC indisponible: {str(e)}")


@app.get("/api/emergency/interventions")
async def get_active_interventions():
    """Récupère les interventions actives via gRPC."""
    try:
        client = EmergencyClient(SERVICES['emergency'])
        interventions = client.get_active_interventions()
        client.close()
        return {"interventions": interventions, "count": len(interventions)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service gRPC indisponible: {str(e)}")


@app.get("/api/emergency/info")
async def get_emergency_info():
    """Informations et statistiques du service gRPC d'urgences."""
    try:
        client = EmergencyClient(SERVICES['emergency'])
        vehicles = client.get_all_vehicles()
        interventions = client.get_active_interventions()
        client.close()
        
        # Statistiques
        available = len([v for v in vehicles if v['status'] == 'available'])
        on_mission = len([v for v in vehicles if v['status'] == 'on_mission'])
        
        return {
            "service": "gRPC Emergency Service",
            "host": SERVICES['emergency'],
            "statistics": {
                "total_vehicles": len(vehicles),
                "available": available,
                "on_mission": on_mission,
                "maintenance": len(vehicles) - available - on_mission,
                "active_interventions": len(interventions)
            },
            "vehicles_by_type": {
                "ambulance": len([v for v in vehicles if v['vehicle_type'] == 'ambulance']),
                "fire_truck": len([v for v in vehicles if v['vehicle_type'] == 'fire_truck']),
                "police_car": len([v for v in vehicles if v['vehicle_type'] == 'police_car'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service gRPC indisponible: {str(e)}")


# ============================================
# ORCHESTRATION - PLANIFICATION DE TRAJET
# ============================================

@app.get("/api/orchestration/plan-trip")
async def plan_trip(zone: str = "Centre-Ville"):
    """
    Orchestre plusieurs services pour planifier un trajet intelligent :
    1. Vérifie la qualité de l'air (SOAP - simulé pour commencer)
    2. Génère une recommandation basée sur l'AQI
    3. Récupère les transports disponibles (REST)
    
    Approche SIMPLE : AQI simulé initialement pour valider le workflow.
    """
    result = {
        "zone": zone,
        "air_quality": {},
        "recommendation": "",
        "transports": []
    }
    
    # Étape 1 : Qualité de l'air (APPEL SOAP RÉEL)
    try:
        # Créer le client SOAP
        wsdl_url = f"{SERVICES['air_quality']}/?wsdl"
        soap_client = Client(wsdl_url)
        
        # Appeler GetMeasuresByStation
        measures = soap_client.service.GetMeasuresByStation(zone)
        
        if measures and len(measures) > 0:
            # Prendre la première mesure (la plus récente)
            measure = measures[0]
            aqi_value = measure.aqi
            air_status = measure.status
        else:
            # Fallback si aucune mesure trouvée pour cette zone
            aqi_value = 75
            air_status = "Données non disponibles"
    except Exception as e:
        # Fallback en cas d'erreur SOAP
        print(f"⚠️ Erreur SOAP: {e}")
        aqi_value = 75
        air_status = "Service temporairement indisponible"
    
    # Interprétation de l'AQI pour la couleur
    if aqi_value <= 50:
        color = "green"
    elif aqi_value <= 100:
        color = "yellow"
    elif aqi_value <= 150:
        color = "orange"
    else:
        color = "red"
    
    result["air_quality"] = {
        "aqi": aqi_value,
        "status": air_status,
        "color": color,
        "source": "SOAP service"
    }
    
    # Étape 2 : Génération de la recommandation
    if aqi_value > 100:
        result["recommendation"] = (
            f"⚠️ La qualité de l'air est mauvaise (AQI: {aqi_value}). "
            "Privilégiez les transports en commun fermés (métro, bus) ou véhicules électriques. "
            "Évitez le vélo ou la marche prolongée."
        )
    elif aqi_value > 50:
        result["recommendation"] = (
            f"ℹ️ Qualité de l'air modérée (AQI: {aqi_value}). "
            "Tous les modes de transport sont acceptables. "
            "Les transports en commun restent un bon choix."
        )
    else:
        result["recommendation"] = (
            f"✅ Excellente qualité de l'air (AQI: {aqi_value})! "
            "Tous les modes de transport sont recommandés. "
            "Profitez du vélo ou de la marche si possible."
        )
    
    # Étape 3 : Récupération des transports disponibles (service REST)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['transport']}/transports/")
            all_transports = response.json()
            
            # Filtrer uniquement les transports opérationnels
            available_transports = [
                t for t in all_transports 
                if t.get("status") == "operationnel"
            ]
            
            # Prioriser selon la qualité de l'air
            if aqi_value > 100:
                # Mauvaise qualité : privilégier métro, bus, train (transports fermés)
                priority_modes = ["Métro", "Bus", "Train", "Taxi"]
                prioritized = [t for t in available_transports if t.get("mode") in priority_modes]
                result["transports"] = prioritized[:5]  # Top 5
            else:
                # Bonne qualité : tous les transports sont OK
                result["transports"] = available_transports[:8]  # Top 8
                
        except Exception as e:
            result["transports_error"] = f"Service transport indisponible: {str(e)}"
            result["transports"] = []
    
    result["orchestration"] = {
        "services_called": ["air_quality (SOAP)", "transport (REST)"],
        "workflow": "SOAP:GetMeasuresByStation → analyze_AQI → REST:GetTransports → filter_by_air_quality",
        "success": True
    }
    
    return result


@app.get("/api/orchestration/tourist-day")
async def plan_tourist_day(zone: str = "Centre-Ville"):
    """
    Scénario 2: Planifier une journée touristique
    Orchestre: SOAP (qualité air) + GraphQL (attractions touristiques) + REST (transports)
    
    Cas d'usage: Un touriste veut visiter la ville en fonction de la météo/pollution
    """
    result = {
        "zone": zone,
        "air_quality": {},
        "recommendation": "",
        "attractions": [],
        "suggested_transport": {},
        "day_plan": {}
    }
    
    # Étape 1: Vérifier la qualité de l'air
    try:
        wsdl_url = f"{SERVICES['air_quality']}/?wsdl"
        soap_client = Client(wsdl_url)
        measures = soap_client.service.GetMeasuresByStation(zone)
        
        if measures and len(measures) > 0:
            aqi_value = measures[0].aqi
            air_status = measures[0].status
        else:
            aqi_value = 75
            air_status = "Données non disponibles"
    except Exception as e:
        aqi_value = 75
        air_status = "Service temporairement indisponible"
    
    result["air_quality"] = {"aqi": aqi_value, "status": air_status}
    
    # Étape 2: Récupérer les attractions touristiques via GraphQL
    query = """
    query {
        attractions {
            id
            name
            category
            description
            rating
            isOpen
        }
    }
    """
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['tourism']}/graphql",
                json={"query": query}
            )
            data = response.json()
            if "data" in data and "attractions" in data["data"]:
                all_attractions = data["data"]["attractions"]
                # Filtrer selon la qualité de l'air
                if aqi_value > 100:
                    # Mauvaise qualité: privilégier attractions en intérieur
                    indoor_categories = ["Musée", "Monument", "Culture"]
                    result["attractions"] = [a for a in all_attractions if a.get("category") in indoor_categories][:5]
                    result["recommendation"] = f"⚠️ AQI élevé ({aqi_value}). Privilégiez les visites en intérieur (musées, monuments)."
                else:
                    # Bonne qualité: toutes les attractions
                    result["attractions"] = sorted(all_attractions, key=lambda x: x.get("rating", 0), reverse=True)[:8]
                    result["recommendation"] = f"✅ Bonne qualité d'air ({aqi_value}). Profitez des parcs et activités extérieures !"
        except Exception as e:
            result["attractions_error"] = str(e)
        
        # Étape 3: Suggérer un transport adapté
        try:
            response = await client.get(f"{SERVICES['transport']}/transports/")
            transports = response.json()
            available = [t for t in transports if t.get("status") == "operationnel"]
            
            if aqi_value > 100:
                # Privilégier métro/bus fermés
                priority = next((t for t in available if t.get("mode") in ["Métro", "Bus"]), None)
            else:
                # Suggérer vélo pour balade
                priority = next((t for t in available if t.get("mode") == "Vélo"), None)
            
            result["suggested_transport"] = priority if priority else available[0] if available else {}
        except Exception as e:
            result["transport_error"] = str(e)
    
    # Étape 4: Créer un plan de journée
    result["day_plan"] = {
        "morning": "Visite des attractions principales",
        "lunch": "Pause déjeuner en zone à faible AQI",
        "afternoon": f"Utiliser {result['suggested_transport'].get('mode', 'transport')} pour se déplacer",
        "evening": "Retour avec transports en commun"
    }
    
    result["orchestration"] = {
        "services_called": ["air_quality (SOAP)", "tourism (GraphQL)", "transport (REST)"],
        "workflow": "SOAP:GetMeasures → GraphQL:GetAttractions → filter_by_AQI → REST:GetTransports → generate_day_plan",
        "success": True
    }
    
    return result


@app.get("/api/orchestration/emergency-response")
async def emergency_response(zone: str, emergency_type: str = "medical"):
    """
    Scénario 3: Gestion d'urgence coordonnée
    Orchestre: gRPC (véhicules urgence) + REST (transports) + SOAP (qualité air)
    
    Cas d'usage: Une urgence nécessite coordination entre services d'urgence et blocage de circulation
    """
    result = {
        "zone": zone,
        "emergency_type": emergency_type,
        "air_quality": {},
        "emergency_vehicles": {},
        "traffic_impact": {},
        "recommendations": []
    }
    
    # Étape 1: Vérifier la qualité de l'air (important pour urgences médicales)
    try:
        wsdl_url = f"{SERVICES['air_quality']}/?wsdl"
        soap_client = Client(wsdl_url)
        measures = soap_client.service.GetMeasuresByStation(zone)
        
        if measures and len(measures) > 0:
            aqi_value = measures[0].aqi
            result["air_quality"] = {
                "aqi": aqi_value,
                "status": measures[0].status,
                "alert": "⚠️ Qualité d'air mauvaise - masques recommandés" if aqi_value > 100 else "✅ Air respirable"
            }
    except Exception as e:
        result["air_quality"] = {"error": str(e)}
    
    # Étape 2: Informations sur les véhicules d'urgence (gRPC RÉEL)
    try:
        grpc_client = EmergencyClient(SERVICES['emergency'])
        
        # Mapper le type d'urgence au type de véhicule
        vehicle_type_map = {
            "medical": "ambulance",
            "fire": "fire_truck",
            "crime": "police_car",
            "accident": "police_car"
        }
        needed_vehicle_type = vehicle_type_map.get(emergency_type, "ambulance")
        
        # Récupérer véhicules disponibles du bon type
        available_vehicles = grpc_client.get_available_vehicles(needed_vehicle_type)
        
        if available_vehicles:
            vehicle = available_vehicles[0]  # Premier disponible
            result["emergency_vehicles"] = {
                "available": True,
                "vehicle_id": vehicle['id'],
                "type": vehicle['vehicle_type'],
                "identifier": vehicle['identifier'],
                "station": vehicle['station'],
                "crew_size": vehicle['crew_size'],
                "eta": "3-5 minutes",
                "route": f"En direction de {zone}",
                "source": "gRPC - Données réelles"
            }
        else:
            # Aucun véhicule disponible
            result["emergency_vehicles"] = {
                "available": False,
                "type": needed_vehicle_type,
                "message": f"Aucun véhicule de type {needed_vehicle_type} disponible",
                "source": "gRPC - Données réelles"
            }
        
        grpc_client.close()
    except Exception as e:
        result["emergency_vehicles"] = {
            "error": f"Service gRPC indisponible: {str(e)}",
            "fallback": True
        }
    
    # Étape 3: Impact sur les transports en commun
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['transport']}/transports/")
            transports = response.json()
            
            # Simuler l'impact: certains transports doivent être détournés
            affected = [t for t in transports if zone.lower() in t.get("route", "").lower()]
            result["traffic_impact"] = {
                "affected_lines": len(affected),
                "lines": [{"mode": t.get("mode"), "route": t.get("route")} for t in affected],
                "action": "Déviation temporaire pendant l'intervention"
            }
        except Exception as e:
            result["traffic_impact"] = {"error": str(e)}
    
    # Étape 4: Recommandations coordonnées
    result["recommendations"] = [
        f"🚑 Véhicule d'urgence en route vers {zone}",
        f"🚦 Dégager les voies d'accès principales",
        f"🚌 {result['traffic_impact'].get('affected_lines', 0)} lignes de transport à dévier",
    ]
    
    if result["air_quality"].get("aqi", 0) > 100:
        result["recommendations"].append("😷 Personnel d'urgence: utiliser équipement de protection respiratoire")
    
    result["orchestration"] = {
        "services_called": ["emergency (gRPC)", "transport (REST)", "air_quality (SOAP)"],
        "workflow": "SOAP:CheckAirQuality → gRPC:DispatchVehicle → REST:RerouteTransport → coordinate_response",
        "priority": "HIGH",
        "success": True
    }
    
    return result


@app.get("/api/orchestration/eco-route")
async def plan_eco_route(start_zone: str, end_zone: str):
    """
    Scénario 4: Trajet écologique optimisé
    Orchestre: SOAP (qualité air multiple zones) + REST (transports) + GraphQL (points d'intérêt)
    
    Cas d'usage: Calculer le trajet le plus écologique en évitant les zones polluées
    """
    result = {
        "start": start_zone,
        "end": end_zone,
        "route_analysis": {},
        "recommended_path": [],
        "eco_score": 0,
        "alternatives": []
    }
    
    zones_to_check = [start_zone, end_zone, "Centre-Ville"]  # Zones intermédiaires
    air_quality_data = {}
    
    # Étape 1: Analyser la qualité de l'air sur plusieurs zones
    try:
        wsdl_url = f"{SERVICES['air_quality']}/?wsdl"
        soap_client = Client(wsdl_url)
        
        for zone in zones_to_check:
            try:
                measures = soap_client.service.GetMeasuresByStation(zone)
                if measures and len(measures) > 0:
                    air_quality_data[zone] = {
                        "aqi": measures[0].aqi,
                        "status": measures[0].status
                    }
            except:
                air_quality_data[zone] = {"aqi": 75, "status": "Non disponible"}
    except Exception as e:
        result["air_quality_error"] = str(e)
    
    result["route_analysis"] = air_quality_data
    
    # Étape 2: Récupérer les transports écologiques
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['transport']}/transports/")
            transports = response.json()
            
            # Filtrer par transports écologiques
            eco_transports = [t for t in transports 
                            if t.get("status") == "operationnel" 
                            and t.get("mode") in ["Vélo", "Métro", "Tramway"]]
            
            # Calculer le score écologique
            avg_aqi = sum(aq.get("aqi", 75) for aq in air_quality_data.values()) / len(air_quality_data)
            eco_bonus = 10 if len(eco_transports) > 0 else 0
            pollution_penalty = -20 if avg_aqi > 100 else 0
            result["eco_score"] = max(0, 100 + eco_bonus + pollution_penalty - int(avg_aqi/5))
            
            result["recommended_path"] = [
                {"step": 1, "zone": start_zone, "aqi": air_quality_data.get(start_zone, {}).get("aqi", "N/A")},
                {"step": 2, "zone": "Centre-Ville", "aqi": air_quality_data.get("Centre-Ville", {}).get("aqi", "N/A"), 
                 "action": f"Utiliser {eco_transports[0].get('mode')} {eco_transports[0].get('route')}" if eco_transports else "Marcher"},
                {"step": 3, "zone": end_zone, "aqi": air_quality_data.get(end_zone, {}).get("aqi", "N/A")}
            ]
            
            # Proposer des alternatives
            result["alternatives"] = [
                {
                    "name": "Route directe (rapide)",
                    "duration": "15 min",
                    "eco_score": result["eco_score"] - 20,
                    "note": "Plus rapide mais traverse zones polluées"
                },
                {
                    "name": "Route écologique (recommandée)",
                    "duration": "25 min",
                    "eco_score": result["eco_score"],
                    "note": "Évite les zones à AQI élevé"
                }
            ]
            
        except Exception as e:
            result["transport_error"] = str(e)
    
    result["orchestration"] = {
        "services_called": ["air_quality (SOAP - multiple zones)", "transport (REST)", "tourism (GraphQL optional)"],
        "workflow": "SOAP:GetMultipleAQI → analyze_pollution_zones → REST:GetEcoTransports → calculate_best_path",
        "optimization": "eco_score",
        "success": True
    }
    
    return result


@app.get("/api/orchestration/city-dashboard")
async def get_city_dashboard():
    """
    Scénario 5: Tableau de bord complet de la ville
    Orchestre: TOUS les services (REST + SOAP + GraphQL + gRPC)
    
    Cas d'usage: Vue d'ensemble temps réel de l'état de la Smart City
    """
    dashboard = {
        "timestamp": "2025-11-23T14:00:00Z",
        "transport": {},
        "air_quality": {},
        "tourism": {},
        "emergency": {},
        "city_status": "",
        "alerts": []
    }
    
    async with httpx.AsyncClient() as client:
        # Service 1: Transport (REST)
        try:
            response = await client.get(f"{SERVICES['transport']}/transports/")
            transports = response.json()
            operational = len([t for t in transports if t.get("status") == "operationnel"])
            total = len(transports)
            dashboard["transport"] = {
                "total_lines": total,
                "operational": operational,
                "status": "✅ Normal" if operational/total > 0.8 else "⚠️ Perturbations",
                "availability": f"{int(operational/total*100)}%"
            }
        except:
            dashboard["transport"] = {"status": "❌ Service indisponible"}
        
        # Service 2: Qualité de l'air (SOAP)
        try:
            wsdl_url = f"{SERVICES['air_quality']}/?wsdl"
            soap_client = Client(wsdl_url)
            all_measures = soap_client.service.GetAllMeasures()
            
            if all_measures and len(all_measures) > 0:
                avg_aqi = sum(m.aqi for m in all_measures) / len(all_measures)
                bad_zones = len([m for m in all_measures if m.aqi > 100])
                
                dashboard["air_quality"] = {
                    "average_aqi": int(avg_aqi),
                    "status": "✅ Bon" if avg_aqi < 50 else "⚠️ Modéré" if avg_aqi < 100 else "🔴 Mauvais",
                    "zones_monitored": len(all_measures),
                    "polluted_zones": bad_zones
                }
                
                if bad_zones > 0:
                    dashboard["alerts"].append(f"⚠️ {bad_zones} zone(s) avec pollution élevée")
        except:
            dashboard["air_quality"] = {"status": "❌ Service indisponible"}
        
        # Service 3: Tourisme (GraphQL)
        try:
            query = '{ attractions { id name isOpen } }'
            response = await client.post(
                f"{SERVICES['tourism']}/graphql",
                json={"query": query}
            )
            data = response.json()
            if "data" in data:
                attractions = data["data"]["attractions"]
                open_count = len([a for a in attractions if a.get("isOpen") == "open"])
                dashboard["tourism"] = {
                    "total_attractions": len(attractions),
                    "currently_open": open_count,
                    "status": "✅ Actif",
                    "occupancy": f"{int(open_count/len(attractions)*100)}%"
                }
        except:
            dashboard["tourism"] = {"status": "❌ Service indisponible"}
        
        # Service 4: Urgences (gRPC RÉEL)
        try:
            grpc_client = EmergencyClient(SERVICES['emergency'])
            vehicles = grpc_client.get_all_vehicles()
            interventions = grpc_client.get_active_interventions()
            grpc_client.close()
            
            available = len([v for v in vehicles if v['status'] == 'available'])
            on_mission = len([v for v in vehicles if v['status'] == 'on_mission'])
            
            dashboard["emergency"] = {
                "status": "✅ Opérationnel" if available > 0 else "⚠️ Tous véhicules en mission",
                "active_interventions": len(interventions),
                "total_vehicles": len(vehicles),
                "available_vehicles": available,
                "on_mission": on_mission,
                "response_time_avg": "3-5 min",
                "source": "gRPC - Données réelles"
            }
            
            if len(interventions) > 2:
                dashboard["alerts"].append(f"🚨 {len(interventions)} interventions actives")
        except Exception as e:
            dashboard["emergency"] = {
                "status": "❌ Service indisponible",
                "error": str(e)
            }
    
    # Analyse globale de la ville
    services_ok = sum([
        1 if "✅" in str(dashboard["transport"].get("status", "")) else 0,
        1 if "✅" in str(dashboard["air_quality"].get("status", "")) else 0,
        1 if "✅" in str(dashboard["tourism"].get("status", "")) else 0,
        1 if "✅" in str(dashboard["emergency"].get("status", "")) else 0
    ])
    
    if services_ok == 4:
        dashboard["city_status"] = "🌟 Tous systèmes opérationnels"
    elif services_ok >= 3:
        dashboard["city_status"] = "✅ Ville opérationnelle avec perturbations mineures"
    else:
        dashboard["city_status"] = "⚠️ Perturbations importantes détectées"
        dashboard["alerts"].append("🚨 Plusieurs services nécessitent attention")
    
    dashboard["orchestration"] = {
        "services_called": ["transport (REST)", "air_quality (SOAP)", "tourism (GraphQL)", "emergency (gRPC)"],
        "workflow": "parallel_queries → aggregate_data → analyze_city_health → generate_alerts",
        "data_sources": 4,
        "success": True
    }
    
    return dashboard


if __name__ == "__main__":
    import uvicorn
    print("🌐 API Gateway - Smart City")
    print("=" * 50)
    print("Gateway: http://0.0.0.0:8080")
    print("Health Check: http://0.0.0.0:8080/health")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8080)
