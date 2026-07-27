# FastAPI Modular Clean Architecture Backend

This repository provides a modular, clean-architecture boilerplate for a production-grade FastAPI application. It is preconfigured with PostgreSQL (via SQLAlchemy 2.0 and Alembic migrations), Redis (for caching/rate-limiting), Docker, and a comprehensive pytest setup.

---

## Project Structure & File Explanations

Below is the directory structure along with explanations of the files created in this initial setup:

```text
├── app/
│   ├── api/
│   │   ├── __init__.py           # Packaged router endpoints root
│   │   └── v1/
│   │       ├── __init__.py       # Package definition for API v1
│   │       ├── endpoints/
│   │       │   ├── __init__.py   # Controller endpoint package
│   │       │   └── health.py     # Checks connection/latency of Postgres & Redis
│   │       └── router.py         # Registers v1 routes under central router
│   ├── auth/
│   │   └── __init__.py           # Package placeholder for authorization modules
│   ├── core/
│   │   ├── __init__.py           # Core settings root
│   │   └── config.py             # Configures pydantic-settings environment loading
│   ├── db/
│   │   ├── __init__.py           # Database packages root
│   │   ├── base.py               # Aggregates all DB models for Alembic auto-discovery
│   │   └── session.py            # Async engine, sessionmaker, and Redis connection pool
│   ├── middleware/
│   │   └── __init__.py           # Custom middlewares placeholder package
│   ├── models/
│   │   ├── __init__.py           # Database models root package
│   │   └── base.py               # Defines modern SQLAlchemy 2.0 DeclarativeBase
│   ├── schemas/
│   │   ├── __init__.py           # Schemas root package
│   │   └── health.py             # Pydantic v2 schemas for health check structures
│   ├── services/
│   │   └── __init__.py           # Domain services and business logic package
│   ├── utils/
│   │   └── __init__.py           # Helpers and utility functions package
│   └── main.py                   # FastAPI initialization, CORS middleware, & lifespan hook
├── migrations/
│   ├── env.py                    # Alembic migration script configured with async runtime
│   ├── script.py.mako            # Alembic migration creation file template
│   └── versions/                 # Folder holding database migration files
├── tests/
│   ├── __init__.py               # Tests package root
│   ├── conftest.py               # Pytest async fixtures (mock database and redis clients)
│   └── test_health.py            # Test suite validating app readiness/liveness checks
├── .env.example                  # Environment configuration template
├── .gitignore                    # Version control exclusion file
├── alembic.ini                   # Configuration file for database migrations
├── Dockerfile                    # Multi-stage lightweight Docker image build config
├── docker-compose.yml            # Local orchestration setup for Postgres, Redis, and FastAPI
├── requirements.txt              # Production and testing python package dependencies
└── README.md                     # Project overview and instruction guide
```

---

## Configuration & Local Setup

### 1. Environment Settings
Initialize your local configuration by copying `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure you customize the database and cache connection properties if you are not running in Docker.

### 2. Dependency Installation
Create a virtual environment and install the required dependencies:
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

---

## Execution Guide

### Using Docker Compose (Recommended)
Build and run the entire suite (PostgreSQL, Redis, and the FastAPI application) using Docker:
```bash
docker compose up --build
```
The application will launch on `http://localhost:8000`. 
* View OpenAPI docs: `http://localhost:8000/docs`
* Health Check Endpoint: `http://localhost:8000/api/v1/health`

### Local Execution
To run the server locally without Docker (make sure you have a local PostgreSQL and Redis running and configured in `.env`):
```bash
uvicorn app.main:app --reload
```

---

## Testing

Run tests using `pytest`. The testing suite is written using async/await testing fixtures and HTTPX, with database and Redis operations mocked out to allow zero-configuration offline execution:
```bash
pytest
```