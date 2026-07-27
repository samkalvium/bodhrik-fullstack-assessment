from unittest.mock import MagicMock
import pytest
from httpx import AsyncClient

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


async def test_health_check_success(
    client: AsyncClient, 
    mock_db: MagicMock, 
    mock_redis: MagicMock
) -> None:
    """
    Assures /health returns 200 OK and status 'ok' when both Postgres and Redis are online.
    """
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"]["status"] == "ok"
    assert data["redis"]["status"] == "ok"
    assert "latency_ms" in data["database"]
    assert "latency_ms" in data["redis"]
    assert "environment" in data


async def test_health_check_db_failure(
    client: AsyncClient, 
    mock_db: MagicMock, 
    mock_redis: MagicMock
) -> None:
    """
    Assures /health returns 503 Service Unavailable when the database check encounters an error.
    """
    # Force mock database execution to fail
    mock_db.execute.side_effect = Exception("DB Connection Timeout")
    
    response = await client.get("/api/v1/health")
    assert response.status_code == 503
    
    # FastAPI HTTPException payload is embedded in "detail"
    data = response.json()["detail"]
    assert data["status"] == "error"
    assert data["database"]["status"] == "error"
    assert data["redis"]["status"] == "ok"


async def test_health_check_redis_failure(
    client: AsyncClient, 
    mock_db: MagicMock, 
    mock_redis: MagicMock
) -> None:
    """
    Assures /health returns 503 Service Unavailable when the Redis check encounters an error.
    """
    # Force mock Redis ping to fail
    mock_redis.ping.side_effect = Exception("Redis Connection Timeout")
    
    response = await client.get("/api/v1/health")
    assert response.status_code == 503
    
    data = response.json()["detail"]
    assert data["status"] == "error"
    assert data["database"]["status"] == "ok"
    assert data["redis"]["status"] == "error"
