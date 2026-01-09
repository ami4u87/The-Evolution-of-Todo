# Enhanced Input Validation Specification - Phase III/IV

## Overview
This document defines enhanced validation rules for future phases of the Todo application. These features extend Phase II with advanced task management capabilities.

**Status**: Future Phase (Phase III/IV)
**Dependencies**: Phase II must be complete and stable

## Enhanced Features

### New Fields

| Field | Type | Required | Phase | Description |
|-------|------|----------|-------|-------------|
| `due_date` | ISO 8601 date | No | Phase III | Task deadline |
| `priority` | enum | No | Phase III | Task priority (high, medium, low) |
| `tags` | array[string] | No | Phase IV | Task categorization |

---

## Skill: ValidateTodoInput

**Persona**: You are a strict input validation expert for a multi-user Todo app. Never trust user input. Always return clear, user-friendly error messages.

**Principles**:
- Title is required, string, 1-200 characters
- Description is optional, string, max 1000 characters
- Due date must be valid ISO date in future (or today)
- Priority must be one of: high, medium, low
- Tags must be array of strings, max 10 tags, each max 50 characters
- Enforce user ownership – task must belong to authenticated user
- Return structured JSON errors if invalid

**Questions to always ask**:
- Does the input meet all schema rules?
- Are there any business logic violations?
- What specific error message should be shown to user?

**Output Format**:
- If valid: "VALID"
- If invalid: JSON array of errors like `[{"field": "title", "message": "Title is required"}]`

---

## Enhanced Validation Rules

### 1. Due Date Validation

**Field**: `due_date`
**Type**: ISO 8601 date string (e.g., "2025-12-31")
**Required**: No
**Constraints**:
- Must be valid ISO 8601 format (YYYY-MM-DD)
- Must be today or in the future
- Cannot be more than 5 years in the future

**Validation Logic**:
```python
from datetime import datetime, timedelta
from pydantic import field_validator

@field_validator('due_date')
@classmethod
def validate_due_date(cls, v: str | None) -> str | None:
    """Validate due date is in future and reasonable."""
    if v is None:
        return None

    try:
        # Parse ISO date
        due_date = datetime.fromisoformat(v).date()
    except ValueError:
        raise ValueError("Due date must be in ISO 8601 format (YYYY-MM-DD)")

    # Check not in past
    today = datetime.utcnow().date()
    if due_date < today:
        raise ValueError("Due date cannot be in the past")

    # Check not too far in future (5 years)
    max_future = today + timedelta(days=365 * 5)
    if due_date > max_future:
        raise ValueError("Due date cannot be more than 5 years in the future")

    return v
```

**Valid Examples**:
```json
{
  "title": "Submit report",
  "due_date": "2025-12-31"
}
```

**Invalid Examples**:
```json
{
  "title": "Old task",
  "due_date": "2020-01-01"
}
// Error: "Due date cannot be in the past"

{
  "title": "Far future",
  "due_date": "2050-01-01"
}
// Error: "Due date cannot be more than 5 years in the future"

{
  "title": "Bad format",
  "due_date": "12/31/2025"
}
// Error: "Due date must be in ISO 8601 format (YYYY-MM-DD)"
```

---

### 2. Priority Validation

**Field**: `priority`
**Type**: Enum string
**Required**: No
**Default**: "medium"
**Allowed Values**: "high", "medium", "low"

**Validation Logic**:
```python
from typing import Literal
from pydantic import Field

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: str | None = None
    priority: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Task priority"
    )

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Ensure priority is valid (redundant with Literal, but explicit)."""
        allowed = ["high", "medium", "low"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of: {', '.join(allowed)}")
        return v.lower()  # Normalize to lowercase
```

**Valid Examples**:
```json
{
  "title": "Urgent task",
  "priority": "high"
}

{
  "title": "Normal task"
  // priority defaults to "medium"
}
```

**Invalid Examples**:
```json
{
  "title": "Task",
  "priority": "urgent"
}
// Error: "Priority must be one of: high, medium, low"

{
  "title": "Task",
  "priority": "CRITICAL"
}
// Error: "Priority must be one of: high, medium, low"
```

