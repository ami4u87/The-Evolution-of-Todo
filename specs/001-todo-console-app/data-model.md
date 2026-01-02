# Data Model: In-Memory Todo Console Application

**Feature**: 001-todo-console-app
**Created**: 2026-01-02
**Source**: Derived from [spec.md](spec.md) functional requirements

## Overview

This document defines the data structures for the In-Memory Todo Console Application. All entities are designed with future database migration in mind (Phase II), following constitution principle V (Extensibility for Future Phases).

## Entities

### TodoItem

**Purpose**: Represents a single task in the user's todo list.

**Type**: Python `@dataclass` (from `dataclasses` module)

**Fields**:

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `id` | `int` | Yes | Auto-generated | Unique, positive integer starting from 1 | Unique identifier for the todo item |
| `title` | `str` | Yes | N/A | Non-empty after `.strip()` | Main task description |
| `description` | `str \| None` | No | `None` | Can be empty string or None | Optional additional details about the task |
| `status` | `str` | Yes | `"pending"` | Must be `"pending"` or `"completed"` | Current completion status of the task |
| `created_at` | `datetime` | Yes | Auto-generated | No future dates | Timestamp when the todo was created (local time) |

**Validation Rules**:
- `title`: Must be non-empty after whitespace stripping (validated in services layer, not in dataclass)
- `id`: Generated automatically by `TodoStore`; never set manually by users
- `status`: Enforced via validation in services; uses string literals for simplicity (no enum in Phase I)
- `created_at`: Set automatically to `datetime.now()` when todo is created

**Immutability**: Not enforced (`frozen=False`) to allow updates to `title`, `description`, and `status` fields.

**Example Instance**:
```python
TodoItem(
    id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    status="pending",
    created_at=datetime(2026, 1, 2, 10, 30, 15)
)
```

**Migration Path (Phase II)**:
```python
# Phase I: Dataclass
@dataclass
class TodoItem:
    id: int
    title: str
    description: str | None
    status: str
    created_at: datetime

# Phase II: SQLAlchemy Model
from sqlalchemy.orm import Mapped, mapped_column

class TodoItem(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20))  # Or Enum
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
```

---

### TodoStore

**Purpose**: Manages the in-memory collection of `TodoItem` objects and provides CRUD operations.

**Type**: Python class (not a dataclass; has mutable state and methods)

**State (Private Fields)**:

| Field | Type | Description |
|-------|------|-------------|
| `_todos` | `list[TodoItem]` | Internal list storing all todo items (private) |
| `_next_id` | `int` | Counter for auto-incrementing IDs (starts at 1) |

**Methods**: See [contracts/services.md](contracts/services.md) for complete signatures.

**Key Behaviors**:
- **ID Generation**: Auto-increments `_next_id` for each new todo (monotonic, never reused)
- **Storage**: Uses a simple Python list (linear search acceptable for Phase I scale)
- **Error Handling**: Raises `KeyError` for non-existent IDs, `ValueError` for validation failures
- **State Isolation**: All state changes go through methods (no direct access to `_todos` or `_next_id`)

**Invariants**:
1. `_next_id` always equals `max(todo.id for todo in _todos) + 1` (or 1 if empty)
2. All `TodoItem.id` values in `_todos` are unique
3. IDs are never reused (even after deletion)

**Example Usage**:
```python
store = TodoStore()

# Add a new todo
todo1 = store.add(title="Buy groceries", description="Milk, eggs, bread")
# todo1.id == 1, status == "pending", created_at == now()

# Get all todos
all_todos = store.get_all()  # Returns list[TodoItem]

# Get specific todo
todo = store.get_by_id(1)  # Returns TodoItem or raises KeyError

# Update todo
store.update(todo_id=1, title="Buy groceries and snacks", description="Updated")

# Mark completed
store.mark_completed(todo_id=1)  # Changes status to "completed"

# Delete todo
store.delete(todo_id=1)  # Removes from list, ID 1 never reused
```

