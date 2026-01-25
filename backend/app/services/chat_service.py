"""Chat service for AI-powered task management.

This service integrates with AI providers (OpenAI or Groq) using function calling
to enable natural language task management.
"""

import json
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import Session

from app.config import settings
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.chat import ChatResponse, ToolAction
from app.services.task_service import TaskService


def get_ai_client():
    """Get the appropriate AI client based on configuration."""
    if settings.ai_provider == "groq" and settings.groq_api_key:
        from groq import Groq
        return Groq(api_key=settings.groq_api_key), settings.groq_model
    elif settings.ai_provider == "openai" and settings.openai_api_key:
        from openai import OpenAI
        return OpenAI(api_key=settings.openai_api_key), settings.openai_model
    elif settings.groq_api_key:
        # Fallback to Groq if available
        from groq import Groq
        return Groq(api_key=settings.groq_api_key), settings.groq_model
    elif settings.openai_api_key:
        # Fallback to OpenAI if available
        from openai import OpenAI
        return OpenAI(api_key=settings.openai_api_key), settings.openai_model
    else:
        return None, None


# Define the tools available to the AI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the current user. Returns tasks with their titles, descriptions, and statuses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status. Default is 'all'."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task (required, max 255 chars)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the task"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task. Use search_tasks first to find the task ID if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "description": "New status for the task"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task permanently. Use search_tasks first to find the task ID if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_complete",
            "description": "Mark a task as completed. Use search_tasks first to find the task ID if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to mark as completed"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search for tasks by title or description. Use this to find task IDs before updating or deleting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to match against task titles and descriptions"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a task management assistant. Help users manage their todo tasks.

IMPORTANT RULES:
- Use ONLY the provided tool functions. Do NOT write function calls as text.
- NEVER create a task unless the user explicitly says "add", "create", or "new task".
- For creating tasks: call create_task with the title extracted from the user's message.
- For listing tasks: call list_tasks.
- For completing tasks: first call list_tasks to find the task ID, then call mark_complete with that ID.
- For uncompleting/unchecking tasks: first call list_tasks to find the task ID, then call update_task with status="pending".
- For deleting tasks: first call list_tasks to find the task ID, then call delete_task with that ID.
- For updating tasks: first call list_tasks to find the task ID, then call update_task with that ID.
- Always use list_tasks instead of search_tasks when you need to find a task ID.
- After performing an action, respond with a short confirmation message.
- Format task lists clearly with status indicators.
- If no tasks exist, say so clearly.

Understanding user intent:
- "uncheck", "undo", "mark as not done", "mark as pending", "uncomplete" → update_task(status="pending")
- "check", "done", "complete", "mark as done", "finish" → mark_complete
- "add", "create", "new task" → create_task
- "remove", "delete" → delete_task
- "list", "show", "what are my tasks" → list_tasks
- "rename", "change title", "update" → update_task