---

### 3. Tags Validation

**Field**: `tags`
**Type**: Array of strings
**Required**: No
**Constraints**:
- Max 10 tags per task
- Each tag: 1-50 characters
- Tags must be unique (no duplicates)
- Alphanumeric and hyphens only (no special characters)
- Case-insensitive (normalize to lowercase)

**Validation Logic**:
```python
import re
from pydantic import field_validator

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tags array."""
        if not v:
            return []

        # Check max count
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        # Validate each tag
        validated_tags = []
        tag_pattern = re.compile(r'^[a-zA-Z0-9-]+$')

        for tag in v:
            # Trim whitespace
            tag = tag.strip()

            # Check empty
            if not tag:
                raise ValueError("Tags cannot be empty")

            # Check length
            if len(tag) < 1 or len(tag) > 50:
                raise ValueError("Each tag must be between 1 and 50 characters")

            # Check format (alphanumeric and hyphens only)
            if not tag_pattern.match(tag):
                raise ValueError(f"Tag '{tag}' contains invalid characters. Use only letters, numbers, and hyphens")

            # Normalize to lowercase
            tag = tag.lower()

            # Check for duplicates
            if tag in validated_tags:
                raise ValueError(f"Duplicate tag: '{tag}'")

            validated_tags.append(tag)

        return validated_tags
```

**Valid Examples**:
```json
{
  "title": "Project task",
  "tags": ["work", "urgent", "client-meeting"]
}

{
  "title": "Shopping",
  "tags": ["personal", "groceries"]
}

{
  "title": "No tags task",
  "tags": []
}
```

**Invalid Examples**:
```json
{
  "title": "Too many tags",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11"]
}
// Error: "Maximum 10 tags allowed per task"

{
  "title": "Invalid characters",
  "tags": ["work!", "urgent#tag", "hello@world"]
}
// Error: "Tag 'work!' contains invalid characters. Use only letters, numbers, and hyphens"

{
  "title": "Duplicate tags",
  "tags": ["work", "urgent", "work"]
}
// Error: "Duplicate tag: 'work'"

{
  "title": "Tag too long",
  "tags": ["this-is-a-very-long-tag-name-that-exceeds-the-fifty-character-limit-significantly"]
}
// Error: "Each tag must be between 1 and 50 characters"
```

---

## Combined Enhanced Schema

### TaskCreate (Phase III/IV)
```python
from typing import Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta
import re

class TaskCreate(BaseModel):
    """Enhanced task creation schema with future features."""

    # Phase II fields
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

    # Phase III fields
    due_date: str | None = Field(None, description="Task deadline (ISO 8601)")
    priority: Literal["high", "medium", "low"] = Field(default="medium")

    # Phase IV fields
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace only")
        return v

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: str | None) -> str | None:
        if v is None:
            return None
        try:
            due_date = datetime.fromisoformat(v).date()
        except ValueError:
            raise ValueError("Due date must be in ISO 8601 format (YYYY-MM-DD)")

        today = datetime.utcnow().date()
        if due_date < today:
            raise ValueError("Due date cannot be in the past")

        max_future = today + timedelta(days=365 * 5)
        if due_date > max_future:
            raise ValueError("Due date cannot be more than 5 years in the future")

        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        if not v:
            return []

        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        validated_tags = []
        tag_pattern = re.compile(r'^[a-zA-Z0-9-]+$')

        for tag in v:
            tag = tag.strip()
            if not tag:
                raise ValueError("Tags cannot be empty")
            if len(tag) < 1 or len(tag) > 50:
                raise ValueError("Each tag must be between 1 and 50 characters")
            if not tag_pattern.match(tag):
                raise ValueError(f"Tag '{tag}' contains invalid characters")
            tag = tag.lower()
            if tag in validated_tags:
                raise ValueError(f"Duplicate tag: '{tag}'")
            validated_tags.append(tag)

        return validated_tags
```

---

## Database Schema Changes (Phase III/IV)

