"""API Gateway - Centralise l'accès aux 4 microservices."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Dict, Any
import asyncio
from zeep import Client
from zeep.exceptions import Fault
from grpc_client import EmergencyClient
from auth import verify_credentials, require_admin
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(
    title="🌐 API Gateway - TuniLink",
    description="L'expérience urbaine réinventée - Point d'entrée centralisé pour tous les microservices de la Grande Tunis",
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

# Configuration API externe pour données météo/qualité d'air en temps réel
# OpenWeatherMap Air Pollution API (gratuite - 1000 appels/jour)
# Inscription: https://openweathermap.org/api/air-pollution
import os
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
OPENWEATHER_AIR_API = "http://api.openweathermap.org/data/2.5/air_pollution"

# Coordonnées GPS des zones de Tunis
TUNIS_ZONES_GPS = {
    "Tunis Centre-Ville": {"lat": 36.8065, "lon": 10.1815},
    "La Marsa": {"lat": 36.8764, "lon": 10.3253},
    "Carthage": {"lat": 36.8530, "lon": 10.3233},
    "Sidi Bou Saïd": {"lat": 36.8687, "lon": 10.3413},
    "Ariana": {"lat": 36.8625, "lon": 10.1956},
    "Bardo": {"lat": 36.8107, "lon": 10.1370},
    "La Goulette": {"lat": 36.8186, "lon": 10.3053},
    "Aéroport Tunis-Carthage": {"lat": 36.8510, "lon": 10.2272},
    "Ben Arous": {"lat": 36.7542, "lon": 10.2189},
    "Hammam-Lif": {"lat": 36.7292, "lon": 10.3439}
}


async def get_real_time_air_quality(zone: str) -> Dict[str, Any]:
    """
    Récupère les données de qualité d'air en temps réel via OpenWeatherMap API.
    
    Retourne:
    - aqi: Air Quality Index (1-5 selon OpenWeather, converti en 0-500 US EPA)
    - status: Description textuelle
    - components: PM2.5, PM10, O3, NO2, CO, etc.
    - source: "OpenWeatherMap API" ou "SOAP fallback"
    """
    # Récupérer les coordonnées GPS de la zone
    coords = TUNIS_ZONES_GPS.get(zone, TUNIS_ZONES_GPS["Tunis Centre-Ville"])
    
    # Si pas de clé API configurée, utiliser le service SOAP local
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "votre_cle_api_ici":
        print(f"⚠️ Pas de clé OpenWeather configurée, utilisation du service SOAP local")
        return await get_soap_air_quality(zone)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                OPENWEATHER_AIR_API,
                params={
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "appid": OPENWEATHER_API_KEY
                }
            )
            
            if response.status_code != 200:
                print(f"⚠️ Erreur API OpenWeather (code {response.status_code}), fallback SOAP")
                return await get_soap_air_quality(zone)
            
            data = response.json()
            
            # Extraire les données de pollution
            aqi_index = data["list"][0]["main"]["aqi"]  # 1-5 selon OpenWeather
            components = data["list"][0]["components"]
            
            # Convertir l'index OpenWeather (1-5) en AQI US EPA (0-500)
            # 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
            aqi_conversion = {1: 25, 2: 60, 3: 90, 4: 130, 5: 200}
            aqi_value = aqi_conversion.get(aqi_index, 75)
            
            # Calculer un AQI plus précis basé sur PM2.5 (norme US EPA)
            pm25 = components.get("pm2_5", 0)
            if pm25 <= 12.0:
                aqi_from_pm25 = (50 / 12.0) * pm25
            elif pm25 <= 35.4:
                aqi_from_pm25 = 50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1)
            elif pm25 <= 55.4:
                aqi_from_pm25 = 100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5)
            elif pm25 <= 150.4:
                aqi_from_pm25 = 150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5)
            else:
                aqi_from_pm25 = 200 + ((300 - 200) / (250.4 - 150.5)) * min(pm25 - 150.5, 100)
            
            # Utiliser la valeur la plus élevée entre l'index OpenWeather et le calcul PM2.5
            final_aqi = int(max(aqi_value, aqi_from_pm25))
            
            # Déterminer le statut
            if final_aqi <= 50:
                status = "Bon"
            elif final_aqi <= 100:
                status = "Modéré"
            elif final_aqi <= 150:
                status = "Mauvais pour groupes sensibles"
            elif final_aqi <= 200:
                status = "Mauvais"
            else:
                status = "Très mauvais"
            
            return {
                "aqi": final_aqi,
                "status": status,
                "components": {
                    "pm2_5": components.get("pm2_5", 0),
                    "pm10": components.get("pm10", 0),
                    "o3": components.get("o3", 0),
                    "no2": components.get("no2", 0),
                    "co": components.get("co", 0)
                },
                "source": "OpenWeatherMap API (temps réel)",
                "coordinates": coords
            }
            
    except Exception as e:
        print(f"⚠️ Erreur lors de l'appel OpenWeather API: {e}")
        return await get_soap_air_quality(zone)


async def get_soap_air_quality(zone: str) -> Dict[str, Any]:
    """
    Fallback: utilise le service SOAP local si l'API externe échoue.
    """
    try:
        wsdl_url = f"{SERVICES['air_quality']}/?wsdl"
        soap_client = Client(wsdl_url)
        measures = soap_client.service.GetMeasuresByStation(zone)
        
        if measures and len(measures) > 0:
            measure = measures[0]
            return {
                "aqi": measure.aqi,
                "status": measure.status,
                "components": {
                    "pm2_5": float(measure.pm25) if measure.pm25 else 0,
                    "pm10": float(measure.pm10) if measure.pm10 else 0,
                    "o3": float(measure.o3) if measure.o3 else 0,
                    "no2": float(measure.no2) if measure.no2 else 0,
                    "co": float(measure.co) if measure.co else 0
                },
                "source": "Service SOAP local"
            }
    except Exception as e:
        print(f"⚠️ Erreur SOAP: {e}")
    
    # Dernière option: données par défaut
    return {
        "aqi": 75,
        "status": "Données non disponibles",
        "components": {"pm2_5": 0, "pm10": 0, "o3": 0, "no2": 0, "co": 0},
        "source": "Données par défaut"
    }


@app.get("/")
def root():
    """Page d'accueil de la Gateway."""
    return {
        "service": "API Gateway - TuniLink",
        "slogan": "L'expérience urbaine réinventée",
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


@app.get("/api/auth/me")
async def get_current_user(user: dict = Depends(verify_credentials)):
    """Retourne les informations de l'utilisateur connecté."""
    return {
        "username": user["username"],
        "role": user["role"],
        "full_name": user["full_name"],
        "permissions": {
            "can_create_transport": user["role"] == "admin",
            "can_update_transport": user["role"] == "admin",
            "can_delete_transport": user["role"] == "admin",
            "can_view_transport": True
        }
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
async def create_transport(data: Dict[str, Any], admin: dict = Depends(require_admin)):
    """Crée un nouveau transport. [ADMIN ONLY]"""
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
async def update_transport(transport_id: int, data: Dict[str, Any], admin: dict = Depends(require_admin)):
    """Met à jour un transport. [ADMIN ONLY]"""
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
async def delete_transport(transport_id: int, admin: dict = Depends(require_admin)):
    """Supprime un transport. [ADMIN ONLY]"""
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
    """
    Liste toutes les mesures de qualité de l'air EN TEMPS RÉEL pour les 10 zones de Tunis.
    Utilise l'API OpenWeatherMap pour chaque zone avec fallback SOAP.
    """
    measures = []
    
    # Récupérer les données en temps réel pour chaque zone
    for zone_name, coords in TUNIS_ZONES_GPS.items():
        try:
            # Utiliser l'API temps réel pour chaque zone
            air_data = await get_real_time_air_quality(zone_name)
            
            measures.append({
                "id": len(measures) + 1,
                "station": zone_name,
                "location": f"GPS: {coords['lat']}, {coords['lon']}",
                "pm25": air_data["components"].get("pm2_5", 0),
                "pm10": air_data["components"].get("pm10", 0),
                "o3": air_data["components"].get("o3", 0),
                "no2": air_data["components"].get("no2", 0),
                "co": air_data["components"].get("co", 0),
                "aqi": air_data["aqi"],
                "quality": air_data["status"],
                "source": air_data.get("source", "Unknown")
            })
        except Exception as e:
            print(f"⚠️ Erreur pour zone {zone_name}: {e}")
            # En cas d'erreur, utiliser le fallback SOAP
            try:
                wsdl_url = f"{SERVICES['air_quality']}/?wsdl"
                soap_client = Client(wsdl_url)
                response = soap_client.service.GetMeasuresByStation(zone_name)
                if response and len(response) > 0:
                    measure = response[0]
                    measures.append({
                        "id": len(measures) + 1,
                        "station": measure.station_name,
                        "location": measure.location,
                        "pm25": float(measure.pm25),
                        "pm10": float(measure.pm10),
                        "o3": float(measure.o3) if measure.o3 else None,
                        "no2": float(measure.no2) if measure.no2 else None,
                        "co": float(measure.co) if measure.co else None,
                        "aqi": measure.aqi,
                        "quality": measure.status,
                        "source": "Service SOAP local (fallback)"
                    })
            except Exception as soap_error:
                print(f"⚠️ Erreur SOAP fallback pour {zone_name}: {soap_error}")
    
    return measures


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
async def plan_trip(zone: str = "Tunis Centre-Ville"):
    """
    Orchestre plusieurs services pour planifier un trajet intelligent :
    1. Vérifie la qualité de l'air pour la zone (SOAP)
    2. Génère une recommandation basée sur l'AQI
    3. Récupère les transports disponibles pour cette zone (REST)
    4. Priorise les transports selon la qualité de l'air
    
    Zones supportées: Tunis Centre-Ville, La Marsa, Carthage, Sidi Bou Saïd, 
                     Ariana, Bardo, La Goulette, Aéroport Tunis-Carthage
    """
    result = {
        "zone": zone,
        "air_quality": {},
        "recommendation": "",
        "transports": []
    }
    
    # Étape 1 : Qualité de l'air EN TEMPS RÉEL (OpenWeatherMap API ou SOAP fallback)
    air_data = await get_real_time_air_quality(zone)
    aqi_value = air_data["aqi"]
    air_status = air_data["status"]
    
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
        "source": air_data.get("source", "SOAP service"),
        "components": air_data.get("components", {}),
        "real_time": "OpenWeatherMap" in air_data.get("source", "")
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
            
            # Filtrer strictement par zone géographique
            # Extraire les mots-clés significatifs de la zone (enlever les mots génériques)
            generic_words = ['tunis', 'centre', 'ville']
            zone_words = zone.lower().split()
            zone_keywords = [w for w in zone_words if w not in generic_words]
            
            # Si tous les mots sont génériques, garder au moins "centre-ville" complet
            if not zone_keywords and 'centre' in zone_words:
                zone_keywords = ['centre-ville', 'centre']
            elif not zone_keywords:
                zone_keywords = zone_words
            
            zone_transports = []
            
            for t in available_transports:
                route_lower = t.get("route", "").lower()
                
                # Vérifier si au moins un mot-clé significatif de la zone est dans la route
                if any(keyword in route_lower for keyword in zone_keywords):
                    zone_transports.append(t)
            
            # Utiliser uniquement les transports de la zone (pas de fallback)
            filtered_transports = zone_transports
            
            # Prioriser selon la qualité de l'air
            if aqi_value > 100:
                # Mauvaise qualité : privilégier métro, bus, train (transports fermés)
                priority_modes = ["Métro", "Bus", "Train", "Taxi"]
                prioritized = [t for t in filtered_transports if t.get("mode") in priority_modes]
                result["transports"] = prioritized[:5] if prioritized else filtered_transports[:5]
            else:
                # Bonne qualité : tous les transports sont OK, avec préférence pour vélo si AQI < 50
                if aqi_value < 50:
                    # Excellent air : promouvoir vélo et marche
                    eco_modes = ["Vélo", "Bus", "Métro", "Train"]
                    prioritized = [t for t in filtered_transports if t.get("mode") in eco_modes]
                    result["transports"] = prioritized[:8] if prioritized else filtered_transports[:8]
                else:
                    result["transports"] = filtered_transports[:8]
                
        except Exception as e:
            result["transports_error"] = f"Service transport indisponible: {str(e)}"
            result["transports"] = []
    
    result["orchestration"] = {
        "services_called": ["air_quality (SOAP)", "transport (REST)"],
        "workflow": "SOAP:GetMeasuresByStation → analyze_AQI → REST:GetTransports → filter_by_air_quality",
        "success": True
    }
    
    return result


@app.get("/api/air-quality/real-time")
async def get_real_time_air(zone: str = "Tunis Centre-Ville"):
    """
    🌍 Endpoint dédié pour récupérer les données de qualité d'air EN TEMPS RÉEL
    
    Source principale: OpenWeatherMap Air Pollution API
    Fallback: Service SOAP local
    
    Params:
        zone: Zone géographique (Tunis Centre-Ville, La Marsa, Carthage, etc.)
    
    Returns:
        - aqi: Air Quality Index (0-500)
        - status: Qualité textuelle (Bon, Modéré, Mauvais, etc.)
        - components: PM2.5, PM10, O3, NO2, CO
        - source: Source des données (API externe ou SOAP local)
        - real_time: True si données en temps réel
    """
    air_data = await get_real_time_air_quality(zone)
    
    # Déterminer la couleur
    aqi = air_data["aqi"]
    if aqi <= 50:
        color = "green"
    elif aqi <= 100:
        color = "yellow"
    elif aqi <= 150:
        color = "orange"
    else:
        color = "red"
    
    return {
        "zone": zone,
        "aqi": aqi,
        "status": air_data["status"],
        "color": color,
        "components": air_data.get("components", {}),
        "source": air_data.get("source", "Unknown"),
        "real_time": "OpenWeatherMap" in air_data.get("source", ""),
        "coordinates": air_data.get("coordinates", TUNIS_ZONES_GPS.get(zone, {})),
        "timestamp": "now"
    }


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
    from datetime import datetime
    
    dashboard = {
        "timestamp": datetime.now().isoformat(),
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
        
        # Service 2: Qualité de l'air (TEMPS RÉEL - OpenWeatherMap)
        try:
            # Récupérer les données en temps réel pour toutes les zones
            all_aqi_values = []
            zones_monitored = 0
            bad_zones = 0
            
            for zone_name in TUNIS_ZONES_GPS.keys():
                try:
                    air_data = await get_real_time_air_quality(zone_name)
                    aqi = air_data["aqi"]
                    all_aqi_values.append(aqi)
                    zones_monitored += 1
                    if aqi > 100:
                        bad_zones += 1
                except:
                    continue
            
            if all_aqi_values:
                avg_aqi = sum(all_aqi_values) / len(all_aqi_values)
                
                dashboard["air_quality"] = {
                    "average_aqi": int(avg_aqi),
                    "status": "✅ Bon" if avg_aqi < 50 else "⚠️ Modéré" if avg_aqi < 100 else "🔴 Mauvais",
                    "zones_monitored": zones_monitored,
                    "polluted_zones": bad_zones,
                    "source": "OpenWeatherMap API (temps réel)"
                }
                
                if bad_zones > 0:
                    dashboard["alerts"].append(f"⚠️ {bad_zones} zone(s) avec pollution élevée")
            else:
                dashboard["air_quality"] = {"status": "❌ Données non disponibles"}
        except Exception as e:
            print(f"⚠️ Erreur récupération qualité air dashboard: {e}")
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
    # Vérifier si les services sont opérationnels (pas d'erreur et données présentes)
    transport_ok = "❌" not in str(dashboard["transport"].get("status", "")) and dashboard["transport"].get("operational", 0) > 0
    air_ok = "❌" not in str(dashboard["air_quality"].get("status", "")) and dashboard["air_quality"].get("average_aqi") is not None
    tourism_ok = "❌" not in str(dashboard["tourism"].get("status", "")) and dashboard["tourism"].get("total_attractions", 0) > 0
    emergency_ok = "❌" not in str(dashboard["emergency"].get("status", "")) and "error" not in dashboard["emergency"]
    
    services_ok = sum([transport_ok, air_ok, tourism_ok, emergency_ok])
    
    if services_ok == 4:
        dashboard["city_status"] = "🌟 Tous systèmes opérationnels"
    elif services_ok >= 3:
        dashboard["city_status"] = "✅ Ville opérationnelle"
    elif services_ok >= 2:
        dashboard["city_status"] = "⚠️ Perturbations détectées"
    else:
        dashboard["city_status"] = "🔴 Perturbations importantes"
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
