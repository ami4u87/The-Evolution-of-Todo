"""
Authentication router for signup and login endpoints.

Migrated from Phase I authentication patterns with the following changes:
- Added email/password signup endpoint
- Added email/password login endpoint
- Implemented proper validation and error handling
- Maintained FastAPI router architecture
"""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.schemas.auth import SignupRequest, LoginRequest, AuthResponse
from app.services.auth_service import AuthService

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
    description="Register a new user with email and password. Returns JWT token for immediate login."
)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """
    Create a new user account with email and password.

    Args:
        signup_data: Validated signup request containing email and password
        session: Database session for database operations

    Returns:
        AuthResponse: User data and JWT token for authentication

    Raises:
        HTTPException: 409 if email already exists, 422 if validation fails
    """
    # Create auth service instance
    auth_service = AuthService(session)

    # Perform signup operation
    user, token = auth_service.signup(signup_data)

    # Return authentication response
    return AuthResponse(
        token=token,
        user_id=user.id,
        email=user.email,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user with email and password",
    description="Log in existing user with email and password. Returns JWT token."
)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """
    Authenticate user with email and password.

    Args:
        login_data: Validated login request containing email and password
        session: Database session for database operations

    Returns:
        AuthResponse: User data and JWT token for authentication

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Create auth service instance
    auth_service = AuthService(session)

    # Perform login operation
    user, token = auth_service.login(login_data)

    # Return authentication response
    return AuthResponse(
        token=token,
        user_id=user.id,
        email=user.email,
    )