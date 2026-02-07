"""Event models following CloudEvents specification."""

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Task event types."""

    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"


class TaskEventData(BaseModel):
    """Payload for task events."""

    task_id: str
    user_id: str
    title: str | None = None
    description: str | None = None
    status: str | None = None


class TaskEvent(BaseModel):
    """CloudEvents-compatible event envelope for task operations."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType
    source: str = "todo-backend"
    specversion: str = "1.0"
    time: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    datacontenttype: str = "application/json"
    data: TaskEventData

    @classmethod
    def from_task(
        cls,
        event_type: EventType,
        task_id: UUID,
        user_id: UUID,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> "TaskEvent":
        """Create a TaskEvent from task data."""
        return cls(
            type=event_type,
            data=TaskEventData(
                task_id=str(task_id),
                user_id=str(user_id),
                title=title,
                description=description,
                status=status,
            ),
        )
