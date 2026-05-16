import asyncio
import uuid
from datetime import datetime, UTC
from sqlalchemy import select, text

from app.core.database import async_session
from app.models.user import User
from app.models.product import Product
from app.models.negotiation import Negotiation
from app.models.rating import Rating
from app.services.rating_service import _update_user_reputation


async def seed_demo_reputation():
    async with async_session() as db:
        # 1. Obtener el vendedor
        res = await db.execute(select(User).where(User.email == "demo@veramarket.co"))
        seller = res.scalar_one_or_none()
        
        if not seller:
            res = await db.execute(select(User).limit(1))
            seller = res.scalar_one_or_none()
            
        if not seller:
            print("No se encontró ningún usuario en la DB para actuar como vendedor.")
            return
        
        print(f"Usando vendedor: {seller.email} ({seller.id})")
        
        # Cleanup previo para evitar duplicados en la demo
        await db.execute(text("DELETE FROM ratings WHERE reviewer_id IN (SELECT id FROM users WHERE email = 'buyer@veramarket.co')"))
        await db.execute(text("DELETE FROM negotiations WHERE buyer_id IN (SELECT id FROM users WHERE email = 'buyer@veramarket.co')"))
        await db.commit()



        # 2. Obtener o crear un comprador (buyer@veramarket.co)
        res = await db.execute(select(User).where(User.email == "buyer@veramarket.co"))
        buyer = res.scalar_one_or_none()
        if not buyer:
            buyer = User(
                email="buyer@veramarket.co",
                institutional_id="1234567",
                name="Juan Comprador",
                role="comprador",
                is_verified=True,
                accepted_terms_at=datetime.now(UTC)
            )
            db.add(buyer)
            await db.flush()
            print(f"Comprador creado: {buyer.email}")


        # 3. Obtener productos del vendedor
        res = await db.execute(select(Product).where(Product.seller_id == seller.id).limit(2))
        products = res.scalars().all()
        if len(products) < 2:
            # Crear productos si no hay suficientes
            for i in range(len(products), 2):
                p = Product(
                    name=f"Producto Demo {i+1}",
                    description="Descripción del producto de prueba para reputación",
                    price=25000.0,
                    seller_id=seller.id,
                    is_active=True
                )
                db.add(p)
                await db.flush()
                products.append(p)
            print("Productos de prueba creados.")

        # 4. Crear 2 negociaciones entregadas y sus calificaciones
        for i, product in enumerate(products):
            # Determinar método de pago y nota
            pay_method = "efectivo" if i == 0 else "nequi"
            note = "Lo recojo en el bloque L." if i == 0 else "Te transfiero apenas nos veamos."

            # Crear negociación
            neg = Negotiation(
                buyer_id=buyer.id,
                seller_id=seller.id,
                product_id=product.id,
                status="delivered",
                buyer_confirmed=True,
                seller_confirmed=True,
                agreed_price_cop=float(product.price),
                quantity=1,
                payment_method=pay_method,
                buyer_note=note,
                transaction_locked=True
            )
            db.add(neg)
            await db.flush()

            
            # Crear calificación (Rating)
            stars = 5 if i == 0 else 4
            comment = "Excelente vendedor, muy rápido!" if i == 0 else "Buen producto, recomendado."
            
            rating = Rating(
                negotiation_id=neg.id,
                reviewer_id=buyer.id,
                reviewed_id=seller.id,
                stars=stars,
                comment=comment
            )
            db.add(rating)
            print(f"Venta {i+1} registrada y calificada ({stars} estrellas).")

        # 5. Actualizar reputación del vendedor
        await _update_user_reputation(db, seller.id)
        print(f"Reputación de {seller.name} actualizada.")

        await db.commit()
        print("\n✅ Seed completado: 2 ventas entregadas y calificadas para demo@veramarket.co")

if __name__ == "__main__":
    asyncio.run(seed_demo_reputation())
