# Backend/DAL/utils/database.py
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextvars import ContextVar
from urllib.parse import quote_plus
from ...config.env_loader import get_env_var

# Database URL construction
DB_USER = get_env_var("DB_USER")
DB_PASSWORD = get_env_var("DB_PASSWORD")
DB_HOST = get_env_var("DB_HOST")
DB_PORT = get_env_var("DB_PORT")
DB_NAME = get_env_var("DB_NAME")
encoded_password = quote_plus(DB_PASSWORD)
DB_DRIVER = get_env_var("DB_DRIVER")

# ✅ Use mysql+asyncmy instead of mysql+mysqlconnector
DB_URL = f"{DB_DRIVER}://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ✅ Create async engine
engine = create_async_engine(
    DB_URL,
    pool_size=15,
    max_overflow=30,
    pool_timeout=15,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False,
)


# ✅ Use async_sessionmaker instead of sessionmaker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# ✅ Context variable for async session
_db_context: ContextVar[Optional[AsyncSession]] = ContextVar("db_session", default=None)


async def set_db_session() -> AsyncSession:
    """Create and set async session in context"""
    db = AsyncSessionLocal()
    _db_context.set(db)
    return db


def get_db_session() -> AsyncSession:
    """Get current async session from context"""
    db = _db_context.get()
    if db is None:
        raise RuntimeError("DB session not found in context")
    return db


async def remove_db_session():
    """Close and remove async session from context"""
    db = _db_context.get()
    if db:
        await db.close()
        _db_context.set(None)


async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session  # ❌ no commit, no rollback
