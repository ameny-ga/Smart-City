"""Script d'initialisation de la base de données Transport."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, Base, engine
from models import TransportDB

# Créer les tables
Base.metadata.create_all(bind=engine)

def init_db():
    """Initialise la base de données avec des données de démonstration."""
    db = SessionLocal()
    
    # Vérifier si la base est déjà remplie
    if db.query(TransportDB).count() > 0:
        print("ℹ️  Base de données déjà initialisée")
        db.close()
        return
    
    transports = [
        TransportDB(mode="Bus", route="Ligne 1", status="operationnel"),
        TransportDB(mode="Bus", route="Ligne 2", status="operationnel"),
        TransportDB(mode="Bus", route="Ligne 5", status="en_maintenance"),
        TransportDB(mode="Métro", route="Ligne A", status="operationnel"),
        TransportDB(mode="Métro", route="Ligne B", status="operationnel"),
        TransportDB(mode="Métro", route="Ligne C", status="retard"),
        TransportDB(mode="Tramway", route="T1", status="operationnel"),
        TransportDB(mode="Tramway", route="T2", status="operationnel"),
        TransportDB(mode="Tramway", route="T3", status="hors_service"),
        TransportDB(mode="Train", route="RER A", status="operationnel"),
        TransportDB(mode="Train", route="RER B", status="retard"),
        TransportDB(mode="Vélo", route="Station Centre-Ville", status="operationnel"),
        TransportDB(mode="Vélo", route="Station Gare", status="operationnel"),
        TransportDB(mode="Taxi", route="Zone Nord", status="operationnel"),
    ]
    
    db.add_all(transports)
    db.commit()
    print(f"✅ {len(transports)} transports ajoutés à la base de données")
    db.close()

if __name__ == "__main__":
    print("🚌 Initialisation de la base de données transport...")
    init_db()
    print("✅ Initialisation terminée")
