"""User Schemas - Request/Response Models"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserCreate(BaseModel):
    """User signup request."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        description="Password (min 8 characters)"
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="User's full name"
    )


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User's email")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """User response (public data only)."""

    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response after auth."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=900, description="Seconds until expiry")


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(..., description="Valid refresh token")


class AuthResponse(BaseModel):
    """Complete auth response (user + tokens)."""

    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
