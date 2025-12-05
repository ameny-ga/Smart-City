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
        # Métro de Tunis
        TransportDB(mode="Métro", route="Ligne 1 (Sud → Nord)", status="operationnel"),
        TransportDB(mode="Métro", route="Ligne 2 (Ariana → Carthage)", status="operationnel"),
        TransportDB(mode="Métro", route="Ligne 3 (La Marsa → Den Den)", status="en_maintenance"),
        TransportDB(mode="Métro", route="Ligne 4 (Tunis Marine → El Mourouj)", status="operationnel"),
        TransportDB(mode="Métro", route="Ligne 5 (Bab Alioua → Ben Arous)", status="operationnel"),
        TransportDB(mode="Métro", route="Ligne 6 (Barcelone → Cité Olympique)", status="retard"),
        
        # TGM (Tunis-Goulette-Marsa)
        TransportDB(mode="Train", route="TGM Tunis → La Marsa", status="operationnel"),
        TransportDB(mode="Train", route="TGM Tunis → Carthage-Hannibal", status="operationnel"),
        TransportDB(mode="Train", route="TGM Tunis → Salammbô", status="operationnel"),
        
        # Bus urbains Grande Tunis
        TransportDB(mode="Bus", route="Ligne 20 - Tunis Centre → Ariana", status="operationnel"),
        TransportDB(mode="Bus", route="Ligne 35 - La Goulette → Sidi Bou Saïd", status="operationnel"),
        TransportDB(mode="Bus", route="Ligne 45 - Bardo → Carthage", status="operationnel"),
        TransportDB(mode="Bus", route="Ligne 50 - Tunis → La Marsa", status="operationnel"),
        TransportDB(mode="Bus", route="Ligne 60 - Mégrine → Hammam-Lif", status="retard"),
        TransportDB(mode="Bus", route="Ligne 70 - Ben Arous → Ezzahra", status="operationnel"),
        TransportDB(mode="Bus", route="Ligne 80 - Ariana → Ennasr", status="en_maintenance"),
        
        # Louages (taxis collectifs)
        TransportDB(mode="Taxi", route="Louage Tunis → Hammamet", status="operationnel"),
        TransportDB(mode="Taxi", route="Louage Tunis → Nabeul", status="operationnel"),
        TransportDB(mode="Taxi", route="Louage Tunis → Bizerte", status="operationnel"),
        TransportDB(mode="Taxi", route="Taxi Tunis Centre-Ville", status="operationnel"),
        
        # Vélos en libre-service
        TransportDB(mode="Vélo", route="Station Avenue Habib Bourguiba", status="operationnel"),
        TransportDB(mode="Vélo", route="Station Belvédère", status="operationnel"),
        TransportDB(mode="Vélo", route="Station Carthage", status="operationnel"),
        TransportDB(mode="Vélo", route="Station La Marsa Plage", status="hors_service"),
        TransportDB(mode="Vélo", route="Station Sidi Bou Saïd", status="operationnel"),
    ]
    
    db.add_all(transports)
    db.commit()
    print(f"✅ {len(transports)} transports ajoutés à la base de données")
    db.close()

if __name__ == "__main__":
    print("🚌 Initialisation de la base de données transport...")
    init_db()
    print("✅ Initialisation terminée")