**Migration Path (Phase II)**:
```python
# Phase I: TodoStore class with list
class TodoStore:
    def __init__(self):
        self._todos: list[TodoItem] = []
        self._next_id = 1

    def add(self, title: str, description: str | None = None) -> TodoItem:
        todo = TodoItem(id=self._next_id, title=title, ...)
        self._todos.append(todo)
        self._next_id += 1
        return todo

# Phase II: Repository pattern with SQLAlchemy
class TodoRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, title: str, description: str | None = None) -> TodoItem:
        todo = TodoItem(title=title, description=description, ...)
        self.session.add(todo)
        self.session.commit()  # ID auto-generated by DB
        return todo
```

---

## Data Flow

### Create Todo Flow
1. **User Input** (CLI layer): User enters title and optional description
2. **Validation** (Services layer): Validate title is non-empty
3. **Storage** (Store layer): `TodoStore.add()` creates `TodoItem` with auto-generated ID and timestamp
4. **Return** → Services → CLI: Display success message with new todo ID

### List Todos Flow
1. **Request** (CLI layer): User selects "List Todos"
2. **Retrieval** (Services layer): Call `TodoStore.get_all()`
3. **Storage** (Store layer): Return copy of `_todos` list
4. **Display** (CLI layer): Format and print each `TodoItem`

### Mark Completed Flow
1. **User Input** (CLI layer): User enters todo ID
2. **Validation** (Services layer): Validate ID exists
3. **State Change** (Store layer): `TodoStore.mark_completed(id)` updates `status` to "completed"
4. **Return** → Services → CLI: Display success message

### Update Todo Flow
1. **User Input** (CLI layer): User enters ID and new title/description
2. **Validation** (Services layer): Validate ID exists and new title is non-empty (if provided)
3. **State Change** (Store layer): `TodoStore.update(id, title, description)` modifies fields
4. **Return** → Services → CLI: Display success message

### Delete Todo Flow
1. **User Input** (CLI layer): User enters todo ID
2. **Validation** (Services layer): Validate ID exists
3. **Removal** (Store layer): `TodoStore.delete(id)` removes from `_todos` list
4. **Return** → Services → CLI: Display success message

---

## Constraints & Assumptions

**Phase I Constraints**:
- No persistence (all data lost on application exit)
- No concurrent access (single-threaded, single-user)
- No pagination (all todos returned in single list)
- No sorting or filtering (todos displayed in insertion order)

**Assumptions**:
- Typical usage: dozens of todos per session (scale: 10-100 items)
- Maximum theoretical capacity: 1000+ todos (Python list performance acceptable)
- ID overflow: Not a concern (Python int is unbounded; practical session length limits)

**Future Phase Considerations**:
- Phase II will add database persistence (SQLAlchemy models)
- Phase II may add pagination for large todo lists
- Phase III may add AI-generated todo suggestions (new fields possible)

---

## Type Definitions (Python)

**Literal Types** (for improved type safety in implementation):

```python
from typing import Literal

TodoStatus = Literal["pending", "completed"]
```

**Usage in TodoItem**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

TodoStatus = Literal["pending", "completed"]

@dataclass
class TodoItem:
    id: int
    title: str
    description: str | None
    status: TodoStatus  # Enforces literal type at type-check time
    created_at: datetime
```

**Benefits**:
- Type checkers (mypy, pyright) catch invalid status values at development time
- Still uses simple strings at runtime (no enum overhead)
- Easy migration to database Enum type in Phase II

---

## Validation Summary

| Field | Validation | Layer | Error Type |
|-------|------------|-------|------------|
| `title` | Non-empty after `.strip()` | Services | `ValueError("Title cannot be empty")` |
| `id` (on get/update/delete) | Exists in store | Services | `KeyError(f"Todo #{id} not found")` |
| `status` | One of "pending" or "completed" | Services | `ValueError("Invalid status")` |
| `created_at` | Auto-generated (no user input) | Store | N/A |
| `description` | None (accepts any string or None) | N/A | N/A |

---

## Notes

- This data model prioritizes simplicity (constitution principle I) over premature optimization
- Field types align with common database schemas (constitution principle V: extensibility)
- Validation rules are enforced in services layer, not in dataclass itself (separation of concerns)
- ID generation is deterministic and explicit (constitution principle IV: no hidden state)
