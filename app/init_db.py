# app/init_db.py
from app.database import engine, Base
from app.models import user, transaction, payment  # Import semua model sebelum create_all()

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

import asyncio
asyncio.run(init())
