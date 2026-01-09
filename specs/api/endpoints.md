# API Endpoints Specification - Phase II

## Overview
This document defines all REST API endpoints for the Evolution of Todo application Phase II. All endpoints require JWT authentication and enforce user-based data isolation.

**Base URL**: `http://localhost:8000` (development)
**API Prefix**: `/api`
**Version**: 2.0.0

## Authentication

All endpoints (except health checks) require JWT authentication via Better Auth.

**Header Format**:
```
Authorization: Bearer <jwt_token>
```

**JWT Payload**:
```json
{
  "sub": "user_id_uuid",
  "email": "user@example.com",
  "iat": 1704672000,
  "exp": 1704758400
}
```

**Authentication Errors**:
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Valid token but insufficient permissions

---

## Health Check Endpoints

### GET /

**Description**: Root endpoint for API health check

**Authentication**: None required

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "message": "Todo API - Phase II",
  "version": "2.0.0"
}
```

**Example**:
```bash
curl http://localhost:8000/
```

---

### GET /health

**Description**: Detailed health check endpoint

**Authentication**: None required

**Response**: `200 OK`
```json
{
  "status": "healthy"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

## Task Management Endpoints

### 1. List All Tasks

**Endpoint**: `GET /api/tasks`

**Description**: Retrieve all tasks for the authenticated user

**Authentication**: Required (JWT Bearer token)

**Query Parameters**: None (pagination to be added in future phase)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response**: `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "created_at": "2025-01-08T10:00:00Z",
    "updated_at": "2025-01-08T10:00:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Write documentation",
    "description": null,
    "status": "completed",
    "created_at": "2025-01-07T15:30:00Z",
    "updated_at": "2025-01-08T09:00:00Z"
  }
]
```

**Response**: `200 OK` (empty list)
```json
[]
```

**Error Responses**:
- `401 Unauthorized` - Missing or invalid JWT token
```json
{
  "detail": "Invalid or expired token"
}
```

**Example**:
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Notes**:
- Only returns tasks owned by authenticated user
- Returns empty array if user has no tasks
- Tasks returned in creation order (oldest first)
- No pagination in Phase II (add in Phase III for large datasets)

---

### 2. Get Single Task

**Endpoint**: `GET /api/tasks/{task_id}`

**Description**: Retrieve a specific task by ID (if owned by user)

**Authentication**: Required (JWT Bearer token)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | Unique task identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2025-01-08T10:00:00Z",
  "updated_at": "2025-01-08T10:00:00Z"
}
```

**Error Responses**:

`401 Unauthorized` - Missing or invalid token
```json
{
  "detail": "Invalid or expired token"
}
```

`404 Not Found` - Task doesn't exist or not owned by user
```json
{
  "detail": "Task not found"
}
```

**Example**:
```bash
curl -X GET http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Notes**:
- Returns 404 if task doesn't exist OR if task belongs to different user
- This prevents information leakage about task existence

---

### 3. Create Task

**Endpoint**: `POST /api/tasks`

**Description**: Create a new task for the authenticated user

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Request Body Schema** (`TaskCreate`):
| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| `title` | string | Yes | 1-255 chars, non-empty after trim | - |
| `description` | string | No | Max 1000 chars | null |

**Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2025-01-08T10:00:00Z",
  "updated_at": "2025-01-08T10:00:00Z"
}
```

**Error Responses**:

`401 Unauthorized` - Missing or invalid token
```json
{
  "detail": "Invalid or expired token"
}
```

`422 Unprocessable Entity` - Validation error
```json
{
  "detail": [
    {
      "field": "title",
      "message": "Title is required"
    }
  ]
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Notes**:
- `user_id` is extracted from JWT token (not from request body)
- `status` defaults to "pending"
- `id`, `created_at`, `updated_at` are auto-generated
- Title is trimmed of whitespace before storage

**Validation Examples**:

❌ Empty title:
```json
{
  "title": "",
  "description": "Test"
}
// Error: "Title cannot be empty or whitespace only"
```

❌ Whitespace-only title:
```json
{
  "title": "   ",
  "description": "Test"
}
// Error: "Title cannot be empty or whitespace only"
```

❌ Title too long:
```json
{
  "title": "x".repeat(256),
  "description": "Test"
}
// Error: "Title must be between 1 and 255 characters"
```

❌ Description too long:
```json
{
  "title": "Valid title",
  "description": "x".repeat(1001)
}
// Error: "Description must be less than 1000 characters"
```

✅ Valid minimal:
```json
{
  "title": "Task"
}
```

✅ Valid complete:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

---

### 4. Update Task

**Endpoint**: `PUT /api/tasks/{task_id}`

**Description**: Update an existing task (if owned by user)

**Authentication**: Required (JWT Bearer token)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | Unique task identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips",
  "status": "pending"
}
```

**Request Body Schema** (`TaskUpdate`):
| Field | Type | Required | Constraints | Default |
|-------|------|----------|-------------|---------|
| `title` | string | No | If provided: 1-255 chars, non-empty | unchanged |
| `description` | string | No | If provided: Max 1000 chars | unchanged |
| `status` | string | No | If provided: "pending" or "completed" | unchanged |

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips",
  "status": "pending",
  "created_at": "2025-01-08T10:00:00Z",
  "updated_at": "2025-01-08T11:30:00Z"
}
```

