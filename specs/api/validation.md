# API Input Validation Specification - Phase II

## Overview
This document defines input validation rules for the Todo API. All user input must be validated before processing to ensure data integrity, security, and user experience.

**Principle**: Never trust user input. Always validate, sanitize, and return clear error messages.

## Validation Layers

1. **Pydantic Schema Validation** - Type checking and basic constraints
2. **Service Layer Validation** - Business logic rules
3. **Database Constraints** - Final safety net

## Phase II Fields

### Task Creation (`POST /api/tasks`)

**Input Schema**: `TaskCreate`

| Field | Type | Required | Constraints | Error Messages |
|-------|------|----------|-------------|----------------|
| `title` | string | Yes | 1-255 characters, non-empty after trim | "Title is required"<br>"Title must be between 1 and 255 characters" |
| `description` | string | No | Max 1000 characters | "Description must be less than 1000 characters" |

**Validation Rules**:

1. **Title Validation**:
   ```python
   # Must be present
   if not title:
       raise ValueError("Title is required")

   # Trim whitespace
   title = title.strip()

   # Check non-empty after trim
   if not title:
       raise ValueError("Title cannot be empty or whitespace only")

   # Check length
   if len(title) < 1 or len(title) > 255:
       raise ValueError("Title must be between 1 and 255 characters")
   ```

2. **Description Validation**:
   ```python
   # Optional field
   if description is not None:
       # Check max length
       if len(description) > 1000:
           raise ValueError("Description must be less than 1000 characters")
   ```

**Example Valid Input**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Example Invalid Input**:
```json
{
  "title": "",
  "description": null
}
```
**Response**:
```json
{
  "detail": [
    {
      "field": "title",
      "message": "Title cannot be empty or whitespace only"
    }
  ]
}
```

---

### Task Update (`PUT /api/tasks/{task_id}`)

**Input Schema**: `TaskUpdate`

| Field | Type | Required | Constraints | Error Messages |
|-------|------|----------|-------------|----------------|
| `title` | string | No | If provided: 1-255 characters, non-empty after trim | "Title must be between 1 and 255 characters"<br>"Title cannot be empty" |
| `description` | string | No | If provided: Max 1000 characters | "Description must be less than 1000 characters" |
| `status` | string | No | If provided: Must be 'pending' or 'completed' | "Status must be 'pending' or 'completed'" |

**Validation Rules**:

1. **Title Validation** (if provided):
   ```python
   if title is not None:
       title = title.strip()
       if not title:
           raise ValueError("Title cannot be empty or whitespace only")
       if len(title) < 1 or len(title) > 255:
           raise ValueError("Title must be between 1 and 255 characters")
   ```

2. **Description Validation** (if provided):
   ```python
   if description is not None:
       if len(description) > 1000:
           raise ValueError("Description must be less than 1000 characters")
   ```

3. **Status Validation** (if provided):
   ```python
   if status is not None:
       if status not in ["pending", "completed"]:
           raise ValueError("Status must be 'pending' or 'completed'")
   ```

**Example Valid Input**:
```json
{
  "title": "Buy groceries and snacks"
}
```

**Example Invalid Input**:
```json
{
  "title": "   ",
  "status": "in-progress"
}
```
**Response**:
```json
{
  "detail": [
    {
      "field": "title",
      "message": "Title cannot be empty or whitespace only"
    },
    {
      "field": "status",
      "message": "Status must be 'pending' or 'completed'"
    }
  ]
}
```

---

### Mark Task Complete (`PATCH /api/tasks/{task_id}/complete`)

**No Input Required** - This endpoint takes no request body.

**Validation**:
- Task must exist
- Task must belong to authenticated user
- No additional validation needed (idempotent operation)

---

## Authorization Validation

**All endpoints require**:

1. **JWT Token Validation**:
   ```python
   # Extract token from Authorization header
   token = request.headers.get("Authorization", "").replace("Bearer ", "")

   if not token:
       raise HTTPException(
           status_code=401,
           detail="Missing authentication token"
       )

   # Verify token signature
   try:
       payload = jwt.decode(token, secret, algorithms=["HS256"])
       user_id = payload.get("sub")
   except JWTError:
       raise HTTPException(
           status_code=401,
           detail="Invalid or expired token"
       )
   ```

2. **Task Ownership Validation**:
   ```python
   # For GET/PUT/DELETE/PATCH on specific task
   task = get_task(task_id)

   if not task:
       raise HTTPException(
           status_code=404,
           detail="Task not found"
       )

   if task.user_id != user_id:
       raise HTTPException(
           status_code=403,
           detail="You do not have permission to access this task"
       )
   ```

