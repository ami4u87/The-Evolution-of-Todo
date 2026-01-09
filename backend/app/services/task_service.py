"""Task service layer - business logic for task operations.

Migrated from Phase I src/services.py with the following changes:
- Changed from standalone functions to TaskService class
- Added user_id parameter to all operations for multi-user support
- Integrated with SQLModel database instead of in-memory TodoStore
- Maintained same validation logic and business rules
"""

from uuid import UUID
from sqlmodel import Session, select
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """
    Service layer for task operations.

    This is the Phase II evolution of Phase I services module.
    Encapsulates business logic and coordinates between API and database.
    """

    def __init__(self, session: Session):
        """
        Initialize service with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create_task(self, user_id: str, data: TaskCreate) -> Task:
        """
        Create a new task with validation.

        Migrated from Phase I create_todo() function.

        Args:
            user_id: UUID of the authenticated user (owner)
            data: Validated task creation data

        Returns:
            Task: The newly created task

        Raises:
            ValueError: If title is empty (validation should happen in schema)

        Example:
            >>> service = TaskService(session)
            >>> task_data = TaskCreate(title="Buy groceries", description="Milk, eggs")
            >>> task = service.create_task(user_id="...", data=task_data)
        """
        # Title validation (already done by Pydantic, but defense in depth)
        if not data.title.strip():
            raise ValueError("Title cannot be empty")

        # Create task instance
        task = Task(
            user_id=UUID(user_id),
            title=data.title.strip(),
            description=data.description,
            status="pending",
        )

        # Persist to database
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def list_user_tasks(self, user_id: str) -> list[Task]:
        """
        Retrieve all tasks for a specific user.

        Migrated from Phase I list_todos() function with user filtering.

        Args:
            user_id: UUID of the authenticated user

        Returns:
            list[Task]: All tasks owned by the user (empty list if none)

        Notes:
            - CRITICAL: Always filters by user_id for data isolation
            - Returns tasks in creation order (can add sorting later)
        """
        statement = select(Task).where(Task.user_id == UUID(user_id))
        tasks = self.session.exec(statement).all()
        return list(tasks)

    def get_task(self, user_id: str, task_id: UUID) -> Task | None:
        """
        Retrieve a specific task if owned by the user.

        Phase II addition - needed for individual task operations.

        Args:
            user_id: UUID of the authenticated user
            task_id: UUID of the task to retrieve

        Returns:
            Task | None: The task if found and owned by user, None otherwise

        Notes:
            - CRITICAL: Filters by both task_id AND user_id
            - Returns None instead of raising exception (let caller decide)
        """
        statement = select(Task).where(
            Task.id == task_id, Task.user_id == UUID(user_id)
        )
        task = self.session.exec(statement).first()
        return task

    def mark_as_completed(self, user_id: str, task_id: UUID) -> Task | None:
        """
        Mark a task as completed with validation.

        Migrated from Phase I mark_as_completed() function with user filtering.

        Args:
            user_id: UUID of the authenticated user
            task_id: UUID of the task to mark complete

        Returns:
            Task | None: The updated task, or None if not found/not owned

        Notes:
            - Idempotent (safe to call on already-completed tasks)
            - Updates updated_at timestamp
            - Returns None if task not found or not owned by user
        """
        task = self.get_task(user_id, task_id)
        if task is None:
            return None

        task.mark_completed()
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def update_task(
        self, user_id: str, task_id: UUID, data: TaskUpdate
    ) -> Task | None:
        """
        Update task fields with validation.

        Migrated from Phase I update_todo() function with user filtering.

        Args:
            user_id: UUID of the authenticated user
            task_id: UUID of the task to update
            data: Validated update data (only provided fields updated)

        Returns:
            Task | None: The updated task, or None if not found/not owned

        Raises:
            ValueError: If title provided but empty after stripping

        Notes:
            - Only updates fields that are not None in data
            - Updates updated_at timestamp
            - Returns None if task not found or not owned by user
        """
        task = self.get_task(user_id, task_id)
        if task is None:
            return None

        # Validate title if provided
        if data.title is not None and not data.title.strip():
            raise ValueError("Title cannot be empty")

        # Update fields (only if provided)
        if data.title is not None:
            task.title = data.title.strip()
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status

        # Update timestamp
        task.update_fields()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def delete_task(self, user_id: str, task_id: UUID) -> bool:
        """
        Delete a task if owned by the user.

        Migrated from Phase I delete_todo() function with user filtering.

        Args:
            user_id: UUID of the authenticated user
            task_id: UUID of the task to delete

        Returns:
            bool: True if deleted, False if not found or not owned

        Notes:
            - Permanent deletion (no soft delete in Phase II)
            - Returns False instead of raising exception
        """
        task = self.get_task(user_id, task_id)
        if task is None:
            return False

        self.session.delete(task)
        self.session.commit()

        return True
