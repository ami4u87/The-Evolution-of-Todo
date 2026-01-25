"""Pydantic schemas for chat request/response validation."""

from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(description="Message role: user or assistant")
    content: str = Field(description="Message content")


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(min_length=1, max_length=2000, description="User message")
    conversation_id: UUID | None = Field(None, description="Optional conversation ID for context")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "message": "Add task: Buy groceries tomorrow",
                "conversation_id": None,
            }]
        }
    }


class ToolAction(BaseModel):
    """Record of a tool action taken by the AI."""
    tool: str = Field(description="Tool name that was called")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments passed to the tool")
    result: Any = Field(default=None, description="Result from the tool")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    response: str = Field(description="AI assistant response")
    conversation_id: UUID = Field(description="Conversation ID for follow-up messages")
    actions_taken: list[ToolAction] = Field(default_factory=list, description="Tools called during processing")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "response": "I've created a new task 'Buy groceries' for you.",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "actions_taken": [
                    {
                        "tool": "create_task",
                        "arguments": {"title": "Buy groceries"},
                        "result": {"id": "...", "title": "Buy groceries"}
                    }
                ]
            }]
        }
    }
