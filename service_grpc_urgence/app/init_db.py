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
    
    # Véhicules d'urgence - Grande Tunis
    vehicles = [
        # Ambulances
        VehicleDB(
            vehicle_type="ambulance",
            identifier="AMB-TUN-001",
            status="available",
            latitude=36.8065,
            longitude=10.1815,
            station="Hôpital Charles Nicolle",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="ambulance",
            identifier="AMB-TUN-002",
            status="on_mission",
            latitude=36.8485,
            longitude=10.1950,
            station="Hôpital La Rabta",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="ambulance",
            identifier="AMB-TUN-003",
            status="available",
            latitude=36.8167,
            longitude=10.1717,
            station="Hôpital Habib Thameur",
            crew_size=3
        ),
        VehicleDB(
            vehicle_type="ambulance",
            identifier="AMB-ARI-001",
            status="available",
            latitude=36.8667,
            longitude=10.1950,
            station="Hôpital Ariana",
            crew_size=2
        ),
        
        # Camions de pompiers
        VehicleDB(
            vehicle_type="fire_truck",
            identifier="FIRE-TUN-001",
            status="available",
            latitude=36.8100,
            longitude=10.1800,
            station="Caserne Centrale Tunis",
            crew_size=6
        ),
        VehicleDB(
            vehicle_type="fire_truck",
            identifier="FIRE-TUN-002",
            status="maintenance",
            latitude=36.8107,
            longitude=10.1370,
            station="Caserne Bardo",
            crew_size=6
        ),
        VehicleDB(
            vehicle_type="fire_truck",
            identifier="FIRE-MAR-001",
            status="available",
            latitude=36.8767,
            longitude=10.3250,
            station="Caserne La Marsa",
            crew_size=5
        ),
        VehicleDB(
            vehicle_type="fire_truck",
            identifier="FIRE-CAR-001",
            status="available",
            latitude=36.8528,
            longitude=10.3233,
            station="Caserne Carthage",
            crew_size=5
        ),
        
        # Voitures de police
        VehicleDB(
            vehicle_type="police_car",
            identifier="POL-TUN-001",
            status="available",
            latitude=36.8169,
            longitude=10.1717,
            station="Commissariat Médina",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="police_car",
            identifier="POL-TUN-002",
            status="on_mission",
            latitude=36.8008,
            longitude=10.1815,
            station="Commissariat Centre-Ville",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="police_car",
            identifier="POL-ARI-001",
            status="available",
            latitude=36.8667,
            longitude=10.1950,
            station="Commissariat Ariana",
            crew_size=2
        ),
        VehicleDB(
            vehicle_type="police_car",
            identifier="POL-SBS-001",
            status="available",
            latitude=36.8687,
            longitude=10.3413,
            station="Commissariat Sidi Bou Saïd",
            crew_size=2
        ),
    ]
    
    # Interventions - Grande Tunis
    interventions = [
        InterventionDB(
            intervention_type="medical",
            priority="high",
            address="Avenue Habib Bourguiba, Tunis",
            latitude=36.8008,
            longitude=10.1815,
            status="in_progress",
            assigned_vehicle_id=2,
            description="Malaise cardiaque, patient conscient, 65 ans"
        ),
        InterventionDB(
            intervention_type="fire",
            priority="critical",
            address="Rue de la Kasbah, Médina de Tunis",
            latitude=36.8169,
            longitude=10.1717,
            status="pending",
            assigned_vehicle_id=None,
            description="Incendie dans commerce de la Médina, propagation rapide"
        ),
        InterventionDB(
            intervention_type="accident",
            priority="medium",
            address="Route de La Marsa, près Carthage",
            latitude=36.8600,
            longitude=10.3100,
            status="in_progress",
            assigned_vehicle_id=10,
            description="Collision entre 2 véhicules, blessés légers"
        ),
        InterventionDB(
            intervention_type="crime",
            priority="high",
            address="Avenue Mohamed V, Centre-Ville Tunis",
            latitude=36.8020,
            longitude=10.1820,
            status="pending",
            assigned_vehicle_id=None,
            description="Tentative de vol à main armée dans agence bancaire"
        ),
        InterventionDB(
            intervention_type="medical",
            priority="critical",
            address="Sidi Bou Saïd Village",
            latitude=36.8687,
            longitude=10.3413,
            status="pending",
            assigned_vehicle_id=None,
            description="Touriste en arrêt cardiaque, réanimation en cours"
        ),
        InterventionDB(
            intervention_type="accident",
            priority="low",
            address="Port de La Goulette",
            latitude=36.8183,
            longitude=10.3050,
            status="completed",
            assigned_vehicle_id=11,
            description="Accident de travail mineur, intervention terminée"
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
