"""FastAPI dependencies for dependency injection.

This module organizes common dependencies used across routers.
"""

from fastapi import Depends
from sqlmodel import Session

from app.auth.jwt import get_current_user_id
from app.database import get_session

# Re-export for convenient importing
__all__ = ["get_session", "get_current_user_id"]


# Example of combined dependency (if needed in future)
async def get_current_user_with_session(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> tuple[str, Session]:
    """
    Combined dependency that provides both authenticated user_id and database session.

    Returns:
        tuple: (user_id, session)

    Example:
        @router.get("/api/tasks")
        async def list_tasks(
            user_session: tuple[str, Session] = Depends(get_current_user_with_session)
        ):
            user_id, session = user_session
            # Use user_id and session
    """
    return user_id, session
