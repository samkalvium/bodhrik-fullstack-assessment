from pydantic import BaseModel, Field
from app.models.user import UserRole


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    role: UserRole = Field(..., description="User role: 'admin', 'teacher', or 'parent'")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole

    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
