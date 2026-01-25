"""Chat API endpoints for AI-powered task management.

This module provides endpoints for conversational task management
using OpenAI's API with function calling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.auth.jwt import get_current_user_id
from app.config import settings
from app.database import get_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """
    Process a chat message and return AI response.

    The AI can manage tasks through natural language commands.
    It has access to tools for listing, creating, updating, and deleting tasks.

    - **Authentication**: Required (JWT Bearer token)
    - **Request Body**: ChatRequest (message required, conversation_id optional)
    - **Returns**: ChatResponse with AI response and actions taken

    Example requests:
        - "Add task: Buy groceries tomorrow"
        - "List my tasks"
        - "Mark the grocery task as complete"
        - "Delete all completed tasks"
        - "What tasks are pending?"

    Example:
        POST /api/chat
        Authorization: Bearer <token>
        Content-Type: application/json

        {
            "message": "Add task: Buy milk",
            "conversation_id": null
        }

        Response: 200 OK
        {
            "response": "I've created a new task 'Buy milk' for you!",
            "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
            "actions_taken": [
                {
                    "tool": "create_task",
                    "arguments": {"title": "Buy milk"},
                    "result": {"success": true, "task": {...}}
                }
            ]
        }
    """
    # Check if any AI provider is configured
    if not settings.openai_api_key and not settings.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI chat service is not configured. Please set GROQ_API_KEY or OPENAI_API_KEY.",
        )

    try:
        chat_service = ChatService(session, user_id)
        response = chat_service.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
        )
        return response

    except Exception as e:
        error_msg = str(e)
        print(f"Chat error for user {user_id}: {error_msg}")

        # Return a user-friendly response instead of 500
        from uuid import uuid4
        return ChatResponse(
            response=f"Sorry, I couldn't process that request. Please try rephrasing. (Error: {error_msg[:100]})",
            conversation_id=request.conversation_id or uuid4(),
            actions_taken=[],
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def chat_health():
    """
    Check if the chat service is available.

    Returns status of the AI chat functionality.
    """
    if settings.groq_api_key:
        return {
            "status": "available",
            "provider": "groq",
            "model": settings.groq_model,
        }
    elif settings.openai_api_key:
        return {
            "status": "available",
            "provider": "openai",
            "model": settings.openai_model,
        }
    else:
        return {
            "status": "unavailable",
            "provider": None,
            "model": None,
        }
