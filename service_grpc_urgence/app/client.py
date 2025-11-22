"""Client gRPC pour tester le service d'urgence."""
import grpc
import emergency_pb2
import emergency_pb2_grpc


def run():
    """Exécute les tests du client gRPC."""
    # Connexion au serveur
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = emergency_pb2_grpc.EmergencyServiceStub(channel)
        
        print("🚑 Tests du Service gRPC - Urgences")
        print("=" * 60)
        
        # Test 1: Récupérer tous les véhicules
        print("\n1️⃣ Test: GetAllVehicles()")
        print("-" * 60)
        try:
            response = stub.GetAllVehicles(emergency_pb2.Empty())
            print(f"✅ Nombre de véhicules: {len(response.vehicles)}")
            for vehicle in response.vehicles[:3]:  # Afficher les 3 premiers
                print(f"   • {vehicle.identifier} ({vehicle.vehicle_type}) - {vehicle.status}")
                print(f"     Station: {vehicle.station}")
        except grpc.RpcError as e:
            print(f"❌ Erreur: {e.details()}")
        
        # Test 2: Récupérer un véhicule par ID
        print("\n2️⃣ Test: GetVehicle(id=1)")
        print("-" * 60)
        try:
            response = stub.GetVehicle(emergency_pb2.VehicleRequest(id=1))
            print(f"✅ Véhicule trouvé:")
            print(f"   ID: {response.id}")
            print(f"   Identifiant: {response.identifier}")
            print(f"   Type: {response.vehicle_type}")
            print(f"   Statut: {response.status}")
            print(f"   Station: {response.station}")
            print(f"   Équipage: {response.crew_size} personnes")
            print(f"   Position: ({response.latitude}, {response.longitude})")
        except grpc.RpcError as e:
            print(f"❌ Erreur: {e.details()}")
        
        # Test 3: Récupérer les ambulances disponibles
        print("\n3️⃣ Test: GetAvailableVehicles(type='ambulance')")
        print("-" * 60)
        try:
            response = stub.GetAvailableVehicles(
                emergency_pb2.VehicleTypeRequest(vehicle_type="ambulance")
            )
            print(f"✅ Ambulances disponibles: {len(response.vehicles)}")
            for vehicle in response.vehicles:
                print(f"   • {vehicle.identifier} - {vehicle.station}")
        except grpc.RpcError as e:
            print(f"❌ Erreur: {e.details()}")
        
        # Test 4: Récupérer les interventions actives
        print("\n4️⃣ Test: GetActiveInterventions()")
        print("-" * 60)
        try:
            response = stub.GetActiveInterventions(emergency_pb2.Empty())
            print(f"✅ Interventions actives: {len(response.interventions)}")
            for intervention in response.interventions:
                print(f"   • #{intervention.id} - {intervention.intervention_type.upper()}")
                print(f"     Priorité: {intervention.priority}")
                print(f"     Adresse: {intervention.address}")
                print(f"     Statut: {intervention.status}")
                if intervention.assigned_vehicle_id:
                    print(f"     Véhicule assigné: ID {intervention.assigned_vehicle_id}")
        except grpc.RpcError as e:
            print(f"❌ Erreur: {e.details()}")
        
        # Test 5: Créer une nouvelle intervention
        print("\n5️⃣ Test: CreateIntervention()")
        print("-" * 60)
        try:
            new_intervention = emergency_pb2.InterventionInput(
                intervention_type="medical",
                priority="high",
                address="10 Rue de la République, 75001 Paris",
                latitude=48.8600,
                longitude=2.3400,
                assigned_vehicle_id=1,
                description="Chute avec suspicion de fracture"
            )
            response = stub.CreateIntervention(new_intervention)
            print(f"✅ Intervention créée:")
            print(f"   ID: {response.id}")
            print(f"   Type: {response.intervention_type}")
            print(f"   Priorité: {response.priority}")
            print(f"   Adresse: {response.address}")
            print(f"   Véhicule assigné: {response.assigned_vehicle_id}")
        except grpc.RpcError as e:
            print(f"❌ Erreur: {e.details()}")
        
        # Test 6: Mettre à jour le statut d'un véhicule
        print("\n6️⃣ Test: UpdateVehicleStatus()")
        print("-" * 60)
        try:
            status_update = emergency_pb2.StatusUpdate(
                vehicle_id=1,
                new_status="on_mission",
                latitude=48.8610,
                longitude=2.3410
            )
            response = stub.UpdateVehicleStatus(status_update)
            print(f"✅ Statut du véhicule mis à jour:")
            print(f"   {response.identifier}: {response.status}")
            print(f"   Nouvelle position: ({response.latitude}, {response.longitude})")
        except grpc.RpcError as e:
            print(f"❌ Erreur: {e.details()}")
        
        print("\n" + "=" * 60)
        print("✅ Tests terminés!")


if __name__ == '__main__':
    run()
