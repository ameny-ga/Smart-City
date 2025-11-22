"""Schéma GraphQL avec Strawberry pour le service tourisme."""
import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import AttractionDB
from .database import SessionLocal


@strawberry.type
class Attraction:
    """Type GraphQL pour une attraction touristique."""
    id: int
    name: str
    category: str
    description: Optional[str]
    address: str
    city: str
    latitude: float
    longitude: float
    rating: Optional[float]
    price_level: Optional[int]
    opening_hours: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    image_url: Optional[str]
    is_open: str


@strawberry.input
class AttractionInput:
    """Input pour créer une attraction."""
    name: str
    category: str
    description: Optional[str] = None
    address: str
    city: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    price_level: Optional[int] = None
    opening_hours: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None
    is_open: str = "open"


@strawberry.input
class AttractionUpdateInput:
    """Input pour mettre à jour une attraction."""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    price_level: Optional[int] = None
    opening_hours: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None
    is_open: Optional[str] = None


def db_to_graphql(db_attraction: AttractionDB) -> Attraction:
    """Convertit un modèle DB en type GraphQL."""
    return Attraction(
        id=db_attraction.id,
        name=db_attraction.name,
        category=db_attraction.category,
        description=db_attraction.description,
        address=db_attraction.address,
        city=db_attraction.city,
        latitude=db_attraction.latitude,
        longitude=db_attraction.longitude,
        rating=db_attraction.rating,
        price_level=db_attraction.price_level,
        opening_hours=db_attraction.opening_hours,
        phone=db_attraction.phone,
        website=db_attraction.website,
        image_url=db_attraction.image_url,
        is_open=db_attraction.is_open
    )


@strawberry.type
class Query:
    """Requêtes GraphQL."""
    
    @strawberry.field
    def attractions(self, city: Optional[str] = None, category: Optional[str] = None) -> List[Attraction]:
        """Récupère toutes les attractions avec filtres optionnels."""
        db = SessionLocal()
        try:
            query = db.query(AttractionDB)
            if city:
                query = query.filter(AttractionDB.city.ilike(f"%{city}%"))
            if category:
                query = query.filter(AttractionDB.category == category)
            
            attractions = query.all()
            return [db_to_graphql(a) for a in attractions]
        finally:
            db.close()
    
    @strawberry.field
    def attraction(self, id: int) -> Optional[Attraction]:
        """Récupère une attraction par ID."""
        db = SessionLocal()
        try:
            attraction = db.query(AttractionDB).filter(AttractionDB.id == id).first()
            if attraction:
                return db_to_graphql(attraction)
            return None
        finally:
            db.close()
    
    @strawberry.field
    def attractions_by_rating(self, min_rating: float = 0.0) -> List[Attraction]:
        """Récupère les attractions avec une note minimale."""
        db = SessionLocal()
        try:
            attractions = db.query(AttractionDB).filter(
                AttractionDB.rating >= min_rating
            ).order_by(AttractionDB.rating.desc()).all()
            return [db_to_graphql(a) for a in attractions]
        finally:
            db.close()


@strawberry.type
class Mutation:
    """Mutations GraphQL."""
    
    @strawberry.mutation
    def create_attraction(self, input: AttractionInput) -> Attraction:
        """Crée une nouvelle attraction."""
        db = SessionLocal()
        try:
            new_attraction = AttractionDB(
                name=input.name,
                category=input.category,
                description=input.description,
                address=input.address,
                city=input.city,
                latitude=input.latitude,
                longitude=input.longitude,
                rating=input.rating,
                price_level=input.price_level,
                opening_hours=input.opening_hours,
                phone=input.phone,
                website=input.website,
                image_url=input.image_url,
                is_open=input.is_open
            )
            db.add(new_attraction)
            db.commit()
            db.refresh(new_attraction)
            return db_to_graphql(new_attraction)
        finally:
            db.close()
    
    @strawberry.mutation
    def update_attraction(self, id: int, input: AttractionUpdateInput) -> Optional[Attraction]:
        """Met à jour une attraction."""
        db = SessionLocal()
        try:
            attraction = db.query(AttractionDB).filter(AttractionDB.id == id).first()
            if not attraction:
                return None
            
            if input.name is not None:
                attraction.name = input.name
            if input.category is not None:
                attraction.category = input.category
            if input.description is not None:
                attraction.description = input.description
            if input.address is not None:
                attraction.address = input.address
            if input.city is not None:
                attraction.city = input.city
            if input.latitude is not None:
                attraction.latitude = input.latitude
            if input.longitude is not None:
                attraction.longitude = input.longitude
            if input.rating is not None:
                attraction.rating = input.rating
            if input.price_level is not None:
                attraction.price_level = input.price_level
            if input.opening_hours is not None:
                attraction.opening_hours = input.opening_hours
            if input.phone is not None:
                attraction.phone = input.phone
            if input.website is not None:
                attraction.website = input.website
            if input.image_url is not None:
                attraction.image_url = input.image_url
            if input.is_open is not None:
                attraction.is_open = input.is_open
            
            db.commit()
            db.refresh(attraction)
            return db_to_graphql(attraction)
        finally:
            db.close()
    
    @strawberry.mutation
    def delete_attraction(self, id: int) -> bool:
        """Supprime une attraction."""
        db = SessionLocal()
        try:
            attraction = db.query(AttractionDB).filter(AttractionDB.id == id).first()
            if not attraction:
                return False
            
            db.delete(attraction)
            db.commit()
            return True
        finally:
            db.close()


# Schéma GraphQL
schema = strawberry.Schema(query=Query, mutation=Mutation)