**Error Responses**:

`401 Unauthorized` - Missing or invalid token
```json
{
  "detail": "Invalid or expired token"
}
```

`404 Not Found` - Task doesn't exist or not owned by user
```json
{
  "detail": "Task not found"
}
```

`422 Unprocessable Entity` - Validation error
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

**Example**:
```bash
curl -X PUT http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and snacks",
    "description": "Milk, eggs, bread, chips"
  }'
```

**Notes**:
- All fields are optional (partial update)
- Only provided fields are updated
- `updated_at` is automatically refreshed
- Returns 404 if task doesn't exist or belongs to different user
- Cannot change `user_id`, `id`, or `created_at`

**Update Examples**:

✅ Update only title:
```json
{
  "title": "New title"
}
```

✅ Update only status:
```json
{
  "status": "completed"
}
```

✅ Update all fields:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "completed"
}
```

❌ Empty title:
```json
{
  "title": "   "
}
// Error: "Title cannot be empty or whitespace only"
```

❌ Invalid status:
```json
{
  "status": "in-progress"
}
// Error: "Status must be 'pending' or 'completed'"
```

---

### 5. Delete Task

**Endpoint**: `DELETE /api/tasks/{task_id}`

**Description**: Permanently delete a task (if owned by user)

**Authentication**: Required (JWT Bearer token)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | Unique task identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response**: `204 No Content`

No response body.

**Error Responses**:

`401 Unauthorized` - Missing or invalid token
```json
{
  "detail": "Invalid or expired token"
}
```

`404 Not Found` - Task doesn't exist or not owned by user
```json
{
  "detail": "Task not found"
}
```

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Notes**:
- Deletion is permanent (no soft delete in Phase II)
- Returns 204 with no body on success
- Returns 404 if task doesn't exist or belongs to different user
- Idempotent: deleting already-deleted task returns 404

---

### 6. Mark Task as Complete

**Endpoint**: `PATCH /api/tasks/{task_id}/complete`

**Description**: Mark a task as completed (if owned by user)

**Authentication**: Required (JWT Bearer token)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | UUID | Yes | Unique task identifier |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**: None

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "completed",
  "created_at": "2025-01-08T10:00:00Z",
  "updated_at": "2025-01-08T12:00:00Z"
}
```

**Error Responses**:

`401 Unauthorized` - Missing or invalid token
```json
{
  "detail": "Invalid or expired token"
}
```

`404 Not Found` - Task doesn't exist or not owned by user
```json
{
  "detail": "Task not found"
}
```

**Example**:
```bash
curl -X PATCH http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000/complete \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Notes**:
- Shortcut for updating status to "completed"
- Idempotent: marking already-completed task is allowed
- Updates `updated_at` timestamp
- Returns 404 if task doesn't exist or belongs to different user
- Alternative: use `PUT /api/tasks/{task_id}` with `{"status": "completed"}`

---

## Error Response Format

All error responses follow a consistent format:

### Single Error
```json
{
  "detail": "Error message here"
}
```

### Multiple Validation Errors
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

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200 OK` | Success | GET, PUT, PATCH operations successful |
| `201 Created` | Resource created | POST operation created new task |
| `204 No Content` | Success, no body | DELETE operation successful |
| `400 Bad Request` | Generic client error | Malformed request |
| `401 Unauthorized` | Authentication failed | Missing or invalid JWT token |
| `403 Forbidden` | Authorization failed | Valid token but insufficient permissions |
| `404 Not Found` | Resource not found | Task doesn't exist or not owned by user |
| `422 Unprocessable Entity` | Validation error | Request body validation failed |
| `500 Internal Server Error` | Server error | Unexpected error (logged for debugging) |

