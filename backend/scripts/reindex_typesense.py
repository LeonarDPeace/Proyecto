import asyncio
import sys
from sqlalchemy import select
from app.core.database import async_session
from app.models.product import Product
from app.services.typesense_service import upsert_product_document

async def reindex_all():
    print("--- INICIANDO RE-INDEXACIÓN DE TYPESENSE ---")
    async with async_session() as db:
        # 1. Obtener todos los productos activos
        result = await db.execute(select(Product))
        products = result.scalars().all()
        
        print(f"Se encontraron {len(products)} productos en la base de datos.")
        
        # 2. Sincronizar uno por uno
        count = 0
        for p in products:
            try:
                await upsert_product_document(db, p)
                count += 1
                print(f"[{count}/{len(products)}] Indexado: {p.name}")
            except Exception as e:
                print(f"Error indexando {p.name}: {str(e)}")
        
        print(f"\n--- PROCESO FINALIZADO ---")
        print(f"Total exitosos: {count}")

if __name__ == "__main__":
    asyncio.run(reindex_all())