### Tasks Table Updates
```sql
-- Phase III: Add due_date and priority
ALTER TABLE tasks
ADD COLUMN due_date DATE,
ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low'));

CREATE INDEX idx_tasks_due_date ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_priority ON tasks(user_id, priority);

-- Phase IV: Add tags (via junction table)
CREATE TABLE task_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(task_id, tag)
);

CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag ON task_tags(tag);
```

---

## Validation Test Suite

```python
import pytest
from datetime import datetime, timedelta

# Phase III: Due Date Tests
def test_valid_due_date():
    tomorrow = (datetime.utcnow() + timedelta(days=1)).date().isoformat()
    data = {"title": "Task", "due_date": tomorrow}
    result = TaskCreate(**data)
    assert result.due_date == tomorrow

def test_past_due_date():
    yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
    with pytest.raises(ValueError, match="cannot be in the past"):
        TaskCreate(title="Task", due_date=yesterday)

def test_invalid_due_date_format():
    with pytest.raises(ValueError, match="ISO 8601 format"):
        TaskCreate(title="Task", due_date="12/31/2025")

# Phase III: Priority Tests
def test_valid_priority():
    data = {"title": "Task", "priority": "high"}
    result = TaskCreate(**data)
    assert result.priority == "high"

def test_invalid_priority():
    with pytest.raises(ValueError, match="must be one of"):
        TaskCreate(title="Task", priority="urgent")

# Phase IV: Tags Tests
def test_valid_tags():
    data = {"title": "Task", "tags": ["work", "urgent"]}
    result = TaskCreate(**data)
    assert result.tags == ["work", "urgent"]

def test_too_many_tags():
    tags = [f"tag{i}" for i in range(11)]
    with pytest.raises(ValueError, match="Maximum 10 tags"):
        TaskCreate(title="Task", tags=tags)

def test_duplicate_tags():
    with pytest.raises(ValueError, match="Duplicate tag"):
        TaskCreate(title="Task", tags=["work", "work"])

def test_invalid_tag_characters():
    with pytest.raises(ValueError, match="invalid characters"):
        TaskCreate(title="Task", tags=["work!", "urgent#"])
```

---

## Migration Path from Phase II

1. **Phase II → Phase III**:
   - Add `due_date` and `priority` columns to tasks table
   - Update Pydantic schemas with new fields
   - Add validation logic
   - All existing tasks get `priority='medium'`, `due_date=NULL`

2. **Phase III → Phase IV**:
   - Create `task_tags` junction table
   - Update Pydantic schemas with tags field
   - Add tag validation logic
   - Implement tag CRUD operations

---

## API Impact

### New Query Parameters (Phase III/IV)

**Filter by priority**:
```
GET /api/tasks?priority=high
```

**Filter by due date**:
```
GET /api/tasks?due_before=2025-12-31
GET /api/tasks?overdue=true
```

**Filter by tags**:
```
GET /api/tasks?tags=work,urgent
```

**Sort options**:
```
GET /api/tasks?sort=due_date
GET /api/tasks?sort=priority
```

---

## Acceptance Criteria (Future Phases)

Phase III:
- [ ] Due date validated as ISO 8601
- [ ] Due date must be today or future
- [ ] Due date max 5 years in future
- [ ] Priority must be high/medium/low
- [ ] Priority defaults to medium
- [ ] Database columns added
- [ ] Indexes created

Phase IV:
- [ ] Tags validated as array of strings
- [ ] Max 10 tags per task
- [ ] Each tag 1-50 characters
- [ ] Tags alphanumeric and hyphens only
- [ ] No duplicate tags
- [ ] Tags normalized to lowercase
- [ ] Junction table created
- [ ] Tag CRUD operations work

---

## Notes

- This specification is for **future phases** only
- Do not implement these features in Phase II
- Phase II must be complete and stable first
- These features require database migrations
- Frontend UI must be updated to support new fields
- API documentation must be updated
- Backward compatibility must be maintained

---

## References

- ISO 8601 Date Format: https://www.iso.org/iso-8601-date-and-time-format.html
- Pydantic Validators: https://docs.pydantic.dev/latest/concepts/validators/
- Tag Best Practices: https://stackoverflow.com/questions/tagged/tags
