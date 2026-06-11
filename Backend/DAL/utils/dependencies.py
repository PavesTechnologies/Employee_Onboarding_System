# Backend/DAL/utils/dependencies.py
from typing import AsyncGenerator
from .database import AsyncSessionLocal, AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
