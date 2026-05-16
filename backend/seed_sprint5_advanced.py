import asyncio
import logging
import uuid
from datetime import UTC, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_session, engine
from app.models.user import User
from app.models.product import Product
from app.services import typesense_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clean_database(db: AsyncSession):
    """Deletes all users and products to start fresh."""
    logger.info("Cleaning database...")
    await db.execute(text("TRUNCATE TABLE products CASCADE"))
    await db.execute(text("TRUNCATE TABLE users CASCADE"))
    await db.commit()

async def seed_users(db: AsyncSession) -> dict[str, User]:
    """Creates base users."""
    logger.info("Seeding users...")
    users_data = [
        {
            "id": uuid.uuid4(),
            "email": "admin@uao.edu.co",
            "name": "Administrador Principal",
            "institutional_id": "ADM-001",
            "role": "admin",
            "is_verified": True,
        },
        {
            "id": uuid.uuid4(),
            "email": "vendedor@uao.edu.co",
            "name": "Vendedor de Prueba",
            "institutional_id": "VEN-001",
            "role": "vendedor",
            "is_verified": True,
        },
        {
            "id": uuid.uuid4(),
            "email": "comprador@uao.edu.co",
            "name": "Comprador de Prueba",
            "institutional_id": "COM-001",
            "role": "comprador",
            "is_verified": True,
        },
    ]
    
    users = {}
    for data in users_data:
        user = User(
            id=data["id"],
            email=data["email"],
            name=data["name"],
            institutional_id=data["institutional_id"],
            role=data["role"],
            is_verified=data["is_verified"],
            accepted_terms_at=datetime.now(UTC),
        )
        db.add(user)
        users[data["role"]] = user
        
    await db.commit()
    for u in users.values():
        await db.refresh(u)
    return users

async def seed_products(db: AsyncSession, seller: User):
    """Creates a robust catalog of categorized products."""
    logger.info("Seeding products...")
    
    products_data = [
        # Tecnología
        {
            "name": "MacBook Pro M2 16GB",
            "description": "Excelente estado, ciclo de batería en 50. Ideal para diseño y programación.",
            "price": 3500000.0,
            "category": "tecnologia",
            "subcategory": "laptops",
            "condition": "usado",
            "brand": "apple",
            "has_free_shipping": True,
            "attributes": {"ram": "16gb", "storage": "512gb ssd"},
        },
        {
            "name": "iPhone 13 128GB",
            "description": "Como nuevo, en caja original. Libre para cualquier operador.",
            "price": 2100000.0,
            "category": "tecnologia",
            "subcategory": "celulares",
            "condition": "usado",
            "brand": "apple",
            "has_free_shipping": False,
            "attributes": {"color": "midnight", "storage": "128gb"},
        },
        {
            "name": "Audífonos Sony WH-1000XM4",
            "description": "Audífonos con cancelación de ruido. Sellados.",
            "price": 950000.0,
            "category": "tecnologia",
            "subcategory": "audio",
            "condition": "nuevo",
            "brand": "sony",
            "has_free_shipping": True,
            "attributes": {"type": "over-ear", "wireless": "yes"},
        },
        # Moda
        {
            "name": "Chaqueta de Jean Levi's Vintage",
            "description": "Talla M. Clásica chaqueta de jean en perfecto estado.",
            "price": 120000.0,
            "category": "moda",
            "subcategory": "ropa",
            "condition": "usado",
            "brand": "levi's",
            "has_free_shipping": False,
            "attributes": {"size": "m", "color": "blue"},
        },
        {
            "name": "Tenis Nike Air Force 1",
            "description": "Blancos, talla 40. Nunca usados, error de talla.",
            "price": 380000.0,
            "category": "moda",
            "subcategory": "calzado",
            "condition": "nuevo",
            "brand": "nike",
            "has_free_shipping": True,
            "attributes": {"size": "40", "color": "white"},
        },
        # Comida
        {
            "name": "Combo Empanadas x5",
            "description": "Deliciosas empanadas de carne o pollo con ají casero.",
            "price": 10000.0,
            "category": "comida",
            "subcategory": "snacks",
            "condition": "nuevo",
            "brand": "casero",
            "has_free_shipping": False,
            "attributes": {"type": "frito", "flavor": "carne/pollo"},
        },
        {
            "name": "Brownies Melcochudos de Chocolate",
            "description": "Caja de 4 brownies artesanales. Perfectos para el antojo.",
            "price": 12000.0,
            "category": "comida",
            "subcategory": "postres",
            "condition": "nuevo",
            "brand": "artesanal",
            "has_free_shipping": False,
            "attributes": {"type": "dulce", "units": 4},
        },
        # Académico
        {
            "name": "Libro: Cálculo de Stewart 8va Edición",
            "description": "Físico, en muy buen estado. Algunas páginas resaltadas.",
            "price": 85000.0,
            "category": "academico",
            "subcategory": "libros",
            "condition": "usado",
            "brand": "cengage",
            "has_free_shipping": False,
            "attributes": {"subject": "matematicas", "edition": 8},
        },
        {
            "name": "Calculadora Científica Casio fx-991EX",
            "description": "ClassWiz, ideal para ingenierías. Funciona perfecto.",
            "price": 95000.0,
            "category": "academico",
            "subcategory": "útiles",
            "condition": "usado",
            "brand": "casio",
            "has_free_shipping": True,
            "attributes": {"type": "cientifica", "model": "fx-991EX"},
        },
    ]

    for data in products_data:
        product = Product(
            seller_id=seller.id,
            name=data["name"],
            description=data["description"],
            price=data["price"],
            category=data["category"],
            subcategory=data["subcategory"],
            condition=data["condition"],
            brand=data["brand"],
            has_free_shipping=data["has_free_shipping"],
            attributes=data["attributes"],
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        # Upsert in Typesense
        try:
            await typesense_service.upsert_product_document(db, product)
            logger.info(f"Indexed product: {product.name}")
        except Exception as e:
            logger.error(f"Failed to index {product.name}: {e}")

async def main():
    logger.info("Initializing Seed Script for Sprint 5 Advanced...")
    async with async_session() as db:
        await clean_database(db)
        
        # Initialize Typesense collection
        logger.info("Ensuring Typesense collection exists...")
        await typesense_service.ensure_products_collection()
        
        users = await seed_users(db)
        seller = users["vendedor"]
        
        await seed_products(db, seller)
    
    logger.info("Seed completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
