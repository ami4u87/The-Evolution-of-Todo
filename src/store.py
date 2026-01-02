"""
In-memory storage for todo items.

This module provides the TodoStore class which manages the collection of todos
using Python lists and dicts. All operations are in-memory only.
"""

from datetime import datetime
from src.models import TodoItem


class TodoStore:
    """
    Manages in-memory collection of todo items.

    Provides CRUD operations with auto-incrementing ID generation.
    Thread-safety not required (single-threaded console application).

    Attributes:
        _todos: Internal list storing all todo items
        _next_id: Counter for auto-incrementing IDs (starts at 1)
    """

    def __init__(self) -> None:
        """
        Initialize empty todo store with ID counter starting at 1.
        """
        self._todos: list[TodoItem] = []
        self._next_id: int = 1

    def add(self, title: str, description: str | None = None) -> TodoItem:
        """
        Add a new todo item to the store.

        Args:
            title: Task description (validation happens in services layer)
            description: Optional additional details

        Returns:
            TodoItem: The newly created todo with auto-generated ID and timestamp

        Notes:
            - ID auto-incremented (monotonic, never reused)
            - Status defaults to "pending"
            - created_at set to current local time
        """
        todo = TodoItem(
            id=self._next_id,
            title=title,
            description=description,
            status="pending",
            created_at=datetime.now(),
        )
        self._todos.append(todo)
        self._next_id += 1
        return todo

    def get_all(self) -> list[TodoItem]:
        """
        Retrieve all todo items.

        Returns:
            list[TodoItem]: All todos in insertion order (empty list if none)
        """
        return self._todos.copy()

    def get_by_id(self, todo_id: int) -> TodoItem:
        """
        Retrieve a specific todo by ID.

        Args:
            todo_id: The unique identifier of the todo

        Returns:
            TodoItem: The matching todo

        Raises:
            KeyError: If no todo with the given ID exists
        """
        for todo in self._todos:
            if todo.id == todo_id:
                return todo
        raise KeyError(f"Todo #{todo_id} not found")

    def update(
        self, todo_id: int, title: str | None = None, description: str | None = None
    ) -> TodoItem:
        """
        Update title and/or description of an existing todo.

        Args:
            todo_id: The unique identifier of the todo to update
            title: New title (if None, keeps existing title)
            description: New description (if None, keeps existing description)

        Returns:
            TodoItem: The updated todo

        Raises:
            KeyError: If no todo with the given ID exists

        Notes:
            - ID and created_at cannot be modified
            - Status unchanged (use mark_completed for status changes)
            - Passing None means "keep existing value"
        """
        todo = self.get_by_id(todo_id)  # Raises KeyError if not found
        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        return todo

    def mark_completed(self, todo_id: int) -> TodoItem:
        """
        Mark a todo as completed (change status to "completed").

        Args:
            todo_id: The unique identifier of the todo

        Returns:
            TodoItem: The updated todo with status="completed"

        Raises:
            KeyError: If no todo with the given ID exists

        Notes:
            - Idempotent (marking already-completed todo is allowed)
            - One-way transition (no "uncomplete" in Phase I)
        """
        todo = self.get_by_id(todo_id)  # Raises KeyError if not found
        todo.status = "completed"
        return todo

    def delete(self, todo_id: int) -> None:
        """
        Permanently remove a todo from the store.

        Args:
            todo_id: The unique identifier of the todo to delete

        Raises:
            KeyError: If no todo with the given ID exists

        Notes:
            - Deleted IDs are never reused
            - Operation is permanent (no undo in Phase I)
        """
        todo = self.get_by_id(todo_id)  # Raises KeyError if not found
        self._todos.remove(todo)
