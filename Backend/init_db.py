import asyncio
from Backend.DAL.utils.database import engine
from Backend.DAL.models import models


async def init_db():
    async with engine.begin() as conn:
        # Run synchronous create_all inside async connection
        await conn.run_sync(models.Base.metadata.create_all)
    print("✅ Database tables created successfully")


if __name__ == "__main__":
    asyncio.run(init_db())