---

## Authentication Flow

### 1. User Login (via Better Auth on Frontend)
```
User → Frontend → Better Auth → JWT Token
```

### 2. API Request with JWT
```
Frontend → Backend API (with JWT in header)
```

### 3. Backend Token Verification
```python
# Extract token from header
token = request.headers.get("Authorization", "").replace("Bearer ", "")

# Verify token signature
payload = jwt.decode(token, secret, algorithms=["HS256"])

# Extract user_id
user_id = payload.get("sub")

# Use user_id to filter database queries
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()
```

---

## Data Isolation

**CRITICAL**: All task endpoints MUST filter by authenticated `user_id`.

**Correct Query**:
```python
# ✓ User can only access their own tasks
task = session.exec(
    select(Task).where(Task.id == task_id, Task.user_id == user_id)
).first()
```

**Incorrect Query (Security Vulnerability)**:
```python
# ✗ User could access any task by guessing IDs
task = session.exec(
    select(Task).where(Task.id == task_id)
).first()
```

**Result**:
- User A cannot access User B's tasks
- Attempting to access another user's task returns 404 (not 403, to prevent information leakage)
- All list operations automatically filtered by user_id

---

## API Testing

### Using cURL

**Set token variable**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**List tasks**:
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

**Create task**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Testing API"}'
```

**Update task**:
```bash
TASK_ID="550e8400-e29b-41d4-a716-446655440000"
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title"}'
```

**Mark complete**:
```bash
curl -X PATCH http://localhost:8000/api/tasks/$TASK_ID/complete \
  -H "Authorization: Bearer $TOKEN"
```

**Delete task**:
```bash
curl -X DELETE http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Using HTTPie

**List tasks**:
```bash
http GET localhost:8000/api/tasks "Authorization: Bearer $TOKEN"
```

**Create task**:
```bash
http POST localhost:8000/api/tasks \
  "Authorization: Bearer $TOKEN" \
  title="Test task" description="Testing API"
```

### Using Postman

1. Set `Authorization` header: `Bearer <token>`
2. Set `Content-Type` header: `application/json`
3. Import collection from OpenAPI spec (see `/docs` endpoint)

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

**Swagger UI**: http://localhost:8000/docs
- Interactive API explorer
- Try endpoints directly in browser
- See request/response schemas

**ReDoc**: http://localhost:8000/redoc
- Clean, readable documentation
- Better for sharing with stakeholders

**OpenAPI JSON**: http://localhost:8000/openapi.json
- Machine-readable API specification
- Import into Postman, Insomnia, etc.

---

## Rate Limiting (Future Phase)

Phase II has no rate limiting. Consider adding in Phase III:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704672000
```

---

## Pagination (Future Phase)

Phase II returns all tasks (no pagination). For Phase III with large datasets:

```
GET /api/tasks?page=1&per_page=20

Response headers:
X-Total-Count: 150
X-Page: 1
X-Per-Page: 20
X-Total-Pages: 8
```

---

## CORS Configuration

Frontend (localhost:3000) can access backend (localhost:8000):

**Allowed Origins**: `http://localhost:3000`
**Allowed Methods**: `GET, POST, PUT, PATCH, DELETE, OPTIONS`
**Allowed Headers**: `Authorization, Content-Type`
**Expose Headers**: `Content-Length`
**Credentials**: `true`

---

## Acceptance Criteria

- [ ] All endpoints implement JWT authentication
- [ ] All endpoints enforce user-based data isolation
- [ ] List tasks returns only user's tasks
- [ ] Get task returns 404 if not owned by user
- [ ] Create task assigns authenticated user_id
- [ ] Update task validates ownership
- [ ] Delete task validates ownership
- [ ] Mark complete validates ownership
- [ ] All validation errors return 422 with structured JSON
- [ ] All auth errors return 401/403 appropriately
- [ ] Not found errors return 404
- [ ] Success responses match schema
- [ ] Interactive docs available at /docs
- [ ] CORS configured for frontend origin
- [ ] All endpoints tested with valid/invalid inputs

---

## Future Enhancements

See `specs/future-phases/` for:
- Filtering by status, priority
- Sorting by due date, priority, created_at
- Pagination for large datasets
- Bulk operations (mark multiple complete, delete multiple)
- Search by title/description
- Tag filtering

---

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- REST API Best Practices: https://restfulapi.net/
- HTTP Status Codes: https://httpstatuses.com/
- OpenAPI Specification: https://swagger.io/specification/
