"""Task model for database persistence.

Migrated from Phase I TodoItem with the following changes:
- Changed id from int to UUID for better distributed system support
- Added user_id UUID field for multi-user support
- Added updated_at timestamp for tracking modifications
- Changed to SQLModel for ORM integration
"""

from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """
    Represents a todo task in the database.

    This is the Phase II evolution of the Phase I TodoItem dataclass.
    Now database-backed with PostgreSQL via SQLModel.

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        user_id: Owner of the task (foreign key to users table)
        title: Main task description (required, non-empty, max 255 chars)
        description: Optional additional details about the task
        status: Completion status ("pending" or "completed")
        created_at: Timestamp when the task was created (UTC)
        updated_at: Timestamp when the task was last modified (UTC)

    Example:
        >>> task = Task(
        ...     user_id=UUID("..."),
        ...     title="Buy groceries",
        ...     description="Milk, eggs, bread",
        ...     status="pending"
        ... )
    """

    __tablename__ = "tasks"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to users table (Phase II: multi-user support)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Task fields (from Phase I)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    status: str = Field(default="pending", max_length=50)  # "pending" or "completed"

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def mark_completed(self) -> None:
        """Mark this task as completed and update timestamp."""
        self.status = "completed"
        self.updated_at = datetime.utcnow()

    def update_fields(
        self, title: str | None = None, description: str | None = None
    ) -> None:
        """Update task fields and refresh updated_at timestamp."""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()
