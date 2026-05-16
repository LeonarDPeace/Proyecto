import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from sqlalchemy import select
from app.core.database import async_session, AsyncSession
from app.models.user import User
from app.models.product import Product
from app.models.negotiation import Negotiation
from app.models.chat_message import ChatMessage
from app.models.transaction import Transaction
from app.models.gmv_metric import GmvMetric
from app.models.coupon import Coupon
from app.models.rating import Rating
from app.models.location import Location
from app.services.typesense_service import upsert_product_document

async def seed_demo_data():
    async with async_session() as db:
        # 1. Crear Usuarios
        print("Creando usuarios...")
        
        buyer = User(
            id=uuid.uuid4(),
            email="comprador@uao.edu.co",
            name="Comprador UAO",
            institutional_id="2200111",
            role="comprador",
            is_verified=True,
            vendor_status="pending",
            accepted_terms_at=datetime.now(UTC)
        )
        
        seller = User(
            id=uuid.uuid4(),
            email="vendedor@uao.edu.co",
            name="Emprendedor Vera",
            institutional_id="2200222",
            role="vendedor",
            is_verified=True,
            vendor_status="approved",
            phone="3001234567",
            average_rating=5.0,
            total_reviews=1,
            accepted_terms_at=datetime.now(UTC)
        )
        
        db.add_all([buyer, seller])
        await db.commit()
        await db.refresh(buyer)
        await db.refresh(seller)

        # 2. Ubicación del Vendedor (UAO - Cafetería Central aprox)
        loc = Location(
            user_id=seller.id,
            campus="UAO",
            label="Cafetería Central",
            coordinates="POINT(-76.5320 3.3516)"
        )
        db.add(loc)
        await db.commit()

        # 3. Cupones
        print("Creando cupones...")
        c1 = Coupon(
            seller_id=seller.id,
            code="PROMO10",
            discount_percent=10.0,
            max_uses=100,
            is_active=True
        )
        c2 = Coupon(
            seller_id=seller.id,
            code="UAO5000",
            discount_fixed_cop=5000.0,
            max_uses=50,
            is_active=True
        )
        db.add_all([c1, c2])
        await db.commit()

        # 4. Productos (Diversificados para filtros)
        print("Creando catálogo diversificado...")
        products = [
            Product(
                id=uuid.uuid4(),
                seller_id=seller.id, name="Notebook Profesional", category="papelería",
                price=55000, stock=10, condition="nuevo", fulfillment_type="merchant",
                payment_methods=["nequi", "daviplata"], image_urls=["https://images.unsplash.com/photo-1517842645767-c639042777db"],
                is_active=True
            ),
            Product(
                id=uuid.uuid4(),
                seller_id=seller.id, name="Smartphone Reacondicionado", category="tecnología",
                price=1200000, stock=2, condition="reacondicionado", fulfillment_type="veramarket",
                discount_percentage=15.0, payment_methods=["nequi"], image_urls=["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"],
                is_active=True
            ),
            Product(
                id=uuid.uuid4(),
                seller_id=seller.id, name="Morral Ergonómico", category="accesorios",
                price=85000, stock=5, condition="nuevo", fulfillment_type="merchant",
                payment_methods=["efectivo"], image_urls=["https://images.unsplash.com/photo-1553062407-98eeb64c6a62"],
                has_free_shipping=True, is_active=True
            ),
            Product(
                id=uuid.uuid4(),
                seller_id=seller.id, name="Libro Cálculo Stewart", category="libros",
                price=45000, stock=1, condition="usado", fulfillment_type="merchant",
                payment_methods=["efectivo", "nequi"], image_urls=["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c"],
                is_active=True
            ),
            Product(
                id=uuid.uuid4(),
                seller_id=seller.id, name="Café Gourmet UAO", category="comida",
                price=6000, stock=50, condition="nuevo", fulfillment_type="merchant",
                discount_percentage=5.0, payment_methods=["efectivo"], image_urls=["https://images.unsplash.com/photo-1509042239860-f550ce710b93"],
                is_active=True
            ),
            Product(
                id=uuid.uuid4(),
                seller_id=seller.id, name="Audífonos Bluetooth", category="tecnología",
                price=150000, stock=0, condition="nuevo", fulfillment_type="merchant",
                payment_methods=["daviplata"], is_active=False, image_urls=["https://images.unsplash.com/photo-1505740420928-5e560c06d30e"]
            ),
        ]
        db.add_all(products)
        await db.commit()

        # 5. Negociaciones y Transacciones (Historial)
        print("Generando transacciones de prueba...")
        
        # Venta 1: Completada (Café)
        n1 = Negotiation(
            id=uuid.uuid4(),
            buyer_id=buyer.id, seller_id=seller.id, product_id=products[4].id,
            status="delivered", agreed_price_cop=6000, quantity=2,
            payment_method="efectivo", transaction_locked=True,
            buyer_confirmed=True, seller_confirmed=True
        )
        db.add(n1)
        await db.commit()
        
        t1 = Transaction(
            id=uuid.uuid4(),
            negotiation_id=n1.id, product_id=products[4].id, buyer_id=buyer.id, seller_id=seller.id,
            product_name=products[4].name, quantity=2, unit_price_cop=6000,
            subtotal_cop=12000, discount_cop=0, total_cop=12000,
            payment_method="efectivo", completed_at=datetime.now(UTC) - timedelta(days=2)
        )
        db.add(t1)
        db.add(GmvMetric(negotiation_id=n1.id, product_id=products[4].id, buyer_id=buyer.id, seller_id=seller.id, amount_cop=12000, product_name=products[4].name))
        await db.commit()

        # Venta 2: Completada (Libro con Cupón + Calificación)
        n2 = Negotiation(
            id=uuid.uuid4(),
            buyer_id=buyer.id, seller_id=seller.id, product_id=products[3].id,
            status="delivered", agreed_price_cop=45000, quantity=1,
            payment_method="nequi", coupon_code="UAO5000", discount_amount=5000,
            transaction_locked=True, buyer_confirmed=True, seller_confirmed=True
        )
        db.add(n2)
        await db.commit()
        
        t2 = Transaction(
            id=uuid.uuid4(),
            negotiation_id=n2.id, product_id=products[3].id, buyer_id=buyer.id, seller_id=seller.id,
            product_name=products[3].name, quantity=1, unit_price_cop=45000,
            subtotal_cop=45000, discount_cop=5000, total_cop=40000,
            payment_method="nequi", coupon_code="UAO5000", completed_at=datetime.now(UTC) - timedelta(hours=5)
        )
        db.add(t2)
        db.add(GmvMetric(negotiation_id=n2.id, product_id=products[3].id, buyer_id=buyer.id, seller_id=seller.id, amount_cop=40000, product_name=products[3].name))
        await db.commit()
        
        # Calificación de la Venta 2
        rating = Rating(
            id=uuid.uuid4(),
            transaction_id=t2.id, rater_id=buyer.id, rated_user_id=seller.id,
            score=5, comment="Excelente vendedor, el libro está como nuevo."
        )
        db.add(rating)
        await db.commit()

        # Negociaciones Varias
        n3 = Negotiation(id=uuid.uuid4(), buyer_id=buyer.id, seller_id=seller.id, product_id=products[0].id, status="accepted", agreed_price_cop=55000, quantity=1)
        n4 = Negotiation(id=uuid.uuid4(), buyer_id=buyer.id, seller_id=seller.id, product_id=products[1].id, status="pending", agreed_price_cop=1200000, quantity=1)
        n5 = Negotiation(id=uuid.uuid4(), buyer_id=buyer.id, seller_id=seller.id, product_id=products[2].id, status="cancelled", agreed_price_cop=85000, quantity=1)
        db.add_all([n3, n4, n5])
        await db.commit()

        db.add(ChatMessage(id=uuid.uuid4(), negotiation_id=n4.id, sender_id=buyer.id, content="Hola, ¿todavía lo tienes disponible?"))
        await db.commit()

        # 6. Sincronizar Typesense
        print("Sincronizando Typesense...")
        for p in products:
            await upsert_product_document(db, p)

        print("\n--- SEMILLA FINALIZADA CON ÉXITO ---")

        print(f"VENDEDOR:  vendedor@uao.edu.co")
        print(f"COMPRADOR: comprador@uao.edu.co")
        print("-" * 35)

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
