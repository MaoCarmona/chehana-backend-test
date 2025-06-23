"""DTOs para autenticación."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """DTO para solicitud de registro de usuario."""
    
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=100)


class UserLoginRequest(BaseModel):
    """DTO para solicitud de login de usuario."""
    
    username: str
    password: str


class TokenResponse(BaseModel):
    """DTO para respuesta de token."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """DTO para respuesta de usuario."""
    
    id: UUID
    email: EmailStr
    username: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
    } 