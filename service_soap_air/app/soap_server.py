"""Service SOAP simple pour la qualité de l'air avec Spyne."""
from spyne import Application, rpc, ServiceBase, Integer, Float, Unicode, Array
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model.complex import ComplexModel
from wsgiref.simple_server import make_server
from sqlalchemy import create_engine, Column, Integer as SQLInteger, Float as SQLFloat, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os

# Configuration SQLite (volume Docker monté sur /app/data)
DATABASE_URL = "sqlite:///./data/air_quality.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Modèle ORM
class AirQualityDB(Base):
    """Modèle SQLAlchemy pour les mesures."""
    __tablename__ = "air_quality"
    
    id = Column(SQLInteger, primary_key=True, autoincrement=True)
    station_name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    pm25 = Column(SQLFloat, nullable=False)
    pm10 = Column(SQLFloat, nullable=False)
    o3 = Column(SQLFloat, nullable=True)
    no2 = Column(SQLFloat, nullable=True)
    co = Column(SQLFloat, nullable=True)
    aqi = Column(SQLInteger, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Créer tables (commenté pour préserver les données)
# Base.metadata.create_all(bind=engine)


# Modèle SOAP
class AirQualityMeasure(ComplexModel):
    """Modèle SOAP pour une mesure."""
    __namespace__ = 'smartcity.air'
    
    measure_id = Integer
    station_name = Unicode
    location = Unicode
    pm25 = Float
    pm10 = Float
    o3 = Float
    no2 = Float
    co = Float
    aqi = Integer
    status = Unicode
    timestamp = Unicode


class AirQualityService(ServiceBase):
    """Service SOAP."""
    
    @rpc(Integer, _returns=AirQualityMeasure)
    def GetAirQuality(ctx, measure_id):
        """Récupère une mesure par ID."""
        db = SessionLocal()
        try:
            m = db.query(AirQualityDB).filter(AirQualityDB.id == measure_id).first()
            if not m:
                return None
            return AirQualityMeasure(
                measure_id=m.id, station_name=m.station_name, location=m.location,
                pm25=m.pm25, pm10=m.pm10, o3=m.o3, no2=m.no2, co=m.co,
                aqi=m.aqi, status=m.status, timestamp=str(m.created_at)
            )
        finally:
            db.close()
    
    @rpc(_returns=Array(AirQualityMeasure))
    def GetAllMeasures(ctx):
        """Liste toutes les mesures."""
        db = SessionLocal()
        try:
            measures = db.query(AirQualityDB).all()
            result = []
            for m in measures:
                result.append(AirQualityMeasure(
                    measure_id=m.id, station_name=m.station_name, location=m.location,
                    pm25=m.pm25, pm10=m.pm10, o3=m.o3, no2=m.no2, co=m.co,
                    aqi=m.aqi, status=m.status, timestamp=str(m.created_at)
                ))
            return result
        finally:
            db.close()
    
    @rpc(Unicode, _returns=Array(AirQualityMeasure))
    def GetMeasuresByStation(ctx, station_name):
        """Récupère les mesures d'une station."""
        db = SessionLocal()
        try:
            measures = db.query(AirQualityDB).filter(
                AirQualityDB.station_name.like(f"%{station_name}%")
            ).all()
            result = []
            for m in measures:
                result.append(AirQualityMeasure(
                    measure_id=m.id, station_name=m.station_name, location=m.location,
                    pm25=m.pm25, pm10=m.pm10, o3=m.o3, no2=m.no2, co=m.co,
                    aqi=m.aqi, status=m.status, timestamp=str(m.created_at)
                ))
            return result
        finally:
            db.close()
    
    @rpc(Unicode, Unicode, Float, Float, Float, Float, Float, Integer, Unicode, 
         _returns=AirQualityMeasure)
    def AddMeasure(ctx, station_name, location, pm25, pm10, o3, no2, co, aqi, status):
        """Ajoute une mesure."""
        db = SessionLocal()
        try:
            new_m = AirQualityDB(
                station_name=station_name, location=location,
                pm25=pm25, pm10=pm10, o3=o3, no2=no2, co=co,
                aqi=aqi, status=status
            )
            db.add(new_m)
            db.commit()
            db.refresh(new_m)
            return AirQualityMeasure(
                measure_id=new_m.id, station_name=new_m.station_name, location=new_m.location,
                pm25=new_m.pm25, pm10=new_m.pm10, o3=new_m.o3, no2=new_m.no2, co=new_m.co,
                aqi=new_m.aqi, status=new_m.status, timestamp=str(new_m.created_at)
            )
        finally:
            db.close()
    
    @rpc(Integer, Unicode, _returns=Unicode)
    def UpdateMeasureStatus(ctx, measure_id, new_status):
        """Met à jour le statut d'une mesure."""
        db = SessionLocal()
        try:
            m = db.query(AirQualityDB).filter(AirQualityDB.id == measure_id).first()
            if not m:
                return "Erreur: Mesure non trouvée"
            m.status = new_status
            db.commit()
            return f"Statut mis à jour: {new_status}"
        finally:
            db.close()


# Application SOAP
application = Application(
    [AirQualityService],
    tns='smartcity.air',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)


def init_demo_data():
    """Initialise la base avec des mesures pour la Grande Tunis."""
    db = SessionLocal()
    try:
        if db.query(AirQualityDB).count() > 0:
            print("ℹ️  Base de données SOAP déjà initialisée")
            return
        
        # Données de qualité d'air pour la Grande Tunis
        measures = [
            # Tunis Centre-Ville - AQI 92 (Modéré) - Zone urbaine dense
            AirQualityDB(station_name="Tunis Centre-Ville", location="Avenue Habib Bourguiba", pm25=32.5, pm10=48.0, o3=68.0, no2=42.0, co=0.9, aqi=92, status="Modéré"),
            # La Marsa - AQI 58 (Bon) - Zone côtière résidentielle
            AirQualityDB(station_name="La Marsa", location="La Marsa Plage", pm25=15.5, pm10=28.0, o3=52.0, no2=22.0, co=0.4, aqi=58, status="Bon"),
            # Sidi Bou Saïd - AQI 48 (Bon) - Village touristique
            AirQualityDB(station_name="Sidi Bou Saïd", location="Rue Habib Thameur", pm25=12.0, pm10=24.0, o3=45.0, no2=18.0, co=0.3, aqi=48, status="Bon"),
            # Carthage - AQI 62 (Bon) - Zone archéologique
            AirQualityDB(station_name="Carthage", location="Site archéologique", pm25=18.0, pm10=32.0, o3=55.0, no2=24.0, co=0.5, aqi=62, status="Bon"),
            # Bardo - AQI 88 (Modéré) - Zone musée et administration
            AirQualityDB(station_name="Bardo", location="Place du Bardo", pm25=30.0, pm10=45.0, o3=65.0, no2=38.0, co=0.8, aqi=88, status="Modéré"),
            # La Goulette - AQI 75 (Modéré) - Zone portuaire
            AirQualityDB(station_name="La Goulette", location="Port de La Goulette", pm25=25.0, pm10=40.0, o3=60.0, no2=35.0, co=0.7, aqi=75, status="Modéré"),
            # Ariana - AQI 95 (Modéré) - Zone résidentielle/commerciale
            AirQualityDB(station_name="Ariana", location="Centre Ariana", pm25=33.0, pm10=52.0, o3=72.0, no2=44.0, co=0.95, aqi=95, status="Modéré"),
            # Ben Arous - AQI 105 (Mauvais pour groupes sensibles) - Zone industrielle
            AirQualityDB(station_name="Ben Arous", location="Zone Industrielle", pm25=38.0, pm10=68.0, o3=85.0, no2=52.0, co=1.2, aqi=105, status="Mauvais pour groupes sensibles"),
            # Aéroport Tunis-Carthage - AQI 98 (Modéré)
            AirQualityDB(station_name="Aéroport Tunis-Carthage", location="Zone Aéroportuaire", pm25=35.0, pm10=58.0, o3=75.0, no2=48.0, co=1.0, aqi=98, status="Modéré"),
            # Hammam-Lif - AQI 70 (Bon) - Zone balnéaire
            AirQualityDB(station_name="Hammam-Lif", location="Front de mer", pm25=22.0, pm10=35.0, o3=58.0, no2=28.0, co=0.6, aqi=70, status="Bon")
        ]
        db.add_all(measures)
        db.commit()
        print(f"✅ {len(measures)} mesures de qualité d'air ajoutées")
    finally:
        db.close()


if __name__ == '__main__':
    print("🌍 TuniLink - Service SOAP Qualité de l'Air")
    print("=" * 50)
    print("🔗 L'expérience urbaine réinventée")
    print("Serveur: http://0.0.0.0:8001")
    print("WSDL: http://0.0.0.0:8001/?wsdl")
    print("=" * 50)
    
    # Initialiser les données
    # print("🌫️ Initialisation des données...")
    # init_demo_data()  # Désactivé pour utiliser les données existantes
    
    server = make_server('0.0.0.0', 8001, wsgi_app)
    print("✅ Serveur démarré")
    server.serve_forever()

