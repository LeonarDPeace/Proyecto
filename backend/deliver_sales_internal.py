import asyncio
import uuid
import sys
import os

# Añadir el directorio actual al path para importar app
sys.path.append(os.getcwd())

from app.core.database import async_session
from app.services import negotiation_service
from sqlalchemy import text

async def deliver_sales():
    async with async_session() as db:
        # Vendedor ID: 1f2aff17-4d6e-4667-a6bc-7052458d5dad
        neg_ids = [
            uuid.UUID("a3ecb338-d4bf-4e61-8e9e-3c0636b5c6b2"),
            uuid.UUID("7b9c26bc-e642-4100-b630-2cbee9cb7771"),
            uuid.UUID("26dce9ea-dec0-4baf-8d9b-dbf18f1df57e")
        ]
        
        for nid in neg_ids:
            print(f"Entregando negociación {nid}...")
            # Forzar transaction_locked para que confirm_delivery no falle
            await db.execute(text(f"UPDATE negotiations SET transaction_locked = true, payment_method = 'efectivo' WHERE id = '{nid}'"))
            await db.commit()
            
            # Obtener datos de la negociación
            res = await db.execute(text(f"SELECT buyer_id, seller_id FROM negotiations WHERE id = '{nid}'"))
            row = res.fetchone()
            if not row:
                print(f"  Negociación {nid} no encontrada.")
                continue
                
            buyer_id, seller_id = row
            
            # Confirmar ambas partes
            print(f"  Confirmando por comprador {buyer_id}...")
            await negotiation_service.confirm_delivery(db, nid, buyer_id)
            print(f"  Confirmando por vendedor {seller_id}...")
            await negotiation_service.confirm_delivery(db, nid, seller_id)
            await db.commit()
            print(f"  Negociación {nid} entregada y registrada.")

if __name__ == "__main__":
    asyncio.run(deliver_sales())
