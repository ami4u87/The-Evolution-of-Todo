"""Task management API endpoints.

This module implements all REST API endpoints for task CRUD operations
with JWT authentication and user-based data isolation.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.jwt import get_current_user_id
from app.database import get_session
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
)


@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
async def list_tasks(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """
    List all tasks for the authenticated user.

    - **Authentication**: Required (JWT Bearer token)
    - **Returns**: List of tasks owned by the user (empty list if none)

    Example:
        GET /api/tasks
        Authorization: Bearer <token>

        Response: 200 OK
        [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "status": "pending",
                "created_at": "2025-01-08T10:00:00Z",
                "updated_at": "2025-01-08T10:00:00Z"
            }
        ]
    """
    service = TaskService(session)
    tasks = service.list_user_tasks(user_id)
    return tasks


@router.get(
    "/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK
)
async def get_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """
    Get a specific task by ID (if owned by user).

    - **Authentication**: Required (JWT Bearer token)
    - **Path Parameters**: task_id (UUID)
    - **Returns**: Task object
    - **Errors**: 404 if task not found or not owned by user

    Example:
        GET /api/tasks/550e8400-e29b-41d4-a716-446655440000
        Authorization: Bearer <token>

        Response: 200 OK
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "title": "Buy groceries",
            ...
        }
    """
    service = TaskService(session)
    task = service.get_task(user_id, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """
    Create a new task for the authenticated user.

    - **Authentication**: Required (JWT Bearer token)
    - **Request Body**: TaskCreate (title required, description optional)
    - **Returns**: Created task object with generated ID and timestamps
    - **Errors**: 422 if validation fails

    Example:
        POST /api/tasks
        Authorization: Bearer <token>
        Content-Type: application/json

        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }

        Response: 201 Created
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "status": "pending",
            "created_at": "2025-01-08T10:00:00Z",
            "updated_at": "2025-01-08T10:00:00Z"
        }
    """
    service = TaskService(session)
    task = service.create_task(user_id, task_data)
    return task


@router.put(
    "/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK
)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """
    Update an existing task (if owned by user).

    - **Authentication**: Required (JWT Bearer token)
    - **Path Parameters**: task_id (UUID)
    - **Request Body**: TaskUpdate (all fields optional)
    - **Returns**: Updated task object with refreshed updated_at
    - **Errors**: 404 if task not found or not owned by user, 422 if validation fails

    Example:
        PUT /api/tasks/550e8400-e29b-41d4-a716-446655440000
        Authorization: Bearer <token>
        Content-Type: application/json

        {
            "title": "Buy groceries and snacks",
            "description": "Milk, eggs, bread, chips"
        }

        Response: 200 OK
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "title": "Buy groceries and snacks",
            "description": "Milk, eggs, bread, chips",
            "status": "pending",
            "created_at": "2025-01-08T10:00:00Z",
            "updated_at": "2025-01-08T11:30:00Z"
        }
    """
    service = TaskService(session)
    task = service.update_task(user_id, task_id, task_data)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """
    Permanently delete a task (if owned by user).

    - **Authentication**: Required (JWT Bearer token)
    - **Path Parameters**: task_id (UUID)
    - **Returns**: 204 No Content (no response body)
    - **Errors**: 404 if task not found or not owned by user

    Example:
        DELETE /api/tasks/550e8400-e29b-41d4-a716-446655440000
        Authorization: Bearer <token>

        Response: 204 No Content
    """
    service = TaskService(session)
    deleted = service.delete_task(user_id, task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Return None for 204 No Content (FastAPI handles this)
    return None


@router.patch(
    "/{task_id}/complete", response_model=TaskResponse, status_code=status.HTTP_200_OK
)
async def mark_task_complete(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """
    Mark a task as completed (if owned by user).

    This is a shortcut endpoint for updating status to "completed".
    Idempotent: marking an already-completed task is allowed.

    - **Authentication**: Required (JWT Bearer token)
    - **Path Parameters**: task_id (UUID)
    - **Returns**: Updated task object with status="completed"
    - **Errors**: 404 if task not found or not owned by user

    Example:
        PATCH /api/tasks/550e8400-e29b-41d4-a716-446655440000/complete
        Authorization: Bearer <token>

        Response: 200 OK
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "status": "completed",
            "created_at": "2025-01-08T10:00:00Z",
            "updated_at": "2025-01-08T12:00:00Z"
        }
    """
    service = TaskService(session)
    task = service.mark_as_completed(user_id, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task
