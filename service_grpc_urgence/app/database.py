"""Configuration de la base de données pour le service urgence."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Chemin de la base de données (volume Docker persistant)
DATABASE_URL = "sqlite:///./data/urgence.db"

# Configuration du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles ORM
Base = declarative_base()
