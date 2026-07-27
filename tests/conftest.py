import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import get_db_session, get_redis


@pytest.fixture
def mock_db() -> MagicMock:
    """
    Fixture that returns a MagicMock representing an AsyncSession.
    Configures async execute command.
    """
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock()
    return db


@pytest.fixture
def mock_redis() -> MagicMock:
    """
    Fixture that returns a MagicMock representing an async Redis client.
    Configures async ping command.
    """
    redis = MagicMock()
    redis.ping = AsyncMock(return_value=True)
    return redis


@pytest.fixture
async def client(mock_db: MagicMock, mock_redis: MagicMock) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP Client fixture.
    Temporarily overrides database and cache dependencies for target tests.
    """
    app.dependency_overrides[get_db_session] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Clean up overrides after test completes
    app.dependency_overrides.clear()