---

## Error Response Format

All validation errors return HTTP 422 with structured JSON:

```json
{
  "detail": [
    {
      "field": "title",
      "message": "Title is required"
    },
    {
      "field": "description",
      "message": "Description must be less than 1000 characters"
    }
  ]
}
```

**HTTP Status Codes**:
- `400 Bad Request` - General client error
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Valid token but insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation error

---

## Pydantic Schema Implementation

### TaskCreate Schema
```python
from pydantic import BaseModel, Field, field_validator

class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Task title"
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Optional task description"
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not empty after stripping whitespace."""
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace only")
        return v

    @field_validator('description')
    @classmethod
    def description_length(cls, v: str | None) -> str | None:
        """Validate description length."""
        if v is not None and len(v) > 1000:
            raise ValueError("Description must be less than 1000 characters")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }
```

### TaskUpdate Schema
```python
class TaskUpdate(BaseModel):
    title: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="New task title"
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="New task description"
    )
    status: Literal["pending", "completed"] | None = Field(
        None,
        description="New task status"
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        """Ensure title is not empty if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v

    @field_validator('description')
    @classmethod
    def description_length(cls, v: str | None) -> str | None:
        """Validate description length if provided."""
        if v is not None and len(v) > 1000:
            raise ValueError("Description must be less than 1000 characters")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and snacks",
                "status": "completed"
            }
        }
```

---

## Common Validation Patterns

### 1. Whitespace Handling
```python
# Always trim whitespace from strings
value = value.strip() if value else value

# Reject whitespace-only values for required fields
if not value or not value.strip():
    raise ValueError("Field cannot be empty or whitespace only")
```

### 2. Length Validation
```python
# Check length after trimming
if len(value.strip()) < min_length or len(value.strip()) > max_length:
    raise ValueError(f"Field must be between {min_length} and {max_length} characters")
```

### 3. Enum Validation
```python
# Use Literal type for type safety
from typing import Literal

status: Literal["pending", "completed"]

# Or validate manually
if value not in ["pending", "completed"]:
    raise ValueError("Status must be 'pending' or 'completed'")
```

---

## Security Considerations

1. **SQL Injection Prevention**:
   - SQLModel uses parameterized queries (safe by default)
   - Never concatenate user input into SQL strings

2. **XSS Prevention**:
   - Input validation doesn't allow HTML tags
   - Frontend must escape output when rendering

3. **Data Sanitization**:
   - Trim whitespace from string inputs
   - Normalize email addresses (lowercase)
   - Validate data types strictly

4. **Rate Limiting** (Future):
   - Limit validation attempts per IP
   - Prevent brute force attacks

---

## Testing Validation

### Valid Cases
```python
def test_valid_task_creation():
    data = {"title": "Buy groceries", "description": "Milk, eggs"}
    result = TaskCreate(**data)
    assert result.title == "Buy groceries"

def test_valid_task_update():
    data = {"title": "Updated title"}
    result = TaskUpdate(**data)
    assert result.title == "Updated title"
```

### Invalid Cases
```python
def test_empty_title():
    with pytest.raises(ValueError, match="Title cannot be empty"):
        TaskCreate(title="   ", description="Test")

def test_title_too_long():
    with pytest.raises(ValueError, match="must be between 1 and 255"):
        TaskCreate(title="x" * 256, description="Test")

def test_description_too_long():
    with pytest.raises(ValueError, match="must be less than 1000"):
        TaskCreate(title="Test", description="x" * 1001)

def test_invalid_status():
    with pytest.raises(ValueError, match="must be 'pending' or 'completed'"):
        TaskUpdate(status="in-progress")
```

---

## Acceptance Criteria

- [ ] Title required on creation
- [ ] Title length between 1-255 characters
- [ ] Whitespace-only titles rejected
- [ ] Description optional
- [ ] Description max 1000 characters
- [ ] Status must be 'pending' or 'completed'
- [ ] All update fields optional
- [ ] Clear error messages for each validation failure
- [ ] JWT token required for all endpoints
- [ ] Task ownership verified before updates/deletes
- [ ] Pydantic validators implemented
- [ ] Service layer validation enforced
- [ ] HTTP status codes correct (400/401/403/404/422)

---

## Future Enhancements (Phase III/IV)

See `specs/api/validation-enhanced.md` for:
- Due date validation
- Priority validation (high/medium/low)
- Tags validation (array of strings)
- Advanced business rules

---

## References

- Pydantic Documentation: https://docs.pydantic.dev/
- FastAPI Validation: https://fastapi.tiangolo.com/tutorial/body-fields/
- OWASP Input Validation: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
