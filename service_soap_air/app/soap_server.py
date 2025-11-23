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


# Créer tables
Base.metadata.create_all(bind=engine)


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
    """Initialise la base avec des mesures pour les 5 zones."""
    db = SessionLocal()
    try:
        if db.query(AirQualityDB).count() > 0:
            print("ℹ️  Base de données SOAP déjà initialisée")
            return
        
        measures = [
            AirQualityDB(station_name="Centre-Ville", location="Centre-Ville", pm25=28.5, pm10=42.0, o3=65.0, no2=38.0, co=0.8, aqi=85, status="Modéré"),
            AirQualityDB(station_name="Zone Nord", location="Zone Nord", pm25=48.0, pm10=85.0, o3=95.0, no2=62.0, co=1.5, aqi=120, status="Mauvais pour groupes sensibles"),
            AirQualityDB(station_name="Zone Sud", location="Zone Sud", pm25=12.0, pm10=25.0, o3=45.0, no2=18.0, co=0.3, aqi=45, status="Bon"),
            AirQualityDB(station_name="Gare", location="Gare", pm25=32.0, pm10=58.0, o3=72.0, no2=45.0, co=1.0, aqi=95, status="Modéré"),
            AirQualityDB(station_name="Aéroport", location="Aéroport", pm25=42.0, pm10=78.0, o3=88.0, no2=55.0, co=1.3, aqi=110, status="Mauvais pour groupes sensibles")
        ]
        db.add_all(measures)
        db.commit()
        print(f"✅ {len(measures)} mesures de qualité d'air ajoutées")
    finally:
        db.close()


if __name__ == '__main__':
    print("🌍 Service SOAP - Qualité de l'Air")
    print("=" * 50)
    print("Serveur: http://0.0.0.0:8001")
    print("WSDL: http://0.0.0.0:8001/?wsdl")
    print("=" * 50)
    
    # Initialiser les données
    print("🌫️ Initialisation des données...")
    init_demo_data()
    
    server = make_server('0.0.0.0', 8001, wsgi_app)
    print("✅ Serveur démarré")
    server.serve_forever()

