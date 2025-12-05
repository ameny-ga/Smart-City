"""Serveur gRPC pour le service d'urgence."""
import grpc
from concurrent import futures
from datetime import datetime

import emergency_pb2
import emergency_pb2_grpc
from database import Base, engine, SessionLocal
from models import VehicleDB, InterventionDB


# Créer les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)


class EmergencyServiceServicer(emergency_pb2_grpc.EmergencyServiceServicer):
    """Implémentation du service gRPC."""
    
    def GetVehicle(self, request, context):
        """Récupère un véhicule par ID."""
        db = SessionLocal()
        try:
            vehicle = db.query(VehicleDB).filter(VehicleDB.id == request.id).first()
            if not vehicle:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Vehicle {request.id} not found')
                return emergency_pb2.Vehicle()
            
            return emergency_pb2.Vehicle(
                id=vehicle.id,
                vehicle_type=vehicle.vehicle_type,
                identifier=vehicle.identifier,
                status=vehicle.status,
                latitude=vehicle.latitude,
                longitude=vehicle.longitude,
                station=vehicle.station,
                crew_size=vehicle.crew_size,
                created_at=str(vehicle.created_at)
            )
        finally:
            db.close()
    
    def GetAllVehicles(self, request, context):
        """Récupère tous les véhicules."""
        db = SessionLocal()
        try:
            vehicles = db.query(VehicleDB).all()
            vehicle_list = []
            for v in vehicles:
                vehicle_list.append(emergency_pb2.Vehicle(
                    id=v.id,
                    vehicle_type=v.vehicle_type,
                    identifier=v.identifier,
                    status=v.status,
                    latitude=v.latitude,
                    longitude=v.longitude,
                    station=v.station,
                    crew_size=v.crew_size,
                    created_at=str(v.created_at)
                ))
            return emergency_pb2.VehicleList(vehicles=vehicle_list)
        finally:
            db.close()
    
    def GetAvailableVehicles(self, request, context):
        """Récupère les véhicules disponibles par type."""
        db = SessionLocal()
        try:
            query = db.query(VehicleDB).filter(VehicleDB.status == "available")
            if request.vehicle_type:
                query = query.filter(VehicleDB.vehicle_type == request.vehicle_type)
            
            vehicles = query.all()
            vehicle_list = []
            for v in vehicles:
                vehicle_list.append(emergency_pb2.Vehicle(
                    id=v.id,
                    vehicle_type=v.vehicle_type,
                    identifier=v.identifier,
                    status=v.status,
                    latitude=v.latitude,
                    longitude=v.longitude,
                    station=v.station,
                    crew_size=v.crew_size,
                    created_at=str(v.created_at)
                ))
            return emergency_pb2.VehicleList(vehicles=vehicle_list)
        finally:
            db.close()
    
    def CreateVehicle(self, request, context):
        """Crée un nouveau véhicule."""
        db = SessionLocal()
        try:
            new_vehicle = VehicleDB(
                vehicle_type=request.vehicle_type,
                identifier=request.identifier,
                status=request.status,
                latitude=request.latitude,
                longitude=request.longitude,
                station=request.station,
                crew_size=request.crew_size
            )
            db.add(new_vehicle)
            db.commit()
            db.refresh(new_vehicle)
            
            return emergency_pb2.Vehicle(
                id=new_vehicle.id,
                vehicle_type=new_vehicle.vehicle_type,
                identifier=new_vehicle.identifier,
                status=new_vehicle.status,
                latitude=new_vehicle.latitude,
                longitude=new_vehicle.longitude,
                station=new_vehicle.station,
                crew_size=new_vehicle.crew_size,
                created_at=str(new_vehicle.created_at)
            )
        finally:
            db.close()
    
    def UpdateVehicleStatus(self, request, context):
        """Met à jour le statut d'un véhicule."""
        db = SessionLocal()
        try:
            vehicle = db.query(VehicleDB).filter(VehicleDB.id == request.vehicle_id).first()
            if not vehicle:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Vehicle {request.vehicle_id} not found')
                return emergency_pb2.Vehicle()
            
            vehicle.status = request.new_status
            vehicle.latitude = request.latitude
            vehicle.longitude = request.longitude
            db.commit()
            db.refresh(vehicle)
            
            return emergency_pb2.Vehicle(
                id=vehicle.id,
                vehicle_type=vehicle.vehicle_type,
                identifier=vehicle.identifier,
                status=vehicle.status,
                latitude=vehicle.latitude,
                longitude=vehicle.longitude,
                station=vehicle.station,
                crew_size=vehicle.crew_size,
                created_at=str(vehicle.created_at)
            )
        finally:
            db.close()
    
    def CreateIntervention(self, request, context):
        """Crée une nouvelle intervention."""
        db = SessionLocal()
        try:
            new_intervention = InterventionDB(
                intervention_type=request.intervention_type,
                priority=request.priority,
                address=request.address,
                latitude=request.latitude,
                longitude=request.longitude,
                status="pending",
                assigned_vehicle_id=request.assigned_vehicle_id if request.assigned_vehicle_id > 0 else None,
                description=request.description
            )
            db.add(new_intervention)
            db.commit()
            db.refresh(new_intervention)
            
            return emergency_pb2.Intervention(
                id=new_intervention.id,
                intervention_type=new_intervention.intervention_type,
                priority=new_intervention.priority,
                address=new_intervention.address,
                latitude=new_intervention.latitude,
                longitude=new_intervention.longitude,
                status=new_intervention.status,
                assigned_vehicle_id=new_intervention.assigned_vehicle_id or 0,
                description=new_intervention.description or "",
                created_at=str(new_intervention.created_at),
                completed_at=""
            )
        finally:
            db.close()
    
    def GetActiveInterventions(self, request, context):
        """Récupère les interventions actives."""
        db = SessionLocal()
        try:
            interventions = db.query(InterventionDB).filter(
                InterventionDB.status.in_(["pending", "in_progress"])
            ).all()
            
            intervention_list = []
            for i in interventions:
                intervention_list.append(emergency_pb2.Intervention(
                    id=i.id,
                    intervention_type=i.intervention_type,
                    priority=i.priority,
                    address=i.address,
                    latitude=i.latitude,
                    longitude=i.longitude,
                    status=i.status,
                    assigned_vehicle_id=i.assigned_vehicle_id or 0,
                    description=i.description or "",
                    created_at=str(i.created_at),
                    completed_at=str(i.completed_at) if i.completed_at else ""
                ))
            return emergency_pb2.InterventionList(interventions=intervention_list)
        finally:
            db.close()
    
    def CompleteIntervention(self, request, context):
        """Termine une intervention."""
        db = SessionLocal()
        try:
            intervention = db.query(InterventionDB).filter(InterventionDB.id == request.id).first()
            if not intervention:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Intervention {request.id} not found')
                return emergency_pb2.Intervention()
            
            intervention.status = "completed"
            intervention.completed_at = datetime.now()
            db.commit()
            db.refresh(intervention)
            
            return emergency_pb2.Intervention(
                id=intervention.id,
                intervention_type=intervention.intervention_type,
                priority=intervention.priority,
                address=intervention.address,
                latitude=intervention.latitude,
                longitude=intervention.longitude,
                status=intervention.status,
                assigned_vehicle_id=intervention.assigned_vehicle_id or 0,
                description=intervention.description or "",
                created_at=str(intervention.created_at),
                completed_at=str(intervention.completed_at)
            )
        finally:
            db.close()


def init_demo_data():
    """Initialise les données de démonstration."""
    from init_db import init_db
    try:
        init_db()
    except Exception as e:
        print(f"⚠️ Erreur initialisation DB: {e}")


def serve():
    """Lance le serveur gRPC."""
    # Initialiser les données
    init_demo_data()
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    emergency_pb2_grpc.add_EmergencyServiceServicer_to_server(
        EmergencyServiceServicer(), server
    )
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    
    print("🚑 TuniLink - Service gRPC Urgences")
    print("=" * 50)
    print("🔗 L'expérience urbaine réinventée")
    print("Serveur: 0.0.0.0:50051")
    print("Protocol: gRPC")
    print("Véhicules: 12 (ambulances, pompiers, police)")
    print("Interventions: 6 en base - Grande Tunis")
    print("=" * 50)
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n⚠️ Arrêt du serveur...")
        server.stop(0)


if __name__ == '__main__':
    serve()
