"""JWT token verification for authentication.

This module provides utilities to verify JWT tokens issued by Better Auth
on the frontend and extract user identity.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings

# HTTP Bearer security scheme
security = HTTPBearer()


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token signature and return payload.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload containing user claims

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        # Decode and verify token signature
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency to extract and verify user_id from JWT token.

    This dependency should be used on all protected endpoints to:
    1. Verify the JWT token signature
    2. Extract the user_id from the token payload
    3. Return the user_id for use in the endpoint

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        str: User ID (UUID as string) extracted from token

    Raises:
        HTTPException: 401 if token is missing, invalid, or doesn't contain user_id

    Example:
        @router.get("/api/tasks")
        async def list_tasks(user_id: str = Depends(get_current_user_id)):
            # user_id is now authenticated and available
            tasks = get_user_tasks(user_id)
            return tasks
    """
    # Extract token from credentials
    token = credentials.credentials

    # Verify token and get payload
    payload = verify_jwt_token(token)

    # Extract user_id from 'sub' claim (standard JWT claim for subject/user)
    user_id: str | None = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain user identification",
        )

    return user_id
