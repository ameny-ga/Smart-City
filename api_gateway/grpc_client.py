"""Client gRPC pour communiquer avec le service d'urgence."""
import grpc
import sys
import os

# Ajouter le chemin pour les fichiers proto générés
sys.path.append(os.path.join(os.path.dirname(__file__), 'proto'))

import emergency_pb2
import emergency_pb2_grpc


class EmergencyClient:
    """Client pour communiquer avec le service gRPC d'urgence."""
    
    def __init__(self, host='service-grpc:50051'):
        """Initialise le client gRPC."""
        self.host = host
        self.channel = None
        self.stub = None
    
    def connect(self):
        """Établit la connexion avec le serveur gRPC."""
        if not self.channel:
            self.channel = grpc.insecure_channel(self.host)
            self.stub = emergency_pb2_grpc.EmergencyServiceStub(self.channel)
    
    def close(self):
        """Ferme la connexion."""
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None
    
    def get_all_vehicles(self):
        """Récupère tous les véhicules."""
        try:
            self.connect()
            request = emergency_pb2.Empty()
            response = self.stub.GetAllVehicles(request)
            
            vehicles = []
            for v in response.vehicles:
                vehicles.append({
                    'id': v.id,
                    'vehicle_type': v.vehicle_type,
                    'identifier': v.identifier,
                    'status': v.status,
                    'latitude': v.latitude,
                    'longitude': v.longitude,
                    'station': v.station,
                    'crew_size': v.crew_size,
                    'created_at': v.created_at
                })
            return vehicles
        except grpc.RpcError as e:
            raise Exception(f"Erreur gRPC: {e.code()} - {e.details()}")
    
    def get_available_vehicles(self, vehicle_type=None):
        """Récupère les véhicules disponibles, optionnellement par type."""
        try:
            self.connect()
            request = emergency_pb2.VehicleTypeRequest(vehicle_type=vehicle_type or "")
            response = self.stub.GetAvailableVehicles(request)
            
            vehicles = []
            for v in response.vehicles:
                vehicles.append({
                    'id': v.id,
                    'vehicle_type': v.vehicle_type,
                    'identifier': v.identifier,
                    'status': v.status,
                    'latitude': v.latitude,
                    'longitude': v.longitude,
                    'station': v.station,
                    'crew_size': v.crew_size
                })
            return vehicles
        except grpc.RpcError as e:
            raise Exception(f"Erreur gRPC: {e.code()} - {e.details()}")
    
    def get_vehicle(self, vehicle_id):
        """Récupère un véhicule par ID."""
        try:
            self.connect()
            request = emergency_pb2.VehicleRequest(id=vehicle_id)
            response = self.stub.GetVehicle(request)
            
            return {
                'id': response.id,
                'vehicle_type': response.vehicle_type,
                'identifier': response.identifier,
                'status': response.status,
                'latitude': response.latitude,
                'longitude': response.longitude,
                'station': response.station,
                'crew_size': response.crew_size,
                'created_at': response.created_at
            }
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise Exception(f"Erreur gRPC: {e.code()} - {e.details()}")
    
    def update_vehicle_status(self, vehicle_id, new_status, latitude=0.0, longitude=0.0):
        """Met à jour le statut d'un véhicule."""
        try:
            self.connect()
            request = emergency_pb2.StatusUpdate(
                vehicle_id=vehicle_id,
                new_status=new_status,
                latitude=latitude,
                longitude=longitude
            )
            response = self.stub.UpdateVehicleStatus(request)
            
            return {
                'id': response.id,
                'vehicle_type': response.vehicle_type,
                'identifier': response.identifier,
                'status': response.status,
                'latitude': response.latitude,
                'longitude': response.longitude,
                'station': response.station,
                'crew_size': response.crew_size
            }
        except grpc.RpcError as e:
            raise Exception(f"Erreur gRPC: {e.code()} - {e.details()}")
    
    def get_active_interventions(self):
        """Récupère les interventions actives."""
        try:
            self.connect()
            request = emergency_pb2.Empty()
            response = self.stub.GetActiveInterventions(request)
            
            interventions = []
            for i in response.interventions:
                interventions.append({
                    'id': i.id,
                    'intervention_type': i.intervention_type,
                    'priority': i.priority,
                    'address': i.address,
                    'latitude': i.latitude,
                    'longitude': i.longitude,
                    'status': i.status,
                    'assigned_vehicle_id': i.assigned_vehicle_id if i.assigned_vehicle_id > 0 else None,
                    'description': i.description,
                    'created_at': i.created_at,
                    'completed_at': i.completed_at if i.completed_at else None
                })
            return interventions
        except grpc.RpcError as e:
            raise Exception(f"Erreur gRPC: {e.code()} - {e.details()}")
    
    def create_intervention(self, intervention_type, priority, address, 
                          latitude, longitude, description="", assigned_vehicle_id=None):
        """Crée une nouvelle intervention."""
        try:
            self.connect()
            request = emergency_pb2.InterventionInput(
                intervention_type=intervention_type,
                priority=priority,
                address=address,
                latitude=latitude,
                longitude=longitude,
                assigned_vehicle_id=assigned_vehicle_id or 0,
                description=description
            )
            response = self.stub.CreateIntervention(request)
            
            return {
                'id': response.id,
                'intervention_type': response.intervention_type,
                'priority': response.priority,
                'address': response.address,
                'status': response.status,
                'assigned_vehicle_id': response.assigned_vehicle_id if response.assigned_vehicle_id > 0 else None,
                'description': response.description,
                'created_at': response.created_at
            }
        except grpc.RpcError as e:
            raise Exception(f"Erreur gRPC: {e.code()} - {e.details()}")
    
    def complete_intervention(self, intervention_id):
        """Termine une intervention."""
        try:
            self.connect()
            request = emergency_pb2.InterventionRequest(id=intervention_id)
            response = self.stub.CompleteIntervention(request)
            
            return {
                'id': response.id,
                'status': response.status,
                'completed_at': response.completed_at
            }
        except grpc.RpcError as e:
            raise Exception(f"Erreur gRPC: {e.code()} - {e.details()}")
