"""Modèles SQLAlchemy pour le service tourisme."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from .database import Base


class AttractionDB(Base):
    """Modèle pour une attraction touristique."""
    __tablename__ = "attractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)  # museum, monument, park, restaurant, hotel
    description = Column(Text, nullable=True)
    address = Column(String(300), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)  # Note de 0 à 5
    price_level = Column(Integer, nullable=True)  # 1 (€) à 4 (€€€€)
    opening_hours = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(300), nullable=True)
    image_url = Column(String(500), nullable=True)
    is_open = Column(String(20), nullable=False, default="open")  # open, closed, temporarily_closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
