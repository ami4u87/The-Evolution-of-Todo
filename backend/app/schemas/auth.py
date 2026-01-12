"""
Authentication request/response schemas.

Migrated from Phase I validation patterns with the following changes:
- Added email/password signup validation
- Implemented password strength requirements
- Added password confirmation field
- Maintained Pydantic v2 compatibility
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from typing import Annotated
import re


class SignupRequest(BaseModel):
    """
    Request schema for user signup.

    Validates email format and password strength. Password confirmation
    validation is handled in the service layer.
    """
    email: EmailStr = Field(description="User's email address")
    password: str = Field(
        min_length=8,
        max_length=100,
        description="User password (minimum 8 characters)"
    )
    password_confirm: str = Field(description="Password confirmation")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength requirements.

        Requirements:
        - At least 8 characters
        - Contains uppercase letter (A-Z)
        - Contains lowercase letter (a-z)
        - Contains digit (0-9)
        - Contains special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&* etc.)')

        return v


class LoginRequest(BaseModel):
    """
    Request schema for user login.
    """
    email: EmailStr = Field(description="User's email address")
    password: str = Field(
        min_length=1,
        max_length=100,
        description="User password"
    )


class AuthResponse(BaseModel):
    """
    Response schema for authentication endpoints.
    """
    token: str = Field(description="JWT authentication token")
    user_id: UUID = Field(description="User's unique identifier")
    email: str = Field(description="User's email address")