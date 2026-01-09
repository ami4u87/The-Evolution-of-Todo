"""User model for authentication and task ownership.

New in Phase II - multi-user support.
"""

from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    Represents a user account in the system.

    Users own tasks and authenticate via email/password.
    This model is new in Phase II to support multi-user functionality.

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        email: User's email address (unique, used for login)
        password_hash: Bcrypt hashed password (never store plain text)
        created_at: Account creation timestamp (UTC)

    Example:
        >>> user = User(
        ...     email="user@example.com",
        ...     password_hash="$2b$12$..."
        ... )
    """

    __tablename__ = "users"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Authentication fields
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Note: Relationship to tasks can be added later if needed
    # tasks: list["Task"] = Relationship(back_populates="owner")
