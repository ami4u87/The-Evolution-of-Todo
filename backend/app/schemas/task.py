"""Pydantic schemas for task request/response validation.

These DTOs define the API contract for task operations.
Separated from database models to allow independent evolution.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

# Task status type (matching model)
TaskStatus = Literal["pending", "completed"]


class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Migrated from Phase I create_todo service logic.
    Validates input before hitting the database.
    """

    title: str = Field(min_length=1, max_length=255, description="Task title")
    description: str | None = Field(None, description="Optional task description")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not empty after stripping whitespace."""
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace only")
        if len(v) > 255:
            raise ValueError("Title must be between 1 and 255 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_length(cls, v: str | None) -> str | None:
        """Validate description length."""
        if v is not None and len(v) > 1000:
            raise ValueError("Description must be less than 1000 characters")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
            }]
        }
    }


class TaskUpdate(BaseModel):
    """
    Request schema for updating an existing task.

    Migrated from Phase I update_todo service logic.
    All fields optional - only provided fields are updated.
    """

    title: str | None = Field(
        None, min_length=1, max_length=255, description="New task title"
    )
    description: str | None = Field(None, description="New task description")
    status: TaskStatus | None = Field(None, description="New task status")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        """Ensure title is not empty if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
            if len(v) > 255:
                raise ValueError("Title must be between 1 and 255 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_length(cls, v: str | None) -> str | None:
        """Validate description length if provided."""
        if v is not None and len(v) > 1000:
            raise ValueError("Description must be less than 1000 characters")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Buy groceries and snacks",
                "description": "Milk, eggs, bread, chips",
            }]
        }
    }


class TaskResponse(BaseModel):
    """
    Response schema for task data.

    Returned by all task endpoints.
    Matches database model structure.
    """

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [{
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "status": "pending",
                "created_at": "2025-01-08T00:00:00Z",
                "updated_at": "2025-01-08T00:00:00Z",
            }]
        }
    }
