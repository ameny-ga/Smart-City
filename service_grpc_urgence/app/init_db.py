"""Script d'initialisation de la base de données urgence."""
from database import Base, engine, SessionLocal
from models import VehicleDB, InterventionDB


def init_db():
    """Initialise la base de données avec des véhicules et interventions."""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Vérifier si déjà remplie
    if db.query(VehicleDB).count() > 0:
        print("ℹ️  Base de données déjà initialisée")
        db.close()
        return
    
    # Véhicules d'urgence
    vehicles = [
        VehicleDB(
            vehicle_type="ambulance",
            identifier="AMB-001",
            status="available",
            latitude=48.8566,
            longitude=2.3522,
            station="Hôpital Cochin",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="ambulance",
            identifier="AMB-002",
            status="on_mission",
            latitude=48.8606,
            longitude=2.3376,
            station="Hôpital Saint-Louis",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="fire_truck",
            identifier="FIRE-001",
            status="available",
            latitude=48.8520,
            longitude=2.3466,
            station="Caserne Sévigné",
            crew_size=6
        ),
        VehicleDB(
            vehicle_type="fire_truck",
            identifier="FIRE-002",
            status="maintenance",
            latitude=48.8738,
            longitude=2.2950,
            station="Caserne Champerret",
            crew_size=6
        ),
        VehicleDB(
            vehicle_type="police_car",
            identifier="POL-001",
            status="available",
            latitude=48.8767,
            longitude=2.3469,
            station="Commissariat 18e",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="police_car",
            identifier="POL-002",
            status="on_mission",
            latitude=48.8422,
            longitude=2.3218,
            station="Commissariat 14e",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="ambulance",
            identifier="AMB-003",
            status="available",
            latitude=48.8462,
            longitude=2.3372,
            station="Hôpital Val-de-Grâce",
            crew_size=3
        ),
        VehicleDB(
            vehicle_type="fire_truck",
            identifier="FIRE-003",
            status="available",
            latitude=48.8584,
            longitude=2.2945,
            station="Caserne Tour Eiffel",
            crew_size=5
        ),
    ]
    
    # Interventions
    interventions = [
        InterventionDB(
            intervention_type="medical",
            priority="high",
            address="15 Rue de Rivoli, 75001 Paris",
            latitude=48.8606,
            longitude=2.3376,
            status="in_progress",
            assigned_vehicle_id=2,
            description="Malaise cardiaque, patient conscient"
        ),
        InterventionDB(
            intervention_type="fire",
            priority="critical",
            address="230 Boulevard Voltaire, 75011 Paris",
            latitude=48.8520,
            longitude=2.3800,
            status="pending",
            assigned_vehicle_id=None,
            description="Incendie dans un appartement au 3ème étage"
        ),
        InterventionDB(
            intervention_type="accident",
            priority="medium",
            address="Avenue des Champs-Élysées, 75008 Paris",
            latitude=48.8698,
            longitude=2.3078,
            status="in_progress",
            assigned_vehicle_id=6,
            description="Accident de la route, 2 véhicules impliqués"
        ),
        InterventionDB(
            intervention_type="crime",
            priority="high",
            address="12 Rue de la Paix, 75002 Paris",
            latitude=48.8692,
            longitude=2.3314,
            status="pending",
            assigned_vehicle_id=None,
            description="Cambriolage en cours dans une bijouterie"
        ),
    ]
    
    db.add_all(vehicles)
    db.add_all(interventions)
    db.commit()
    db.close()
    print(f"✅ {len(vehicles)} véhicules et {len(interventions)} interventions ajoutés")


if __name__ == '__main__':
    print("🚑 Initialisation de la base de données urgence...")
    init_db()
    print("✅ Initialisation terminée")
