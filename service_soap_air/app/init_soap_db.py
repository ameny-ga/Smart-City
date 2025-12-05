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
    
    # Données de qualité d'air pour la Grande Tunis
    measures = [
        # Tunis Centre-Ville - AQI 92 (Modéré) - Zone urbaine dense
        AirQualityDB(
            station_name="Tunis Centre-Ville",
            location="Avenue Habib Bourguiba",
            pm25=32.5,
            pm10=48.0,
            o3=68.0,
            no2=42.0,
            co=0.9,
            aqi=92,
            status="Modéré"
        ),
        # La Marsa - AQI 58 (Bon) - Zone côtière résidentielle
        AirQualityDB(
            station_name="La Marsa",
            location="La Marsa Plage",
            pm25=15.5,
            pm10=28.0,
            o3=52.0,
            no2=22.0,
            co=0.4,
            aqi=58,
            status="Bon"
        ),
        # Sidi Bou Saïd - AQI 48 (Bon) - Village touristique
        AirQualityDB(
            station_name="Sidi Bou Saïd",
            location="Rue Habib Thameur",
            pm25=12.0,
            pm10=24.0,
            o3=45.0,
            no2=18.0,
            co=0.3,
            aqi=48,
            status="Bon"
        ),
        # Carthage - AQI 62 (Bon) - Zone archéologique
        AirQualityDB(
            station_name="Carthage",
            location="Site archéologique",
            pm25=18.0,
            pm10=32.0,
            o3=55.0,
            no2=24.0,
            co=0.5,
            aqi=62,
            status="Bon"
        ),
        # Bardo - AQI 88 (Modéré) - Zone musée et administration
        AirQualityDB(
            station_name="Bardo",
            location="Place du Bardo",
            pm25=30.0,
            pm10=45.0,
            o3=65.0,
            no2=38.0,
            co=0.8,
            aqi=88,
            status="Modéré"
        ),
        # La Goulette - AQI 75 (Modéré) - Zone portuaire
        AirQualityDB(
            station_name="La Goulette",
            location="Port de La Goulette",
            pm25=25.0,
            pm10=40.0,
            o3=60.0,
            no2=35.0,
            co=0.7,
            aqi=75,
            status="Modéré"
        ),
        # Ariana - AQI 95 (Modéré) - Zone résidentielle/commerciale
        AirQualityDB(
            station_name="Ariana",
            location="Centre Ariana",
            pm25=33.0,
            pm10=52.0,
            o3=72.0,
            no2=44.0,
            co=0.95,
            aqi=95,
            status="Modéré"
        ),
        # Ben Arous - AQI 105 (Mauvais pour groupes sensibles) - Zone industrielle
        AirQualityDB(
            station_name="Ben Arous",
            location="Zone Industrielle",
            pm25=38.0,
            pm10=68.0,
            o3=85.0,
            no2=52.0,
            co=1.2,
            aqi=105,
            status="Mauvais pour groupes sensibles"
        ),
        # Aéroport Tunis-Carthage - AQI 98 (Modéré)
        AirQualityDB(
            station_name="Aéroport Tunis-Carthage",
            location="Zone Aéroportuaire",
            pm25=35.0,
            pm10=58.0,
            o3=75.0,
            no2=48.0,
            co=1.0,
            aqi=98,
            status="Modéré"
        ),
        # Hammam-Lif - AQI 70 (Bon) - Zone balnéaire
        AirQualityDB(
            station_name="Hammam-Lif",
            location="Front de mer",
            pm25=22.0,
            pm10=35.0,
            o3=58.0,
            no2=28.0,
            co=0.6,
            aqi=70,
            status="Bon"
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
