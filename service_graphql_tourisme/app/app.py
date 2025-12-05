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
        # Musées
        AttractionDB(
            name="Musée National du Bardo",
            category="museum",
            description="L'un des plus importants musées de mosaïques romaines au monde. Collection exceptionnelle d'antiquités puniques, romaines et islamiques.",
            address="Place du Bardo, Le Bardo",
            city="Tunis",
            latitude=36.8107,
            longitude=10.1370,
            rating=4.6,
            price_level=2,
            opening_hours="9h30-16h30 (fermé lundi)",
            phone="+216 71 513 650",
            website="https://www.bardomuseum.tn",
            image_url="https://example.com/bardo.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Musée de Carthage",
            category="museum",
            description="Musée archéologique présentant des vestiges puniques et romains de la célèbre Carthage antique.",
            address="Rue de Carthage, Carthage",
            city="Carthage",
            latitude=36.8529,
            longitude=10.3233,
            rating=4.3,
            price_level=2,
            opening_hours="9h-17h",
            phone="+216 71 730 036",
            website="https://www.inp.rnrt.tn",
            image_url="https://example.com/carthage-museum.jpg",
            is_open="open"
        ),
        
        # Sites Archéologiques
        AttractionDB(
            name="Site Archéologique de Carthage",
            category="monument",
            description="Vestiges de l'ancienne cité punique puis romaine. Site classé UNESCO. Thermes d'Antonin, théâtre, amphithéâtre.",
            address="Carthage",
            city="Carthage",
            latitude=36.8528,
            longitude=10.3233,
            rating=4.7,
            price_level=2,
            opening_hours="8h30-17h30",
            phone="+216 71 730 036",
            website="https://whc.unesco.org/fr/list/37",
            image_url="https://example.com/carthage-site.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Thermes d'Antonin",
            category="monument",
            description="Imposants thermes romains du IIe siècle, parmi les plus grands de l'Empire romain. Vue panoramique sur la mer.",
            address="Carthage Antonin",
            city="Carthage",
            latitude=36.8580,
            longitude=10.3257,
            rating=4.5,
            price_level=2,
            opening_hours="8h30-17h",
            phone="+216 71 730 036",
            website="https://www.inp.rnrt.tn",
            image_url="https://example.com/antonin.jpg",
            is_open="open"
        ),
        
        # Villages et Médinas
        AttractionDB(
            name="Sidi Bou Saïd",
            category="monument",
            description="Village pittoresque aux maisons blanches et bleues, perché sur une falaise. Vue spectaculaire sur le golfe de Tunis.",
            address="Sidi Bou Saïd",
            city="Sidi Bou Saïd",
            latitude=36.8687,
            longitude=10.3413,
            rating=4.8,
            price_level=1,
            opening_hours="Accès libre toute la journée",
            phone="+216 71 740 666",
            website="https://www.discovertunisia.com/fr/sidi-bou-said",
            image_url="https://example.com/sidi-bou-said.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Médina de Tunis",
            category="monument",
            description="Centre historique classé UNESCO. Souks authentiques, mosquées, palais. Plus de 700 monuments historiques.",
            address="Médina, Tunis",
            city="Tunis",
            latitude=36.8169,
            longitude=10.1717,
            rating=4.6,
            price_level=1,
            opening_hours="Accès libre 24h/24",
            phone="+216 71 561 550",
            website="https://whc.unesco.org/fr/list/36",
            image_url="https://example.com/medina-tunis.jpg",
            is_open="open"
        ),
        
        # Monuments Religieux
        AttractionDB(
            name="Mosquée Zitouna",
            category="monument",
            description="Grande mosquée de Tunis fondée en 732. Centre spirituel et intellectuel de la Médina. Architecture andalouse et ottomane.",
            address="Place Zitouna, Médina",
            city="Tunis",
            latitude=36.8166,
            longitude=10.1739,
            rating=4.7,
            price_level=1,
            opening_hours="8h-12h (non-musulmans cour uniquement)",
            phone="+216 71 562 838",
            website="https://www.mosqueezitouna.tn",
            image_url="https://example.com/zitouna.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Cathédrale Saint-Vincent-de-Paul",
            category="monument",
            description="Majestueuse cathédrale néo-byzantine construite en 1897. Architecture remarquable avec ses deux tours et sa coupole.",
            address="Avenue Habib Bourguiba",
            city="Tunis",
            latitude=36.8008,
            longitude=10.1815,
            rating=4.4,
            price_level=1,
            opening_hours="9h-12h, 15h-18h",
            phone="+216 71 255 346",
            website="https://www.cathedraletunis.org",
            image_url="https://example.com/cathedrale.jpg",
            is_open="open"
        ),
        
        # Loisirs et Nature
        AttractionDB(
            name="Parc du Belvédère",
            category="park",
            description="Plus grand parc de Tunis avec zoo, lac, jardin botanique. Vue panoramique sur la ville. Idéal pour familles.",
            address="Avenue Taieb Mhiri",
            city="Tunis",
            latitude=36.8220,
            longitude=10.1587,
            rating=4.2,
            price_level=1,
            opening_hours="6h-20h (été), 7h-18h (hiver)",
            phone="+216 71 892 463",
            website="https://www.parcbelvedere.tn",
            image_url="https://example.com/belvedere.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Port de Plaisance Sidi Bou Saïd",
            category="park",
            description="Marina moderne avec restaurants, cafés et boutiques. Vue magnifique sur yachts et mer Méditerranée.",
            address="Port Sidi Bou Saïd",
            city="Sidi Bou Saïd",
            latitude=36.8700,
            longitude=10.3450,
            rating=4.3,
            price_level=2,
            opening_hours="24h/24",
            phone="+216 71 729 300",
            website="https://www.marina-sbs.tn",
            image_url="https://example.com/marina.jpg",
            is_open="open"
        ),
        
        # Restaurants Typiques
        AttractionDB(
            name="Restaurant Dar El Jeld",
            category="restaurant",
            description="Restaurant gastronomique dans un palais du XVIIe siècle. Cuisine tunisienne raffinée dans cadre somptueux.",
            address="5-10 Rue Dar El Jeld, Médina",
            city="Tunis",
            latitude=36.8175,
            longitude=10.1705,
            rating=4.6,
            price_level=4,
            opening_hours="12h-15h, 19h30-23h",
            phone="+216 71 560 916",
            website="https://www.dareljeld.com.tn",
            image_url="https://example.com/dareljeld.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Café des Délices",
            category="restaurant",
            description="Café mythique de Sidi Bou Saïd avec terrasse panoramique. Vue exceptionnelle sur mer et village. Thé à la menthe et pâtisseries.",
            address="Avenue Habib Thameur, Sidi Bou Saïd",
            city="Sidi Bou Saïd",
            latitude=36.8686,
            longitude=10.3422,
            rating=4.5,
            price_level=2,
            opening_hours="8h-minuit",
            phone="+216 71 740 061",
            website="https://www.cafedelices.tn",
            image_url="https://example.com/delices.jpg",
            is_open="open"
        ),
        
        # Hôtels de Luxe
        AttractionDB(
            name="La Badira Hotel",
            category="hotel",
            description="Hôtel 5 étoiles à Hammamet. Architecture contemporaine, spa luxueux, plage privée. Vue mer exceptionnelle.",
            address="Route Touristique, Hammamet",
            city="Hammamet",
            latitude=36.4170,
            longitude=10.5750,
            rating=4.7,
            price_level=4,
            opening_hours="24h/24",
            phone="+216 72 241 444",
            website="https://www.labadira.com",
            image_url="https://example.com/badira.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Hôtel The Residence Tunis",
            category="hotel",
            description="Palace 5 étoiles à Gammarth. Luxe à la tunisienne, spa Thalgo, golf 18 trous, plage privée.",
            address="Les Côtes de Carthage, Gammarth",
            city="Tunis",
            latitude=37.0667,
            longitude=10.2833,
            rating=4.8,
            price_level=4,
            opening_hours="24h/24",
            phone="+216 71 910 101",
            website="https://www.theresidence.com",
            image_url="https://example.com/residence.jpg",
            is_open="open"
        ),
        
        # Plages
        AttractionDB(
            name="Plage de La Marsa",
            category="park",
            description="Belle plage de sable fin prisée par les Tunisois. Restaurants et cafés en bord de mer. Ambiance familiale.",
            address="Corniche La Marsa",
            city="La Marsa",
            latitude=36.8767,
            longitude=10.3250,
            rating=4.1,
            price_level=1,
            opening_hours="Accès libre 24h/24",
            phone="+216 71 742 000",
            website="https://www.tunisia.com/plages",
            image_url="https://example.com/plage-marsa.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Plage de Gammarth",
            category="park",
            description="Plage élégante au nord de Tunis. Eaux cristallines, clubs de plage chics, sports nautiques.",
            address="Gammarth",
            city="Tunis",
            latitude=37.0700,
            longitude=10.2833,
            rating=4.3,
            price_level=2,
            opening_hours="Accès libre 24h/24",
            phone="+216 71 740 800",
            website="https://www.gammarth.tn",
            image_url="https://example.com/gammarth.jpg",
            is_open="open"
        ),
        AttractionDB(
            name="Avenue Habib Bourguiba",
            category="monument",
            description="Avenue principale de Tunis, comparable aux Champs-Élysées. Boutiques, cafés, architecture coloniale française.",
            address="Avenue Habib Bourguiba",
            city="Tunis",
            latitude=36.8008,
            longitude=10.1815,
            rating=4.4,
            price_level=1,
            opening_hours="Accès libre 24h/24",
            phone="+216 71 800 000",
            website="https://www.tunis.gov.tn",
            image_url="https://example.com/bourguiba.jpg",
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
