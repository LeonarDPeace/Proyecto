import asyncio
import uuid
import random
from datetime import UTC, datetime, timedelta
from sqlalchemy import select
from app.core.database import async_session
from app.models.user import User
from app.models.product import Product
from app.models.negotiation import Negotiation
from app.models.transaction import Transaction

async def seed_variable_sales():
    async with async_session() as db:
        print("Buscando vendedor y productos...")
        
        # 1. Buscar al vendedor demo
        result = await db.execute(select(User).where(User.email == "vendedor@uao.edu.co"))
        seller = result.scalar_one_or_none()
        
        if not seller:
            print("Error: Vendedor no encontrado. Ejecuta seed_demo.py primero.")
            return

        # 2. Buscar al comprador demo
        result = await db.execute(select(User).where(User.email == "comprador@uao.edu.co"))
        buyer = result.scalar_one_or_none()

        # 3. Obtener productos del vendedor
        result = await db.execute(select(Product).where(Product.seller_id == seller.id))
        products = result.scalars().all()
        
        if not products:
            print("Error: El vendedor no tiene productos.")
            return

        print(f"Generando 40 transacciones para {seller.email}...")

        # 4. Generar 40 transacciones aleatorias en los últimos 30 días
        new_objects = []
        for i in range(40):
            product = random.choice(products)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            completed_at = datetime.now(UTC) - timedelta(days=days_ago, hours=hours_ago)
            
            # Cantidad aleatoria (1-3)
            quantity = random.randint(1, 3)
            
            # Precio con variabilidad (negociación simulada +/- 15%)
            variation = random.uniform(0.85, 1.15)
            agreed_price = int(float(product.price) * variation)
            
            subtotal = agreed_price * quantity
            discount = 0
            if random.random() > 0.8: # 20% chance of random discount
                discount = int(subtotal * 0.1)
            
            total = subtotal - discount

            # Crear Negociación primero para cumplir FK
            neg_id = uuid.uuid4()
            neg = Negotiation(
                id=neg_id,
                buyer_id=buyer.id if buyer else None,
                seller_id=seller.id,
                product_id=product.id,
                status="delivered",
                agreed_price_cop=agreed_price,
                quantity=quantity,
                payment_method=random.choice(["efectivo", "nequi", "daviplata"]),
                transaction_locked=True,
                buyer_confirmed=True,
                seller_confirmed=True
            )
            new_objects.append(neg)

            tx = Transaction(
                id=uuid.uuid4(),
                negotiation_id=neg_id,
                product_id=product.id,
                buyer_id=buyer.id if buyer else None,
                seller_id=seller.id,
                product_name=product.name,
                quantity=quantity,
                unit_price_cop=agreed_price,
                subtotal_cop=subtotal,
                discount_cop=discount,
                total_cop=total,
                payment_method=neg.payment_method,
                completed_at=completed_at
            )
            new_objects.append(tx)

        db.add_all(new_objects)
        await db.commit()
        print(f"¡Éxito! Se han agregado 40 nuevas ventas al historial de {seller.name}.")

if __name__ == "__main__":
    asyncio.run(seed_variable_sales())
