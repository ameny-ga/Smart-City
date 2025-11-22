"""Opérations CRUD pour la base de données."""
from sqlalchemy.orm import Session
from .models import TransportDB
from typing import List, Optional


def get_transport(db: Session, transport_id: int) -> Optional[TransportDB]:
    """Récupère un transport par son ID."""
    return db.query(TransportDB).filter(TransportDB.id == transport_id).first()


def get_transports(db: Session, skip: int = 0, limit: int = 100) -> List[TransportDB]:
    """Récupère une liste de transports avec pagination."""
    return db.query(TransportDB).offset(skip).limit(limit).all()


def create_transport(db: Session, mode: str, route: str, status: str) -> TransportDB:
    """Crée un nouveau transport."""
    db_transport = TransportDB(mode=mode, route=route, status=status)
    db.add(db_transport)
    db.commit()
    db.refresh(db_transport)
    return db_transport


def update_transport(
    db: Session, 
    transport_id: int, 
    mode: Optional[str] = None,
    route: Optional[str] = None,
    status: Optional[str] = None
) -> Optional[TransportDB]:
    """Met à jour un transport existant."""
    db_transport = get_transport(db, transport_id)
    if not db_transport:
        return None
    
    if mode is not None:
        db_transport.mode = mode
    if route is not None:
        db_transport.route = route
    if status is not None:
        db_transport.status = status
    
    db.commit()
    db.refresh(db_transport)
    return db_transport


def delete_transport(db: Session, transport_id: int) -> bool:
    """Supprime un transport."""
    db_transport = get_transport(db, transport_id)
    if not db_transport:
        return False
    
    db.delete(db_transport)
    db.commit()
    return True
