"""Modèles SQLAlchemy pour la base de données."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class TransportDB(Base):
    """Modèle de transport pour la base de données."""
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mode = Column(String, nullable=False, index=True)
    route = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
