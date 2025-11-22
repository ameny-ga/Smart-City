from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session

# Imports locaux
from .database import get_db, engine, Base
from .models import TransportDB
from . import crud

# Créer les tables au démarrage
Base.metadata.create_all(bind=engine)

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


@app.get("/transport", response_model=List[Transport], tags=["Transport"])
def list_transports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Liste tous les transports disponibles avec pagination."""
    transports = crud.get_transports(db, skip=skip, limit=limit)
    return transports


@app.get("/transport/{transport_id}", response_model=Transport, tags=["Transport"])
def get_transport(transport_id: int, db: Session = Depends(get_db)):
    """Récupère un transport par son ID."""
    transport = crud.get_transport(db, transport_id)
    if not transport:
        raise HTTPException(status_code=404, detail="Transport non trouvé")
    return transport


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