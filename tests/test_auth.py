from unittest.mock import MagicMock
import pytest
from httpx import AsyncClient

from app.models.user import User, UserRole
from app.utils.security import create_access_token, hash_password

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


async def test_register_user_success(client: AsyncClient, mock_db: MagicMock) -> None:
    """
    Assures user registration successfully inserts user records and returns the serialized model.
    """
    # Mock no existing user
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute.return_value = mock_result

    # Mock refresh to assign database ID
    async def mock_refresh(obj):
        obj.id = 1
    mock_db.refresh = mock_refresh


    payload = {
        "name": "Alice Admin",
        "email": "alice@example.com",
        "password": "strongpassword123",
        "role": "admin"
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Alice Admin"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "admin"
    assert "id" in data
    # Ensure password hash is not exposed
    assert "password" not in data
    assert "password_hash" not in data


async def test_register_user_already_exists(client: AsyncClient, mock_db: MagicMock) -> None:
    """
    Assures register fails with 400 Bad Request when the email is already registered.
    """
    # Mock user exists
    existing_user = User(
        id=1,
        name="Alice Admin",
        email="alice@example.com",
        password_hash="hashedpwd",
        role=UserRole.ADMIN
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = existing_user
    mock_db.execute.return_value = mock_result

    payload = {
        "name": "Alice Admin",
        "email": "alice@example.com",
        "password": "strongpassword123",
        "role": "admin"
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


async def test_login_success(client: AsyncClient, mock_db: MagicMock) -> None:
    """
    Assures user can log in with correct credentials and receive a JWT access token.
    """
    hashed_pwd = hash_password("secretpass")
    registered_user = User(
        id=123,
        name="Bob Teacher",
        email="bob@example.com",
        password_hash=hashed_pwd,
        role=UserRole.TEACHER
    )
    
    # Mock finding user
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = registered_user
    mock_db.execute.return_value = mock_result

    login_payload = {
        "username": "bob@example.com",
        "password": "secretpass"
    }
    
    response = await client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_password(client: AsyncClient, mock_db: MagicMock) -> None:
    """
    Assures login fails with 400 Bad Request if the password is correct/incorrect.
    """
    hashed_pwd = hash_password("secretpass")
    registered_user = User(
        id=123,
        name="Bob Teacher",
        email="bob@example.com",
        password_hash=hashed_pwd,
        role=UserRole.TEACHER
    )
    
    # Mock finding user
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = registered_user
    mock_db.execute.return_value = mock_result

    login_payload = {
        "username": "bob@example.com",
        "password": "wrongpassword"
    }
    
    response = await client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 400
    assert "Incorrect email" in response.json()["detail"]


async def test_get_me_unauthorized(client: AsyncClient) -> None:
    """
    Assures that accessing protected routes without a token yields 401 Unauthorized.
    """
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_get_me_success(client: AsyncClient, mock_db: MagicMock) -> None:
    """
    Assures that accessing protected routes with a valid token returns current user context.
    """
    registered_user = User(
        id=456,
        name="Cathy Parent",
        email="cathy@example.com",
        password_hash="hashedpwd",
        role=UserRole.PARENT
    )
    
    # Mock user retrieval inside dependency
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = registered_user
    mock_db.execute.return_value = mock_result

    # Generate token for Cathy
    token = create_access_token(subject=456)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == 456
    assert data["name"] == "Cathy Parent"
    assert data["email"] == "cathy@example.com"
    assert data["role"] == "parent"
