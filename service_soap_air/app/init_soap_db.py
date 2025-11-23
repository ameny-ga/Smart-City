"""Script d'initialisation de la base de données SOAP (Qualité de l'air)."""
from database import SessionLocal, Base, engine
from models import AirQualityDB

# Créer les tables
Base.metadata.create_all(bind=engine)

def init_soap_data():
    """Initialise la base avec des mesures pour les 5 zones."""
    db = SessionLocal()
    
    # Vérifier si déjà remplie
    if db.query(AirQualityDB).count() > 0:
        print("ℹ️  Base de données SOAP déjà initialisée")
        db.close()
        return
    
    # Données de qualité d'air pour chaque zone
    measures = [
        # Centre-Ville - AQI 85 (Modéré)
        AirQualityDB(
            station_name="Centre-Ville",
            location="Centre-Ville",
            pm25=28.5,
            pm10=42.0,
            o3=65.0,
            no2=38.0,
            co=0.8,
            aqi=85,
            status="Modéré"
        ),
        # Zone Nord - AQI 120 (Mauvais pour groupes sensibles)
        AirQualityDB(
            station_name="Zone Nord",
            location="Zone Nord",
            pm25=48.0,
            pm10=85.0,
            o3=95.0,
            no2=62.0,
            co=1.5,
            aqi=120,
            status="Mauvais pour groupes sensibles"
        ),
        # Zone Sud - AQI 45 (Bon)
        AirQualityDB(
            station_name="Zone Sud",
            location="Zone Sud",
            pm25=12.0,
            pm10=25.0,
            o3=45.0,
            no2=18.0,
            co=0.3,
            aqi=45,
            status="Bon"
        ),
        # Gare - AQI 95 (Modéré)
        AirQualityDB(
            station_name="Gare",
            location="Gare",
            pm25=32.0,
            pm10=58.0,
            o3=72.0,
            no2=45.0,
            co=1.0,
            aqi=95,
            status="Modéré"
        ),
        # Aéroport - AQI 110 (Mauvais pour groupes sensibles)
        AirQualityDB(
            station_name="Aéroport",
            location="Aéroport",
            pm25=42.0,
            pm10=78.0,
            o3=88.0,
            no2=55.0,
            co=1.3,
            aqi=110,
            status="Mauvais pour groupes sensibles"
        )
    ]
    
    db.add_all(measures)
    db.commit()
    print(f"✅ {len(measures)} mesures de qualité d'air ajoutées")
    db.close()

if __name__ == "__main__":
    print("🌫️ Initialisation de la base de données qualité de l'air...")
    init_soap_data()
    print("✅ Initialisation terminée")
