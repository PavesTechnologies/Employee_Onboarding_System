import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from  DAL.models.models import Base   


async def create_all_tables():
    DB_HOST = "paves-intranet-demo.czsgackimf7p.ap-south-1.rds.amazonaws.com"
    DB_PORT = "3306"
    DB_USER = "admin_paves"
    DB_NAME = "eos"
    DB_PASSWORD = "PavesAdmin"

    DATABASE_URL = (
        f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("All tables created successfully.")

    finally:
        # Ensure all connections are closed before the event loop shuts down.
        await engine.dispose()
    
if __name__ == "__main__":
    asyncio.run(create_all_tables())