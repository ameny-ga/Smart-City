# service_soap_air - Qualité de l'Air

Service SOAP pour la gestion et consultation des mesures de qualité de l'air urbain.

## Caractéristiques

- **Protocole**: SOAP 1.1 avec WSDL
- **Framework**: Spyne (Python)
- **Base de données**: SQLite
- **Mesures**: PM2.5, PM10, O3, NO2, CO, AQI

## Installation

```powershell
# Activer l'environnement virtuel
venv\Scripts\activate

# Installer les dépendances
pip install -r service_soap_air\app\requirements.txt

# Initialiser la base de données
python service_soap_air\app\init_db.py
```

## Lancement

```powershell
python service_soap_air\app\app.py
```

Le service sera accessible sur:
- **Endpoint SOAP**: http://0.0.0.0:8001
- **WSDL**: http://0.0.0.0:8001/?wsdl

## Opérations SOAP disponibles

### GetAirQuality
Récupère une mesure par ID.
```xml
<GetAirQuality>
    <measure_id>1</measure_id>
</GetAirQuality>
```

### GetAllMeasures
Liste toutes les mesures.
```xml
<GetAllMeasures/>
```

### GetMeasuresByStation
Filtre par nom de station.
```xml
<GetMeasuresByStation>
    <station_name>Parc des Plantes</station_name>
</GetMeasuresByStation>
```

### AddMeasure
Ajoute une nouvelle mesure.
```xml
<AddMeasure>
    <station_name>Nouvelle Station</station_name>
    <location>Zone test</location>
    <pm25>25.5</pm25>
    <pm10>45.0</pm10>
    <o3>60.0</o3>
    <no2>35.0</no2>
    <co>1.0</co>
    <aqi>75</aqi>
    <status>moderate</status>
</AddMeasure>
```

### UpdateMeasureStatus
Met à jour le statut AQI.
```xml
<UpdateMeasureStatus>
    <measure_id>1</measure_id>
    <new_aqi>120</new_aqi>
    <new_status>unhealthy</new_status>
</UpdateMeasureStatus>
```

## Indicateurs de Qualité (AQI)

- **0-50**: Good (Bon)
- **51-100**: Moderate (Modéré)
- **101-150**: Unhealthy for Sensitive Groups
- **151-200**: Unhealthy (Mauvais)
- **201-300**: Very Unhealthy
- **301-500**: Hazardous (Dangereux)

## Test avec SoapUI ou curl

```powershell
# Télécharger le WSDL
curl http://127.0.0.1:8001/?wsdl -o air_service.wsdl

# Tester GetAllMeasures
curl -X POST http://127.0.0.1:8001/ `
  -H "Content-Type: text/xml" `
  -d @- << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:air="smartcity.air">
  <soap:Body>
    <air:GetAllMeasures/>
  </soap:Body>
</soap:Envelope>
EOF
```
