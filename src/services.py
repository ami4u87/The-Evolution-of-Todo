"""
Business logic layer for todo operations.

This module contains service functions that implement business rules and validation.
All functions are pure business logic with NO I/O operations (no input()/print()).
"""

from src.store import TodoStore
from src.models import TodoItem


def create_todo(
    store: TodoStore, title: str, description: str | None = None
) -> TodoItem:
    """
    Create a new todo with validation.

    Args:
        store: The TodoStore instance
        title: Task description (will be validated)
        description: Optional additional details

    Returns:
        TodoItem: The newly created todo

    Raises:
        ValueError: If title is empty after stripping whitespace

    Example:
        >>> store = TodoStore()
        >>> todo = create_todo(store, "Buy groceries", "Milk, eggs")
        >>> todo.id
        1
        >>> todo.status
        'pending'
    """
    if not title.strip():
        raise ValueError("Title cannot be empty")
    return store.add(title=title.strip(), description=description)


def list_todos(store: TodoStore) -> list[TodoItem]:
    """
    Retrieve all todos from the store.

    Args:
        store: The TodoStore instance

    Returns:
        list[TodoItem]: All todos (empty list if none)

    Notes:
        - No pagination in Phase I
        - Todos returned in insertion order
        - No validation needed (delegates directly to store)
    """
    return store.get_all()


def mark_as_completed(store: TodoStore, todo_id: int) -> TodoItem:
    """
    Mark a todo as completed with validation.

    Args:
        store: The TodoStore instance
        todo_id: The ID of the todo to mark complete

    Returns:
        TodoItem: The updated todo with status="completed"

    Raises:
        KeyError: If todo with given ID doesn't exist (from store layer)

    Notes:
        - Idempotent (safe to call on already-completed todos)
        - Services layer passes through KeyError from store
    """
    return store.mark_completed(todo_id)


def update_todo(
    store: TodoStore,
    todo_id: int,
    new_title: str | None = None,
    new_description: str | None = None,
) -> TodoItem:
    """
    Update todo title and/or description with validation.

    Args:
        store: The TodoStore instance
        todo_id: The ID of the todo to update
        new_title: New title (if provided, will be validated; None keeps existing)
        new_description: New description (None keeps existing)

    Returns:
        TodoItem: The updated todo

    Raises:
        KeyError: If todo with given ID doesn't exist
        ValueError: If new_title is provided but empty after stripping

    Example:
        >>> todo = update_todo(store, 1, new_title="Buy groceries and snacks")
        >>> todo.title
        'Buy groceries and snacks'
    """
    if new_title is not None and not new_title.strip():
        raise ValueError("Title cannot be empty")

    # Strip whitespace from title if provided
    if new_title is not None:
        new_title = new_title.strip()

    return store.update(todo_id=todo_id, title=new_title, description=new_description)


def delete_todo(store: TodoStore, todo_id: int) -> None:
    """
    Delete a todo with validation.

    Args:
        store: The TodoStore instance
        todo_id: The ID of the todo to delete

    Raises:
        KeyError: If todo with given ID doesn't exist

    Notes:
        - Permanent deletion (no undo)
        - Services layer passes through KeyError from store
    """
    store.delete(todo_id)
