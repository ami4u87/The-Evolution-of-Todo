"""
Authentication service layer - business logic for signup/login operations.

Migrated from Phase I authentication patterns with the following changes:
- Added email/password signup functionality
- Implemented password hashing with bcrypt
- Added duplicate email checking
- Maintained service layer architecture
"""

from sqlmodel import Session, select
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_jwt_token


class AuthService:
    """
    Service layer for authentication operations.

    Handles user signup and login with proper validation and security.
    """

    def __init__(self, session: Session):
        """
        Initialize service with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def signup(self, data: SignupRequest) -> tuple[User, str]:
        """
        Create a new user account with email/password.

        Args:
            data: Validated signup request data

        Returns:
            tuple[User, str]: Created user and JWT token

        Raises:
            HTTPException: If email already exists (409 Conflict) or passwords don't match
        """
        # Check if passwords match
        if data.password != data.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passwords do not match"
            )

        # Check if email already exists
        existing_user = self.session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Hash the password
        password_hash = hash_password(data.password)

        # Create user instance
        user = User(
            email=data.email,
            password_hash=password_hash
        )

        # Persist to database
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        # Generate JWT token
        token = create_jwt_token(user.id)

        return user, token

    def login(self, data: LoginRequest) -> tuple[User, str]:
        """
        Authenticate user with email/password.

        Args:
            data: Validated login request data

        Returns:
            tuple[User, str]: Authenticated user and JWT token

        Raises:
            HTTPException: If credentials are invalid (401 Unauthorized)
        """
        # Find user by email
        user = self.session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Generate JWT token
        token = create_jwt_token(user.id)

        return user, token