Examples:
- "Add task: Buy milk" → create_task(title="Buy milk")
- "List my tasks" → list_tasks()
- "Complete the milk task" → list_tasks(), then mark_complete(task_id=...)
- "Uncheck walk the dog" → list_tasks(), then update_task(task_id=..., status="pending")
- "Delete grocery task" → list_tasks(), then delete_task(task_id=...)
- "Rename milk task to Buy groceries" → list_tasks(), then update_task(task_id=..., title="Buy groceries")"""


class ChatService:
    """Service for processing chat messages with AI."""

    def __init__(self, session: Session, user_id: str):
        self.session = session
        self.user_id = user_id
        self.task_service = TaskService(session)
        self.client, self.model = get_ai_client()
        self.actions_taken: list[ToolAction] = []

    def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any] | str:
        """Execute a tool and return the result."""
        try:
            if tool_name == "list_tasks":
                status_filter = arguments.get("status_filter", "all")
                tasks = self.task_service.list_user_tasks(self.user_id)

                if status_filter != "all":
                    tasks = [t for t in tasks if t.status == status_filter]

                return {
                    "tasks": [
                        {
                            "id": str(t.id),
                            "title": t.title,
                            "description": t.description,
                            "status": t.status,
                            "created_at": t.created_at.isoformat() if t.created_at else None,
                        }
                        for t in tasks
                    ],
                    "count": len(tasks)
                }

            elif tool_name == "create_task":
                task_data = TaskCreate(
                    title=arguments["title"],
                    description=arguments.get("description")
                )
                task = self.task_service.create_task(self.user_id, task_data)
                return {
                    "success": True,
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                    }
                }

            elif tool_name == "update_task":
                task_id = UUID(arguments["task_id"])
                task_data = TaskUpdate(
                    title=arguments.get("title"),
                    description=arguments.get("description"),
                    status=arguments.get("status")
                )
                task = self.task_service.update_task(self.user_id, task_id, task_data)
                if task is None:
                    return {"success": False, "error": "Task not found"}
                return {
                    "success": True,
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                    }
                }

            elif tool_name == "delete_task":
                task_id = UUID(arguments["task_id"])
                deleted = self.task_service.delete_task(self.user_id, task_id)
                return {
                    "success": deleted,
                    "message": "Task deleted" if deleted else "Task not found"
                }

            elif tool_name == "mark_complete":
                task_id = UUID(arguments["task_id"])
                task = self.task_service.mark_as_completed(self.user_id, task_id)
                if task is None:
                    return {"success": False, "error": "Task not found"}
                return {
                    "success": True,
                    "task": {
                        "id": str(task.id),
                        "title": task.title,
                        "status": task.status,
                    }
                }

            elif tool_name == "search_tasks":
                query = arguments["query"].lower()
                tasks = self.task_service.list_user_tasks(self.user_id)
                matching = [
                    t for t in tasks
                    if query in t.title.lower() or (t.description and query in t.description.lower())
                ]
                return {
                    "tasks": [
                        {
                            "id": str(t.id),
                            "title": t.title,
                            "description": t.description,
                            "status": t.status,
                        }
                        for t in matching
                    ],
                    "count": len(matching)
                }

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    def process_message(
        self,
        message: str,
        conversation_id: UUID | None = None
    ) -> ChatResponse:
        """Process a user message and return AI response."""
        # Check if AI client is available
        if self.client is None:
            raise ValueError("No AI provider configured. Set GROQ_API_KEY or OPENAI_API_KEY.")

        # Generate conversation ID if not provided
        if conversation_id is None:
            conversation_id = uuid4()

        self.actions_taken = []

        # Initial messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

        max_retries = 2
        max_tool_rounds = 5

        for attempt in range(max_retries):
            try:
                # Call AI API (works with both OpenAI and Groq)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    max_tokens=1000,
                )

                # Process the response
                assistant_message = response.choices[0].message

                # Handle tool calls if any
                tool_rounds = 0
                while assistant_message.tool_calls and tool_rounds < max_tool_rounds:
                    tool_rounds += 1

                    # Add assistant message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })

                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                        except (json.JSONDecodeError, TypeError):
                            arguments = {}

                        if not isinstance(arguments, dict):
                            arguments = {}

                        # Execute the tool
                        result = self._execute_tool(tool_name, arguments)

                        # Record the action
                        self.actions_taken.append(ToolAction(
                            tool=tool_name,
                            arguments=arguments,
                            result=result
                        ))

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })

                    # Get next response from AI
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=TOOLS,
                        tool_choice="auto",
                        max_tokens=1000,
                    )

                    assistant_message = response.choices[0].message

                # Return final response
                return ChatResponse(
                    response=assistant_message.content or "Done! Your request has been processed.",
                    conversation_id=conversation_id,
                    actions_taken=self.actions_taken
                )

            except Exception as e:
                error_msg = str(e)
                # Retry on tool_use_failed errors (common with Groq/Llama)
                if "tool_use_failed" in error_msg and attempt < max_retries - 1:
                    # Reset and retry with a more explicit prompt
                    self.actions_taken = []
                    messages = [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Please use the tool functions to help with this request: {message}"}
                    ]
                    continue
                raise

        # Fallback if all retries fail
        return ChatResponse(
            response="I had trouble processing your request. Please try rephrasing it.",
            conversation_id=conversation_id,
            actions_taken=self.actions_taken
        )
