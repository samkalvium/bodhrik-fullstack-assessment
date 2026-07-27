import time
from fastapi import APIRouter, Depends, HTTPException, status
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.core.config import settings
from app.db.session import get_db_session, get_redis
from app.schemas.health import HealthCheckResponse, ServiceStatus

router = APIRouter()


@router.get("", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
async def health_check(
    db: AsyncSession = Depends(get_db_session),
    redis: aioredis.Redis = Depends(get_redis),
) -> HealthCheckResponse:
    """
    Robust health check verifying connectivity to PostgreSQL and Redis.
    Measures latency and returns HTTP 503 if any service is unresponsive.
    """
    # 1. Database check
    database_ok = True
    database_latency = 0.0
    db_start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        database_latency = (time.perf_counter() - db_start) * 1000.0
    except Exception:
        database_ok = False

    # 2. Redis check
    redis_ok = True
    redis_latency = 0.0
    redis_start = time.perf_counter()
    try:
        await redis.ping()
        redis_latency = (time.perf_counter() - redis_start) * 1000.0
    except Exception:
        redis_ok = False

    overall_status = "ok" if (database_ok and redis_ok) else "error"

    response_data = HealthCheckResponse(
        status=overall_status,
        database=ServiceStatus(
            status="ok" if database_ok else "error",
            latency_ms=round(database_latency, 2),
        ),
        redis=ServiceStatus(
            status="ok" if redis_ok else "error",
            latency_ms=round(redis_latency, 2),
        ),
        environment=settings.ENVIRONMENT,
    )

    if overall_status == "error":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_data.model_dump(),
        )

    return response_data
