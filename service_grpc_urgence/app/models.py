"""Modèles SQLAlchemy pour le service urgence."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class VehicleDB(Base):
    """Modèle pour un véhicule d'urgence."""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_type = Column(String(50), nullable=False)  # ambulance, fire_truck, police_car
    identifier = Column(String(50), nullable=False, unique=True)  # AMB-001, FIRE-003, POL-012
    status = Column(String(50), nullable=False, default="available")  # available, on_mission, maintenance
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    station = Column(String(200), nullable=False)  # Caserne/Station de rattachement
    crew_size = Column(Integer, nullable=False, default=2)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InterventionDB(Base):
    """Modèle pour une intervention d'urgence."""
    __tablename__ = "interventions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_type = Column(String(50), nullable=False)  # medical, fire, crime, accident
    priority = Column(String(20), nullable=False)  # low, medium, high, critical
    address = Column(String(300), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, in_progress, completed
    assigned_vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
