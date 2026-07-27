from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    status: str = Field(..., description="Status of the sub-service (e.g., 'ok' or 'error')")
    latency_ms: float = Field(..., description="Response latency in milliseconds")


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Overall health status of the application ('ok' or 'error')")
    database: ServiceStatus = Field(..., description="Database connection health info")
    redis: ServiceStatus = Field(..., description="Redis connection health info")
    environment: str = Field(..., description="Current environment mode (e.g., 'development', 'production')")
