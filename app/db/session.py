from typing import AsyncGenerator, Optional
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# --- DATABASE SETUP ---
# Create async database engine with pre-ping validation
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator that yields an active SQLAlchemy AsyncSession.
    Ensures the session is cleanly closed after execution.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# --- REDIS CACHE SETUP ---
# Global Redis client placeholder, instantiated during app lifespan setup
redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    """
    Initializes the Redis client with an async connection pool.
    """
    global redis_client
    redis_client = aioredis.from_url(
        settings.REDIS_URI,
        encoding="utf-8",
        decode_responses=True,
        max_connections=10,
    )


async def close_redis() -> None:
    """
    Closes the Redis client and releases pool connections.
    """
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """
    Dependency generator that yields the initialized Redis client.
    """
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized. Run init_redis() first.")
    yield redis_client
