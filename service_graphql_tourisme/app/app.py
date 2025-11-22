"""Application FastAPI avec GraphQL pour le service tourisme."""
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .schema import schema
from .database import Base, engine
from .models import AttractionDB
from .database import SessionLocal
import uvicorn

# Créer les tables
Base.metadata.create_all(bind=engine)

# Initialiser la base de données avec des données
def init_db():
    """Initialise la base de données avec des attractions touristiques."""
    db = SessionLocal()
    
    # Vérifier si la base est déjà remplie
    if db.query(AttractionDB).count() > 0:
        db.close()
        return
    
    attractions = [
        AttractionDB(
            name="Musée du Louvre",
            category="museum",
            description="Le plus grand musée d'art du monde et un monument historique emblématique de Paris.",
            address="Rue de Rivoli, 75001",
            city="Paris",
            latitude=48.8606,
            longitude=2.3376,
            rating=4.7,
            price_level=3,
            opening_hours="9h-18h (fermé mardi)",
            phone="+33 1 40 20 50 50",
            website="https://www.louvre.fr",
            image_url="https://example.com/louvre.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Tour Eiffel",
            category="monument",
            description="Monument emblématique de Paris, symbole de la France dans le monde entier.",
            address="Champ de Mars, 5 Avenue Anatole France, 75007",
            city="Paris",
            latitude=48.8584,
            longitude=2.2945,
            rating=4.6,
            price_level=2,
            opening_hours="9h30-23h45",
            phone="+33 892 70 12 39",
            website="https://www.toureiffel.paris",
            image_url="https://example.com/eiffel.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Jardin du Luxembourg",
            category="park",
            description="Grand jardin public créé en 1612, offrant un cadre paisible au cœur de Paris.",
            address="75006",
            city="Paris",
            latitude=48.8462,
            longitude=2.3372,
            rating=4.8,
            price_level=1,
            opening_hours="7h30-21h30 (variable selon saison)",
            phone="+33 1 42 34 20 00",
            website="https://www.senat.fr/visite/jardin",
            image_url="https://example.com/luxembourg.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Cathédrale Notre-Dame",
            category="monument",
            description="Chef-d'œuvre de l'architecture gothique, actuellement en restauration après l'incendie de 2019.",
            address="6 Parvis Notre-Dame - Pl. Jean-Paul II, 75004",
            city="Paris",
            latitude=48.8530,
            longitude=2.3499,
            rating=4.7,
            price_level=1,
            opening_hours="Temporairement fermé",
            phone="+33 1 42 34 56 10",
            website="https://www.notredamedeparis.fr",
            image_url="https://example.com/notredame.jpg",
            is_open="temporarily_closed"
        ),
        AttractionDB(
            name="Restaurant Le Jules Verne",
            category="restaurant",
            description="Restaurant gastronomique au 2ème étage de la Tour Eiffel, cuisine française raffinée.",
            address="Tour Eiffel, Avenue Gustave Eiffel, 75007",
            city="Paris",
            latitude=48.8582,
            longitude=2.2945,
            rating=4.4,
            price_level=4,
            opening_hours="12h-14h30, 19h-22h30",
            phone="+33 1 45 55 61 44",
            website="https://www.lejulesverne-paris.com",
            image_url="https://example.com/julesverne.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Hôtel Ritz Paris",
            category="hotel",
            description="Palace légendaire situé Place Vendôme, symbole du luxe à la française.",
            address="15 Place Vendôme, 75001",
            city="Paris",
            latitude=48.8676,
            longitude=2.3289,
            rating=4.8,
            price_level=4,
            opening_hours="24h/24",
            phone="+33 1 43 16 30 30",
            website="https://www.ritzparis.com",
            image_url="https://example.com/ritz.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Musée d'Orsay",
            category="museum",
            description="Musée consacré aux arts de la période 1848-1914, avec une importante collection impressionniste.",
            address="1 Rue de la Légion d'Honneur, 75007",
            city="Paris",
            latitude=48.8600,
            longitude=2.3266,
            rating=4.7,
            price_level=2,
            opening_hours="9h30-18h (fermé lundi)",
            phone="+33 1 40 49 48 14",
            website="https://www.musee-orsay.fr",
            image_url="https://example.com/orsay.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Arc de Triomphe",
            category="monument",
            description="Monument emblématique situé en haut des Champs-Élysées, offrant une vue panoramique sur Paris.",
            address="Place Charles de Gaulle, 75008",
            city="Paris",
            latitude=48.8738,
            longitude=2.2950,
            rating=4.7,
            price_level=2,
            opening_hours="10h-23h",
            phone="+33 1 55 37 73 77",
            website="https://www.paris-arc-de-triomphe.fr",
            image_url="https://example.com/arc.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Parc des Buttes-Chaumont",
            category="park",
            description="Parc paysager du 19ème siècle avec un lac, des cascades et une vue imprenable sur Paris.",
            address="1 Rue Botzaris, 75019",
            city="Paris",
            latitude=48.8799,
            longitude=2.3831,
            rating=4.6,
            price_level=1,
            opening_hours="7h-22h",
            phone="+33 1 48 03 83 10",
            website="https://www.paris.fr",
            image_url="https://example.com/buttes.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Restaurant L'Ambroisie",
            category="restaurant",
            description="Restaurant trois étoiles Michelin dans le Marais, cuisine française classique.",
            address="9 Place des Vosges, 75004",
            city="Paris",
            latitude=48.8551,
            longitude=2.3662,
            rating=4.6,
            price_level=4,
            opening_hours="12h-13h30, 20h-21h30 (fermé dimanche-lundi)",
            phone="+33 1 42 78 51 45",
            website="https://www.ambroisie-paris.com",
            image_url="https://example.com/ambroisie.jpg",
            is_open="open"
        )
    ]
    
    db.add_all(attractions)
    db.commit()
    db.close()
    print(f"✅ {len(attractions)} attractions touristiques ajoutées à la base de données")


# Initialiser la DB
init_db()

# Application FastAPI
app = FastAPI(
    title="🏛️ Service GraphQL - Tourisme",
    description="API GraphQL pour gérer les attractions touristiques de la Smart City",
    version="1.0.0"
)

# Router GraphQL avec Strawberry
graphql_app = GraphQLRouter(schema)

# Monter le router GraphQL
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    """Point d'entrée de l'API."""
    return {
        "service": "Tourisme GraphQL",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql",
        "graphql_playground": "http://127.0.0.1:8002/graphql",
        "operations": {
            "queries": ["attractions", "attraction", "attractions_by_rating"],
            "mutations": ["create_attraction", "update_attraction", "delete_attraction"]
        }
    }


@app.get("/health")
def health():
    """Vérification de santé du service."""
    return {"status": "healthy", "service": "tourisme-graphql"}


if __name__ == "__main__":
    print("🏛️ Service GraphQL - Tourisme")
    print("=" * 50)
    print("Serveur: http://127.0.0.1:8002")
    print("GraphQL Playground: http://127.0.0.1:8002/graphql")
    print("Documentation: http://127.0.0.1:8002/docs")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8002)
