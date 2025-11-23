from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session

# Imports locaux
from .database import get_db, engine, Base, SessionLocal
from .models import TransportDB
from . import crud

# Créer les tables au démarrage
Base.metadata.create_all(bind=engine)

# Initialiser les données de démonstration si la base est vide
def init_demo_data():
    """Initialise la base avec des données de démonstration si elle est vide."""
    db = SessionLocal()
    try:
        if db.query(TransportDB).count() == 0:
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
            print(f"✅ {len(transports)} transports initialisés")
    finally:
        db.close()

init_demo_data()

# Métadonnées OpenAPI pour une documentation professionnelle
app = FastAPI(
    title="Service REST Transport - Smart City",
    description="API REST pour la gestion des transports urbains (mobilité)",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI auto-généré
    redoc_url="/redoc"  # ReDoc alternatif
)

# Modèle Pydantic avec validation (Obligatoire pour une bonne note)
class Transport(BaseModel):
    id: int = Field(..., description="Identifiant unique du transport", gt=0)
    mode: str = Field(..., description="Mode de transport (bus, tram, métro, etc.)", min_length=1)
    route: str = Field(..., description="Ligne ou itinéraire (ex: A-B)", min_length=1)
    status: str = Field(..., description="État du transport (on-time, delayed, cancelled)", min_length=1)

    class Config:
        schema_extra = {
            "example": {
                "id": 3,
                "mode": "metro",
                "route": "E-F",
                "status": "on-time"
            }
        }

class TransportCreate(BaseModel):
    mode: str = Field(..., min_length=1)
    route: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)

class TransportUpdate(BaseModel):
    mode: Optional[str] = Field(None, min_length=1)
    route: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, min_length=1)

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Endpoint de santé pour vérifier que le service est opérationnel."""
    count = db.query(TransportDB).count()
    return {"status": "ok", "service": "transport", "transports_count": count}


@app.get("/transports/", response_model=List[Transport], tags=["Transport"])
@app.get("/transport", response_model=List[Transport], tags=["Transport"])
def list_transports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Liste tous les transports disponibles avec pagination."""
    transports = crud.get_transports(db, skip=skip, limit=limit)
    return transports


@app.get("/transports/{transport_id}", response_model=Transport, tags=["Transport"])
@app.get("/transport/{transport_id}", response_model=Transport, tags=["Transport"])
def get_transport(transport_id: int, db: Session = Depends(get_db)):
    """Récupère un transport par son ID."""
    transport = crud.get_transport(db, transport_id)
    if not transport:
        raise HTTPException(status_code=404, detail="Transport non trouvé")
    return transport


@app.post("/transports/", response_model=Transport, status_code=201, tags=["Transport"])
@app.post("/transport", response_model=Transport, status_code=201, tags=["Transport"])
def create_transport(transport: TransportCreate, db: Session = Depends(get_db)):
    """Crée un nouveau transport."""
    new_transport = crud.create_transport(
        db, 
        mode=transport.mode, 
        route=transport.route, 
        status=transport.status
    )
    return new_transport


@app.put("/transports/{transport_id}", response_model=Transport, tags=["Transport"])
@app.put("/transport/{transport_id}", response_model=Transport, tags=["Transport"])
def update_transport(transport_id: int, transport: TransportUpdate, db: Session = Depends(get_db)):
    """Met à jour un transport existant."""
    updated_transport = crud.update_transport(
        db, 
        transport_id, 
        mode=transport.mode, 
        route=transport.route, 
        status=transport.status
    )
    if not updated_transport:
        raise HTTPException(status_code=404, detail="Transport non trouvé")
    return updated_transport


@app.delete("/transports/{transport_id}", status_code=204, tags=["Transport"])
@app.delete("/transport/{transport_id}", status_code=204, tags=["Transport"])
def delete_transport(transport_id: int, db: Session = Depends(get_db)):
    """Supprime un transport."""
    success = crud.delete_transport(db, transport_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transport non trouvé")
    return


# Lancement: 

# pour lancer service: .\venv\Scripts\python.exe -m uvicorn service_rest_transport.app.app:app --host 0.0.0.0 --port 8000 --reload
# 3. Documentation: http://127.0.0.1:8000/docs